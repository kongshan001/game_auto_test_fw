# -*- coding: utf-8 -*-
"""
GLM-4.6V 视觉理解模块

基于智谱 GLM-4.6V 多模态模型，支持图像/视频/文件理解
文档: https://docs.bigmodel.cn/cn/guide/models/vlm/glm-4.6v
"""

import base64
import json
import re
from pathlib import Path
from typing import Dict, Any, Optional, List, Union

# 尝试导入新版 SDK
try:
    from zai import ZhipuAiClient
    HAS_ZAI_SDK = True
except ImportError:
    HAS_ZAI_SDK = False
    import requests

import sys
sys.path.append(str(Path(__file__).parent.parent))
import config


class GLMVision:
    """
    GLM-4.6V 视觉理解
    
    支持的功能:
    - 图像理解 (URL 或 base64)
    - 视频理解
    - 文件理解
    - 深度思考模式 (thinking)
    - 流式输出
    """
    
    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or config.GLM_API_KEY
        self.model = model or config.GLM_MODEL
        self.api_url = config.GLM_API_URL
        self._client = None
    
    @property
    def client(self):
        """延迟初始化 SDK client"""
        if self._client is None and HAS_ZAI_SDK:
            self._client = ZhipuAiClient(api_key=self.api_key)
        return self._client
    
    def _encode_image(self, image_path: str) -> str:
        """
        图片转 base64
        
        GLM-4.6V 支持直接传入 base64 字符串，无需 data URI 前缀
        """
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    
    def _build_content(
        self,
        text: str,
        image_urls: Optional[List[str]] = None,
        video_urls: Optional[List[str]] = None,
        file_urls: Optional[List[str]] = None,
        local_image: Optional[str] = None
    ) -> List[Dict]:
        """
        构建多模态消息内容
        
        Args:
            text: 文本提示
            image_urls: 图片 URL 列表
            video_urls: 视频 URL 列表
            file_urls: 文件 URL 列表
            local_image: 本地图片路径
        
        Returns:
            content 列表
        """
        content = []
        
        # 添加图片
        if image_urls:
            for url in image_urls:
                content.append({
                    "type": "image_url",
                    "image_url": {"url": url}
                })
        
        # 添加本地图片 (base64)
        if local_image:
            img_base64 = self._encode_image(local_image)
            content.append({
                "type": "image_url",
                "image_url": {"url": img_base64}
            })
        
        # 添加视频
        if video_urls:
            for url in video_urls:
                content.append({
                    "type": "video_url",
                    "video_url": {"url": url}
                })
        
        # 添加文件
        if file_urls:
            for url in file_urls:
                content.append({
                    "type": "file_url",
                    "file_url": {"url": url}
                })
        
        # 添加文本 (放在最后，符合 GLM 建议)
        content.append({
            "type": "text",
            "text": text
        })
        
        return content
    
    def analyze(
        self,
        prompt: str,
        image_path: Optional[str] = None,
        image_urls: Optional[List[str]] = None,
        video_urls: Optional[List[str]] = None,
        file_urls: Optional[List[str]] = None,
        thinking: bool = True,
        stream: bool = False
    ) -> Dict[str, Any]:
        """
        多模态分析
        
        Args:
            prompt: 文本提示
            image_path: 本地图片路径
            image_urls: 图片 URL 列表
            video_urls: 视频 URL 列表
            file_urls: 文件 URL 列表
            thinking: 是否开启深度思考
            stream: 是否流式输出
        
        Returns:
            {"success": bool, "content": str, "reasoning": str, "error": str}
        """
        try:
            content = self._build_content(
                text=prompt,
                image_urls=image_urls,
                video_urls=video_urls,
                file_urls=file_urls,
                local_image=image_path
            )
            
            if HAS_ZAI_SDK and self.client:
                return self._analyze_with_sdk(content, thinking, stream)
            else:
                return self._analyze_with_http(content, thinking, stream)
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _analyze_with_sdk(
        self,
        content: List[Dict],
        thinking: bool,
        stream: bool
    ) -> Dict[str, Any]:
        """使用 zai-sdk 调用"""
        kwargs = {
            "model": self.model,
            "messages": [{"role": "user", "content": content}]
        }
        
        if thinking:
            kwargs["thinking"] = {"type": "enabled"}
        
        if stream:
            kwargs["stream"] = True
            return self._handle_stream_response(self.client.chat.completions.create(**kwargs))
        else:
            response = self.client.chat.completions.create(**kwargs)
            result = {"success": True, "content": ""}
            
            if hasattr(response, 'choices') and response.choices:
                msg = response.choices[0].message
                if hasattr(msg, 'content'):
                    result["content"] = msg.content
                if hasattr(msg, 'reasoning_content'):
                    result["reasoning"] = msg.reasoning_content
            
            return result
    
    def _analyze_with_http(
        self,
        content: List[Dict],
        thinking: bool,
        stream: bool
    ) -> Dict[str, Any]:
        """使用原生 HTTP 调用 (fallback)"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": content}]
        }
        
        if thinking:
            payload["thinking"] = {"type": "enabled"}
        
        if stream:
            payload["stream"] = True
        
        response = requests.post(
            self.api_url,
            headers=headers,
            json=payload,
            timeout=60,
            stream=stream
        )
        
        if response.status_code != 200:
            return {
                "success": False,
                "error": f"HTTP {response.status_code}",
                "detail": response.text
            }
        
        if stream:
            return self._handle_http_stream(response)
        else:
            result = response.json()
            content_text = ""
            reasoning_text = ""
            
            if "choices" in result and result["choices"]:
                msg = result["choices"][0].get("message", {})
                content_text = msg.get("content", "")
                reasoning_text = msg.get("reasoning_content", "")
            
            return {
                "success": True,
                "content": content_text,
                "reasoning": reasoning_text
            }
    
    def _handle_stream_response(self, response) -> Dict[str, Any]:
        """处理 SDK 流式响应"""
        content_parts = []
        reasoning_parts = []
        
        for chunk in response:
            if chunk.choices and chunk.choices[0].delta:
                delta = chunk.choices[0].delta
                if hasattr(delta, 'reasoning_content') and delta.reasoning_content:
                    reasoning_parts.append(delta.reasoning_content)
                if hasattr(delta, 'content') and delta.content:
                    content_parts.append(delta.content)
        
        return {
            "success": True,
            "content": "".join(content_parts),
            "reasoning": "".join(reasoning_parts)
        }
    
    def _handle_http_stream(self, response) -> Dict[str, Any]:
        """处理 HTTP 流式响应"""
        content_parts = []
        reasoning_parts = []
        
        for line in response.iter_lines():
            if line:
                line = line.decode('utf-8')
                if line.startswith('data: '):
                    data = line[6:]
                    if data == '[DONE]':
                        break
                    try:
                        chunk = json.loads(data)
                        if 'choices' in chunk and chunk['choices']:
                            delta = chunk['choices'][0].get('delta', {})
                            if 'reasoning_content' in delta:
                                reasoning_parts.append(delta['reasoning_content'])
                            if 'content' in delta:
                                content_parts.append(delta['content'])
                    except json.JSONDecodeError:
                        continue
        
        return {
            "success": True,
            "content": "".join(content_parts),
            "reasoning": "".join(reasoning_parts)
        }
    
    def _extract_json(self, text: str) -> Optional[Dict]:
        """从文本中提取 JSON"""
        # 尝试直接解析
        try:
            return json.loads(text.strip())
        except json.JSONDecodeError:
            pass
        
        # 尝试从代码块中提取
        if "```" in text:
            match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', text)
            if match:
                try:
                    return json.loads(match.group(1))
                except json.JSONDecodeError:
                    pass
        
        # 尝试找 JSON 对象
        match = re.search(r'\{[\s\S]*\}', text)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                pass
        
        return None
    
    def find_element(self, image_path: str, element_name: str) -> Dict[str, Any]:
        """
        查找界面元素位置
        
        Args:
            image_path: 截图路径
            element_name: 元素描述
        
        Returns:
            {"found": bool, "x": int, "y": int, "width": int, "height": int}
        """
        prompt = f"""找到界面中「{element_name}」的位置。

