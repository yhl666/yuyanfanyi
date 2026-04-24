"""
历史记录服务
"""
import json
from datetime import datetime, timedelta
from pathlib import Path
from config import LOGS_DIR

def get_available_dates():
    """获取所有有记录的日期"""
    dates = []
    for log_file in LOGS_DIR.glob("transcript_*.jsonl"):
        date_str = log_file.stem.replace("transcript_", "")
        try:
            date_obj = datetime.strptime(date_str, "%Y%m%d")
            dates.append({
                "date": date_str,
                "formatted": date_obj.strftime("%Y年%m月%d日"),
                "file": log_file.name
            })
        except ValueError:
            continue
    
    # 按日期倒序排序
    dates.sort(key=lambda x: x["date"], reverse=True)
    return dates

def get_history_by_date(date_str: str):
    """获取指定日期的对话记录"""
    log_file = LOGS_DIR / f"transcript_{date_str}.jsonl"
    
    if not log_file.exists():
        return []
    
    records = []
    try:
        with open(log_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    record = json.loads(line)
                    records.append(record)
    except Exception as e:
        print(f"读取历史记录错误: {e}")
        return []
    
    return records

def search_history(keyword: str, date_str: str = None):
    """搜索历史记录"""
    results = []
    
    # 确定要搜索的文件
    if date_str:
        log_files = [LOGS_DIR / f"transcript_{date_str}.jsonl"]
    else:
        log_files = list(LOGS_DIR.glob("transcript_*.jsonl"))
    
    for log_file in log_files:
        if not log_file.exists():
            continue
        
        try:
            with open(log_file, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        record = json.loads(line)
                        # 在原文和译文中搜索
                        if (keyword.lower() in record.get("original", "").lower() or 
                            keyword.lower() in record.get("translated", "").lower()):
                            results.append(record)
        except Exception as e:
            print(f"搜索历史记录错误: {e}")
            continue
    
    return results

def get_statistics():
    """获取统计信息"""
    total_records = 0
    by_mode = {}
    by_language = {}
    
    for log_file in LOGS_DIR.glob("transcript_*.jsonl"):
        try:
            with open(log_file, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        record = json.loads(line)
                        total_records += 1
                        
                        # 按模式统计
                        mode = record.get("mode", "unknown")
                        by_mode[mode] = by_mode.get(mode, 0) + 1
                        
                        # 按语言统计
                        src_lang = record.get("src_lang", "unknown")
                        by_language[src_lang] = by_language.get(src_lang, 0) + 1
        except Exception as e:
            print(f"统计错误: {e}")
            continue
    
    return {
        "total": total_records,
        "by_mode": by_mode,
        "by_language": by_language
    }
