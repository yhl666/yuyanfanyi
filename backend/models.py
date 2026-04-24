"""
数据模型定义
"""
from pydantic import BaseModel

class TranslateRequest(BaseModel):
    """翻译请求模型"""
    text: str
    src_lang: str = "auto"
    target_lang: str = "zh"
