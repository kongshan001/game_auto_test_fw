# -*- coding: utf-8 -*-
"""
配置模块单元测试
"""

import os
import sys
import pytest
from pathlib import Path
from unittest.mock import patch

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

import config


class TestConfig:
    """配置模块测试"""
    
    def test_glm_api_url(self):
        """测试 API URL 配置"""
        assert config.GLM_API_URL == "https://open.bigmodel.cn/api/paas/v4/chat/completions"
    
    def test_glm_model_default(self):
        """测试默认模型配置"""
        assert config.GLM_MODEL in ["glm-4.6v-flash", "glm-4.6v", "glm-4.6v-flashx", "glm-4v-flash"]
    
    def test_directories_exist(self):
        """测试目录是否创建"""
        assert config.SCREENSHOT_DIR.exists()
        assert config.LOG_DIR.exists()
        assert config.REPORT_DIR.exists()
    
    def test_max_steps_default(self):
        """测试最大步数默认值"""
        assert config.MAX_STEPS > 0
        assert config.MAX_STEPS <= 100
    
    def test_timeout_config(self):
        """测试超时配置"""
        assert config.DECISION_TIMEOUT > 0
        assert config.RETRY_TIMES >= 0
    
    def test_test_goals_structure(self):
        """测试测试目标结构"""
        assert "initial" in config.TEST_GOALS
        assert "final" in config.TEST_GOALS
        assert isinstance(config.TEST_GOALS["initial"], str)
        assert isinstance(config.TEST_GOALS["final"], str)
    
    @patch.dict(os.environ, {"GLM_MODEL": "glm-4.6v"})
    def test_env_override(self):
        """测试环境变量覆盖"""
        # 需要重新导入才能生效
        import importlib
        importlib.reload(config)
        assert config.GLM_MODEL == "glm-4.6v"


class TestEnvHelpers:
    """环境变量辅助函数测试"""
    
    def test_get_env_bool_true(self):
        """测试布尔值解析 - True"""
        with patch.dict(os.environ, {"TEST_BOOL": "true"}):
            assert config.get_env_bool("TEST_BOOL") == True
        
        with patch.dict(os.environ, {"TEST_BOOL": "1"}):
            assert config.get_env_bool("TEST_BOOL") == True
        
        with patch.dict(os.environ, {"TEST_BOOL": "yes"}):
            assert config.get_env_bool("TEST_BOOL") == True
    
    def test_get_env_bool_false(self):
        """测试布尔值解析 - False"""
        with patch.dict(os.environ, {"TEST_BOOL": "false"}):
            assert config.get_env_bool("TEST_BOOL") == False
        
        with patch.dict(os.environ, {"TEST_BOOL": "0"}):
            assert config.get_env_bool("TEST_BOOL") == False
    
    def test_get_env_bool_default(self):
        """测试布尔值默认值"""
        assert config.get_env_bool("NONEXISTENT_KEY", True) == True
        assert config.get_env_bool("NONEXISTENT_KEY", False) == False
    
    def test_get_env_int(self):
        """测试整数值解析"""
        with patch.dict(os.environ, {"TEST_INT": "42"}):
            assert config.get_env_int("TEST_INT") == 42
        
        with patch.dict(os.environ, {"TEST_INT": "invalid"}):
            assert config.get_env_int("TEST_INT", 10) == 10


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
