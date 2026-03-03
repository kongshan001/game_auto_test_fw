# -*- coding: utf-8 -*-
"""
GLM Vision 模块单元测试
"""

import os
import sys
import json
import base64
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.glm_vision import GLMVision
import config


class TestGLMVisionInit:
    """GLMVision 初始化测试"""
    
    def test_init_with_config(self):
        """测试使用配置初始化"""
        vision = GLMVision()
        assert vision.api_key == config.GLM_API_KEY
        assert vision.model == config.GLM_MODEL
    
    def test_init_with_custom_params(self):
        """测试自定义参数初始化"""
        vision = GLMVision(api_key="test_key", model="custom_model")
        assert vision.api_key == "test_key"
        assert vision.model == "custom_model"


class TestBuildContent:
    """消息内容构建测试"""
    
    def test_build_text_only(self):
        """测试纯文本内容"""
        vision = GLMVision()
        content = vision._build_content(text="Hello")
        
        assert len(content) == 1
        assert content[0]["type"] == "text"
        assert content[0]["text"] == "Hello"
    
    def test_build_with_image_url(self):
        """测试图片 URL 内容"""
        vision = GLMVision()
        content = vision._build_content(
            text="Describe this",
            image_urls=["https://example.com/image.png"]
        )
        
        assert len(content) == 2
        assert content[0]["type"] == "image_url"
        assert content[0]["image_url"]["url"] == "https://example.com/image.png"
        assert content[1]["type"] == "text"
    
    def test_build_with_video_url(self):
        """测试视频 URL 内容"""
        vision = GLMVision()
        content = vision._build_content(
            text="Analyze video",
            video_urls=["https://example.com/video.mp4"]
        )
        
        assert any(c["type"] == "video_url" for c in content)
    
    def test_build_with_file_url(self):
        """测试文件 URL 内容"""
        vision = GLMVision()
        content = vision._build_content(
            text="Read file",
            file_urls=["https://example.com/doc.pdf"]
        )
        
        assert any(c["type"] == "file_url" for c in content)
    
    def test_build_with_local_image(self, tmp_path):
        """测试本地图片内容"""
        # 创建临时图片
        from PIL import Image
        img = Image.new('RGB', (100, 100), color='red')
        img_path = tmp_path / "test.png"
        img.save(img_path)
        
        vision = GLMVision()
        content = vision._build_content(
            text="What is this?",
            local_image=str(img_path)
        )
        
        assert any(c["type"] == "image_url" for c in content)
        # 验证是 base64
        img_content = next(c for c in content if c["type"] == "image_url")
        assert len(img_content["image_url"]["url"]) > 0


class TestEncodeImage:
    """图片编码测试"""
    
    def test_encode_image(self, tmp_path):
        """测试图片转 base64"""
        from PIL import Image
        
        # 创建测试图片
        img = Image.new('RGB', (50, 50), color='blue')
        img_path = tmp_path / "test_encode.png"
        img.save(img_path)
        
        vision = GLMVision()
        encoded = vision._encode_image(str(img_path))
        
        # 验证是有效的 base64
        assert isinstance(encoded, str)
        assert len(encoded) > 0
        
        # 验证可以解码
        decoded = base64.b64decode(encoded)
        assert len(decoded) > 0
    
    def test_encode_nonexistent_image(self):
        """测试编码不存在的图片"""
        vision = GLMVision()
        
        with pytest.raises(FileNotFoundError):
            vision._encode_image("/nonexistent/path/image.png")


class TestExtractJson:
    """JSON 提取测试"""
    
    def test_extract_direct_json(self):
        """测试直接 JSON 解析"""
        vision = GLMVision()
        
        text = '{"found": true, "x": 100, "y": 200}'
        result = vision._extract_json(text)
        
        assert result == {"found": True, "x": 100, "y": 200}
    
    def test_extract_json_from_code_block(self):
        """测试从代码块提取 JSON"""
        vision = GLMVision()
        
        text = '''
        Here is the result:
        ```json
        {"action": "click", "x": 50, "y": 100}
        ```
        '''
        result = vision._extract_json(text)
        
        assert result == {"action": "click", "x": 50, "y": 100}
    
    def test_extract_json_from_plain_code_block(self):
        """测试从无语言标记的代码块提取"""
        vision = GLMVision()
        
        text = '''
        ```
        {"matched": true}
        ```
        '''
        result = vision._extract_json(text)
        
        assert result == {"matched": True}
    
    def test_extract_embedded_json(self):
        """测试从文本中提取嵌入的 JSON"""
        vision = GLMVision()
        
        text = 'The result is {"found": false} and that is final.'
        result = vision._extract_json(text)
        
        assert result == {"found": False}
    
    def test_extract_invalid_json(self):
        """测试无效 JSON 返回 None"""
        vision = GLMVision()
        
        text = "This is not JSON at all"
        result = vision._extract_json(text)
        
        assert result is None


