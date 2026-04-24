"""
日志服务
"""
import json
from datetime import datetime
from config import LOGS_DIR

def save_log(mode: str, src_lang: str, original: str, translated: str):
    """保存对话记录"""
    today = datetime.now().strftime("%Y%m%d")
    log_file = LOGS_DIR / f"transcript_{today}.jsonl"
    
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "mode": mode,
        "src_lang": src_lang,
        "original": original,
        "translated": translated
    }
    
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
