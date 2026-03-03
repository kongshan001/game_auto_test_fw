# -*- coding: utf-8 -*-
"""
GLM-4V 视觉理解模块（简化版）
"""

import base64
import requests
import json
from typing import Dict, Any
from pathlib import Path

import sys
sys.path.append(str(Path(__file__).parent.parent))
import config


class GLMVision:
    """GLM-4V 视觉理解"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or config.GLM_API_KEY
        self.api_url = config.GLM_API_URL
        self.model = config.GLM_MODEL
    
    def _encode_image(self, image_path: str) -> str:
        """图片转 base64"""
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    
    def analyze(self, image_path: str, prompt: str) -> Dict[str, Any]:
        """
        分析图片
        
        Args:
            image_path: 图片路径
            prompt: 提示词
            
        Returns:
            {"success": bool, "content": str, "error": str}
        """
        try:
            image_base64 = self._encode_image(image_path)
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.model,
                "messages": [{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_base64}"}}
                    ]
                }],
                "max_tokens": 1024,
                "temperature": 0.1
            }
            
            response = requests.post(self.api_url, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                return {"success": True, "content": content}
            else:
                return {"success": False, "error": f"HTTP {response.status_code}", "detail": response.text}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def find_element(self, image_path: str, element_name: str) -> Dict[str, Any]:
        """查找元素位置"""
        prompt = f"""找到"{element_name}"的位置。返回JSON:
{{"found":true,"x":100,"y":200,"width":50,"height":30}}
或 {{"found":false}}"""
        
        result = self.analyze(image_path, prompt)
        if result["success"]:
            try:
                content = result["content"]
                if "```" in content:
                    content = content.split("```")[1].split("```")[0]
                return json.loads(content.strip())
            except:
                return {"found": False}
        return {"found": False}
    
    def verify_state(self, image_path: str, expected: str) -> Dict[str, Any]:
        """验证界面状态"""
        prompt = f"""验证界面是否显示：{expected}。返回JSON:
{{"matched":true,"confidence":0.9}} 或 {{"matched":false}}"""
        
        result = self.analyze(image_path, prompt)
        if result["success"]:
            try:
                content = result["content"]
                if "```" in content:
                    content = content.split("```")[1].split("```")[0]
                return json.loads(content.strip())
            except:
                return {"matched": False}
        return {"matched": False}
    
    def decide_action(self, image_path: str, goal: str) -> Dict[str, Any]:
        """决策下一步操作"""
        prompt = f"""目标：{goal}
分析界面，决定下一步。返回JSON:
{{"action":"click","target":"登录按钮","x":100,"y":200,"next_goal":"下一步"}}
支持的action: click, input, wait, done"""
        
        result = self.analyze(image_path, prompt)
        if result["success"]:
            try:
                content = result["content"]
                if "```" in content:
                    content = content.split("```")[1].split("```")[0]
                decision = json.loads(content.strip())
                decision["screenshot"] = image_path
                return decision
            except:
                return {"action": "wait", "seconds": 2}
        return {"action": "wait", "seconds": 2}


if __name__ == "__main__":
    print("GLM Vision 模块")
    print(f"Model: {config.GLM_MODEL}")