class TestAnalyze:
    """分析功能测试"""
    
    @patch('src.glm_vision.HAS_ZAI_SDK', False)
    def test_analyze_with_http_success(self, tmp_path):
        """测试 HTTP 调用成功"""
        from PIL import Image
        
        # 创建测试图片
        img = Image.new('RGB', (100, 100), color='green')
        img_path = tmp_path / "test.png"
        img.save(img_path)
        
        vision = GLMVision()
        
        # Mock HTTP 响应
        with patch('requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "choices": [{
                    "message": {
                        "content": "This is a green image"
                    }
                }]
            }
            mock_post.return_value = mock_response
            
            result = vision.analyze(
                image_path=str(img_path),
                prompt="What color is this image?"
            )
            
            assert result["success"] == True
            assert "green" in result["content"].lower() or "This is a green image" in result["content"]
    
    @patch('src.glm_vision.HAS_ZAI_SDK', False)
    def test_analyze_http_error(self):
        """测试 HTTP 调用失败"""
        vision = GLMVision()
        
        with patch('requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 401
            mock_response.text = "Unauthorized"
            mock_post.return_value = mock_response
            
            result = vision.analyze(prompt="Test")
            
            assert result["success"] == False
            assert "401" in result["error"]


class TestFindElement:
    """元素查找测试"""
    
    def test_find_element_success(self, tmp_path):
        """测试成功找到元素"""
        from PIL import Image
        
        img = Image.new('RGB', (800, 600), color='white')
        img_path = tmp_path / "screen.png"
        img.save(img_path)
        
        vision = GLMVision()
        
        with patch.object(vision, 'analyze') as mock_analyze:
            mock_analyze.return_value = {
                "success": True,
                "content": '{"found": true, "x": 400, "y": 300, "width": 100, "height": 50}'
            }
            
            result = vision.find_element(str(img_path), "login button")
            
            assert result["found"] == True
            assert result["x"] == 400
            assert result["y"] == 300
    
    def test_find_element_not_found(self, tmp_path):
        """测试未找到元素"""
        from PIL import Image
        
        img = Image.new('RGB', (800, 600), color='white')
        img_path = tmp_path / "screen.png"
        img.save(img_path)
        
        vision = GLMVision()
        
        with patch.object(vision, 'analyze') as mock_analyze:
            mock_analyze.return_value = {
                "success": True,
                "content": '{"found": false}'
            }
            
            result = vision.find_element(str(img_path), "nonexistent button")
            
            assert result["found"] == False


class TestVerifyState:
    """状态验证测试"""
    
    def test_verify_state_matched(self, tmp_path):
        """测试状态匹配"""
        from PIL import Image
        
        img = Image.new('RGB', (800, 600), color='white')
        img_path = tmp_path / "screen.png"
        img.save(img_path)
        
        vision = GLMVision()
        
        with patch.object(vision, 'analyze') as mock_analyze:
            mock_analyze.return_value = {
                "success": True,
                "content": '{"matched": true, "confidence": 0.95}'
            }
            
            result = vision.verify_state(str(img_path), "login page")
            
            assert result["matched"] == True
            assert result["confidence"] > 0.9


class TestDecideAction:
    """决策测试"""
    
    def test_decide_click_action(self, tmp_path):
        """测试点击决策"""
        from PIL import Image
        
        img = Image.new('RGB', (800, 600), color='white')
        img_path = tmp_path / "screen.png"
        img.save(img_path)
        
        vision = GLMVision()
        
        with patch.object(vision, 'analyze') as mock_analyze:
            mock_analyze.return_value = {
                "success": True,
                "content": '{"action": "click", "x": 400, "y": 300, "target": "start button"}'
            }
            
            result = vision.decide_action(str(img_path), "Click start")
            
            assert result["action"] == "click"
            assert result["x"] == 400
            assert result["y"] == 300
    
    def test_decide_wait_action(self, tmp_path):
        """测试等待决策"""
        from PIL import Image
        
        img = Image.new('RGB', (800, 600), color='white')
        img_path = tmp_path / "screen.png"
        img.save(img_path)
        
        vision = GLMVision()
        
        with patch.object(vision, 'analyze') as mock_analyze:
            mock_analyze.return_value = {
                "success": True,
                "content": '{"action": "wait", "seconds": 3}'
            }
            
            result = vision.decide_action(str(img_path), "Wait for loading")
            
            assert result["action"] == "wait"
            assert result["seconds"] == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
