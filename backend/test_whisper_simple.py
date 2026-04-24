"""
简单的 Whisper 测试脚本
直接运行，然后拖放音频文件到命令行窗口
"""
import os
import sys

# 设置 FFmpeg 路径
os.environ["PATH"] += os.pathsep + r"D:\ffmpeg-7.1.1\bin"

from faster_whisper import WhisperModel

# 模型路径
WHISPER_MODEL_PATH = r"D:\桌面\黄善文\1中泰实时翻译\backend\faster-whisper-small"

print("=" * 70)
print("                    Whisper 语音识别测试工具")
print("=" * 70)

# 加载模型
print("\n[1/2] 正在加载 Whisper 模型...")
try:
    model = WhisperModel(WHISPER_MODEL_PATH, device="cpu", compute_type="int8")
    print("      ✓ 模型加载成功！")
except Exception as e:
    print(f"      ✗ 模型加载失败: {e}")
    input("\n按回车键退出...")
    sys.exit(1)

print("\n[2/2] 准备就绪！")
print("\n" + "=" * 70)
print("使用方法:")
print("  1. 将音频文件拖放到此窗口")
print("  2. 按回车键开始识别")
print("  3. 输入 'q' 退出程序")
print("=" * 70)

def clean_path(path):
    """清理文件路径"""
    # 移除引号和空格
    path = path.strip().strip('"').strip("'")
    return path

def transcribe(file_path):
    """识别音频"""
    print("\n" + "-" * 70)
    print(f"文件: {os.path.basename(file_path)}")
    print("-" * 70)
    
    try:
        # 检查文件
        if not os.path.exists(file_path):
            print(f"✗ 文件不存在!")
            return
        
        file_size = os.path.getsize(file_path) / 1024
        print(f"大小: {file_size:.2f} KB")
        
        # 识别
        print("\n正在识别...")
        segments, info = model.transcribe(file_path, language=None)
        
        # 输出结果
        print(f"\n✓ 识别完成!")
        print(f"  语言: {info.language} (置信度: {info.language_probability:.1%})")
        print(f"  时长: {info.duration:.1f} 秒")
        
        print("\n" + "=" * 70)
        print("识别文本:")
        print("=" * 70)
        
        full_text = []
        for segment in segments:
            text = segment.text.strip()
            full_text.append(text)
            print(f"[{segment.start:6.1f}s] {text}")
        
        print("=" * 70)
        print("\n完整文本:")
        result = " ".join(full_text)
        print(result)
        print("=" * 70)
        
    except Exception as e:
        print(f"\n✗ 识别失败: {e}")
        import traceback
        traceback.print_exc()

# 主循环
while True:
    try:
        print("\n请拖放音频文件到此窗口 (或输入 'q' 退出):")
        user_input = input("> ").strip()
        
        if user_input.lower() == 'q':
            print("\n再见!")
            break
        
        if not user_input:
            continue
        
        file_path = clean_path(user_input)
        transcribe(file_path)
        
    except KeyboardInterrupt:
        print("\n\n再见!")
        break
    except Exception as e:
        print(f"\n错误: {e}")

input("\n按回车键退出...")