返回 JSON 格式:
{{"found": true, "x": 100, "y": 200, "width": 50, "height": 30}}

如果找不到，返回:
{{"found": false}}

坐标使用相对于图片左上角的像素位置。"""
        
        result = self.analyze(image_path=image_path, prompt=prompt, thinking=True)
        
        if result["success"]:
            extracted = self._extract_json(result["content"])
            if extracted:
                return extracted
        
        return {"found": False}
    
    def verify_state(self, image_path: str, expected: str) -> Dict[str, Any]:
        """
        验证界面状态
        
        Args:
            image_path: 截图路径
            expected: 期望状态的描述
        
        Returns:
            {"matched": bool, "confidence": float, "detail": str}
        """
        prompt = f"""验证当前界面是否符合期望状态。

期望状态: {expected}

返回 JSON 格式:
{{"matched": true, "confidence": 0.95, "detail": "简要说明"}}

如果不符合:
{{"matched": false, "confidence": 0.2, "detail": "说明不符合的原因"}}"""
        
        result = self.analyze(image_path=image_path, prompt=prompt, thinking=True)
        
        if result["success"]:
            extracted = self._extract_json(result["content"])
            if extracted:
                return extracted
        
        return {"matched": False, "confidence": 0, "detail": "解析失败"}
    
    def decide_action(
        self,
        image_path: str,
        goal: str,
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        智能决策下一步操作
        
        Args:
            image_path: 截图路径
            goal: 当前目标
            context: 上下文信息（可选）
        
        Returns:
            {
                "action": "click|input|wait|swipe|done|fail",
                "target": "操作目标描述",
                "x": 100, "y": 200,
                "text": "输入内容（input时）",
                "next_goal": "下一步目标",
                "screenshot": "截图路径"
            }
        """
        context_str = f"\n上下文: {context}" if context else ""
        
        prompt = f"""你是一个游戏自动化测试的智能决策系统。

当前目标: {goal}{context_str}

分析当前界面，决定下一步操作。

返回 JSON 格式:
{{
    "action": "click",
    "target": "登录按钮",
    "x": 100,
    "y": 200,
    "next_goal": "等待进入游戏"
}}

支持的 action 类型:
- click: 点击指定位置 (需要 x, y)
- input: 输入文本 (需要 text)
- swipe: 滑动 (需要 direction: up/down/left/right)
- wait: 等待 (需要 seconds)
- done: 目标已完成
- fail: 无法完成，需要人工介入

请仔细分析界面，做出最合理的决策。"""
        
        result = self.analyze(image_path=image_path, prompt=prompt, thinking=True)
        
        if result["success"]:
            extracted = self._extract_json(result["content"])
            if extracted:
                extracted["screenshot"] = image_path
                return extracted
        
        return {"action": "wait", "seconds": 2, "screenshot": image_path}
    
    def describe_screen(self, image_path: str) -> str:
        """
        描述当前界面内容
        
        Args:
            image_path: 截图路径
        
        Returns:
            界面描述文本
        """
        prompt = """请详细描述当前界面的内容，包括:
1. 界面类型（登录、主菜单、游戏内等）
2. 可见的主要元素（按钮、文字、图标等）
3. 当前状态（加载中、等待输入、显示结果等）
4. 任何值得注意的信息"""

        result = self.analyze(image_path=image_path, prompt=prompt, thinking=False)
        
        if result["success"]:
            return result["content"]
        return f"分析失败: {result.get('error', '未知错误')}"


if __name__ == "__main__":
    print("GLM-4.6V 视觉理解模块")
    print(f"SDK 可用: {HAS_ZAI_SDK}")
    print(f"Model: {config.GLM_MODEL}")
    print(f"API URL: {config.GLM_API_URL}")
