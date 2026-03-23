#!/usr/bin/env python3
"""诊断图片生成失败的原因"""
import os
import sys
from pathlib import Path

# 添加 backend 目录到 Python 路径
backend_dir = Path(__file__).parent / 'backend'
sys.path.insert(0, str(backend_dir))

# 激活虚拟环境
venv_dir = Path(__file__).parent / 'backend' / 'venv'
if venv_dir.exists():
    import site
    site_packages = venv_dir / 'Lib' / 'site-packages'
    sys.path.insert(0, str(site_packages))

# 加载环境变量
from dotenv import load_dotenv
project_root = Path(__file__).parent
env_file = project_root / '.env'
load_dotenv(env_file, override=True)

print("=== Banana Slides 图片生成诊断 ===\n")

# 1. 检查配置
print("【1. 检查 AI 配置】")
print(f"AI_PROVIDER_FORMAT: {os.getenv('AI_PROVIDER_FORMAT')}")
print(f"TEXT_MODEL_SOURCE: {os.getenv('TEXT_MODEL_SOURCE')}")
print(f"IMAGE_MODEL_SOURCE: {os.getenv('IMAGE_MODEL_SOURCE')}")
print(f"IMAGE_MODEL: {os.getenv('IMAGE_MODEL')}")
print()

# 2. 检查 API Keys
print("【2. 检查 API Keys】")
api_keys = {
    'GOOGLE_API_KEY': os.getenv('GOOGLE_API_KEY'),
    'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY'),
    'QWEN_API_KEY': os.getenv('QWEN_API_KEY'),
    'DEEPSEEK_API_KEY': os.getenv('DEEPSEEK_API_KEY'),
    'GLM_API_KEY': os.getenv('GLM_API_KEY'),
    'SILICONFLOW_API_KEY': os.getenv('SILICONFLOW_API_KEY'),
}

for key_name, key_value in api_keys.items():
    if key_value:
        print(f"[OK] {key_name}: {key_value[:20]}...{key_value[-4:]}")
    else:
        print(f"[MISS] {key_name}: [未设置]")
print()

# 3. 测试图片生成
print("【3. 测试图片生成】")

try:
    from services.ai_service_manager import get_ai_service

    ai_service = get_ai_service()
    print(f"[OK] AI Service 创建成功")
    print(f"  - Image Model: {ai_service.image_model}")
    print(f"  - Caption Model: {ai_service.caption_model}")
    print()

    # 测试图片生成
    print("  正在测试图片生成（提示词：一只可爱的猫）...")
    try:
        from PIL import Image
        image = ai_service.generate_image(
            prompt="一只可爱的猫",
            aspect_ratio="1:1",
            resolution="1K"
        )

        if image:
            print(f"[OK] 图片生成成功！")
            print(f"  - 图片尺寸: {image.size}")

            # 保存测试图片
            output_dir = project_root / "output" / "test"
            output_dir.mkdir(parents=True, exist_ok=True)
            test_image_path = output_dir / "test_image_generation.png"
            image.save(test_image_path)
            print(f"  - 测试图片已保存: {test_image_path}")
        else:
            print(f"[FAIL] 图片生成失败：返回了 None")

    except Exception as e:
        print(f"[FAIL] 图片生成失败：{type(e).__name__}: {e}")
        import traceback
        print("\n  详细错误信息：")
        for line in traceback.format_exc().split('\n'):
            if line.strip():
                print(f"    {line}")

except Exception as e:
    print(f"[FAIL] AI Service 初始化失败：{type(e).__name__}: {e}")
    import traceback
    for line in traceback.format_exc().split('\n'):
        if line.strip():
            print(f"    {line}")

print("\n=== 诊断完成 ===")
