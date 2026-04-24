"""
翻译服务
"""
import services.model_loader as ml

async def correct_text(text: str, lang: str) -> str:
    """使用 AI 纠正语音识别错误"""
    lang_map = {"zh": "中文", "th": "泰语", "en": "英语"}
    
    prompt = f"以下是语音识别的{lang_map.get(lang, '文本')}，可能有识别错误，请纠正错别字和语法错误，只输出纠正后的文本：\n{text}"
    
    try:
        response = ml.deepseek_client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "你是一个文本纠错助手，纠正语音识别中的错误，只输出纠正后的文本，不要解释。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            max_tokens=200
        )
        corrected = response.choices[0].message.content.strip()
        return corrected if corrected else text
    except Exception as e:
        print(f"纠错错误: {e}")
        return text

async def translate_text(text: str, src_lang: str, target_lang: str) -> str:
    """使用 DeepSeek 翻译文本"""
    lang_map = {"zh": "中文", "th": "泰语", "en": "英语"}
    
    prompt = f"将以下{lang_map[src_lang]}翻译成{lang_map[target_lang]}，只输出翻译结果，不要解释：\n{text}"
    
    try:
        response = ml.deepseek_client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "你是一个专业的翻译助手，只输出翻译结果，不要添加任何解释或额外内容。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=200
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"翻译错误: {e}")
        return text
