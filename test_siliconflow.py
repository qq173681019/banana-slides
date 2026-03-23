#!/usr/bin/env python3
"""测试 banana-slides 的硅基流动 API key 配置"""
import os
from pathlib import Path

# 项目根目录（脚本所在目录）
project_root = Path(__file__).parent

# 加载环境变量
from dotenv import load_dotenv

env_file = project_root / '.env'
usless_file = project_root / 'usless'

print("=== Banana Slides API Key 配置测试 ===\n")

print(f"项目根目录: {project_root}")
print(f".env 文件: {env_file}")
print(f".env 存在: {env_file.exists()}")
print(f"usless 文件: {usless_file}")
print(f"usless 存在: {usless_file.exists()}\n")

# 先加载 usless（低优先级）
if usless_file.exists():
    print("加载 usless 文件...")
    load_dotenv(dotenv_path=usless_file, override=False)

# 再加载 .env（高优先级）
if env_file.exists():
    print("加载 .env 文件...")
    load_dotenv(dotenv_path=env_file, override=True)

print("\n=== 已加载的 API Key ===\n")

# 检查各种 API key
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
        # 只显示前20个字符和后4个字符
        masked = f"{key_value[:20]}...{key_value[-4:]}" if len(key_value) > 24 else "***"
        status = "[OK]" if key_value else "[未设置]"
        print(f"{key_name:25s} {status} {masked}")
    else:
        print(f"{key_name:25s} [未设置]")

print("\n=== 其他配置 ===\n")

other_configs = {
    'AI_PROVIDER_FORMAT': os.getenv('AI_PROVIDER_FORMAT'),
    'TEXT_MODEL_SOURCE': os.getenv('TEXT_MODEL_SOURCE'),
    'IMAGE_MODEL_SOURCE': os.getenv('IMAGE_MODEL_SOURCE'),
    'TEXT_MODEL': os.getenv('TEXT_MODEL'),
    'IMAGE_MODEL': os.getenv('IMAGE_MODEL'),
    'BACKEND_PORT': os.getenv('BACKEND_PORT'),
    'FRONTEND_PORT': os.getenv('FRONTEND_PORT'),
}

for key_name, key_value in other_configs.items():
    print(f"{key_name:25s} = {key_value}")

# 测试硅基流动 API（如果有 key）
print("\n=== 测试硅基流动 API ===\n")

siliconflow_key = os.getenv('SILICONFLOW_API_KEY')
if siliconflow_key:
    print(f"发现硅基流动 API key，准备测试...")

    try:
        import requests

        # 测试模型列表 API
        base_url = "https://api.siliconflow.cn/v1"
        response = requests.get(
            f"{base_url}/models",
            headers={"Authorization": f"Bearer {siliconflow_key}"},
            timeout=10
        )

        if response.status_code == 200:
            models = response.json()
            print(f"[OK] API 认证成功！")
            print(f"[OK] 可用模型数量: {len(models.get('data', []))}")

            # 显示几个模型
            print("\n部分可用模型:")
            for model in models.get('data', [])[:5]:
                print(f"  - {model.get('id', 'N/A')}")

            # 测试对话 API
            print("\n测试对话 API...")
            chat_response = requests.post(
                f"{base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {siliconflow_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "deepseek-ai/DeepSeek-V3",
                    "messages": [{"role": "user", "content": "你好"}],
                    "max_tokens": 50
                },
                timeout=30
            )

            if chat_response.status_code == 200:
                result = chat_response.json()
                reply = result['choices'][0]['message']['content']
                print(f"[OK] 对话 API 工作正常")
                print(f"回复: {reply}")
            else:
                print(f"[WARN] 对话 API 失败: {chat_response.status_code}")
                print(f"响应: {chat_response.text[:200]}")

        else:
            print(f"[ERROR] API 认证失败: {response.status_code}")
            print(f"响应: {response.text[:200]}")

    except Exception as e:
        print(f"[ERROR] 测试失败: {e}")
else:
    print("[未设置] 没有配置硅基流动 API key")

print("\n=== 测试完成 ===")
