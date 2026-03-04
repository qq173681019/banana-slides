#!/usr/bin/env python3
"""
API Key Verification Script — Banana Slides
============================================
Run this on your local machine to verify your AI provider API keys
before deploying.

Usage:
    python scripts/check_api_keys.py            # reads from .env automatically
    python scripts/check_api_keys.py --key sk-xxx --vendor qwen
    python scripts/check_api_keys.py --help

Supported vendors: qwen, deepseek, glm, doubao, siliconflow, minimax, sensenova
"""
import argparse
import os
import sys

# ---------------------------------------------------------------------------
# Vendor definitions: endpoint, model, auth header style
# ---------------------------------------------------------------------------
VENDOR_CONFIGS = {
    "qwen": {
        "name": "通义千问 (Alibaba Qwen)",
        "endpoint": "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
        "model": "qwen-turbo",
        "auth": "Bearer",
    },
    "deepseek": {
        "name": "DeepSeek",
        "endpoint": "https://api.deepseek.com/v1/chat/completions",
        "model": "deepseek-chat",
        "auth": "Bearer",
    },
    "glm": {
        "name": "智谱 GLM",
        "endpoint": "https://open.bigmodel.cn/api/paas/v4/chat/completions",
        "model": "glm-4-flash",
        "auth": "Bearer",
    },
    "doubao": {
        "name": "豆包 (Volcengine Doubao)",
        "endpoint": "https://ark.cn-beijing.volces.com/api/v3/chat/completions",
        "model": "doubao-1-5-lite-32k-250115",
        "auth": "Bearer",
    },
    "siliconflow": {
        "name": "SiliconFlow (硅基流动)",
        "endpoint": "https://api.siliconflow.cn/v1/chat/completions",
        "model": "Qwen/Qwen2.5-7B-Instruct",
        "auth": "Bearer",
    },
    "minimax": {
        "name": "MiniMax",
        "endpoint": "https://api.minimaxi.chat/v1/text/chatcompletion_v2",
        "model": "MiniMax-Text-01",
        "auth": "Bearer",
    },
    "sensenova": {
        "name": "商汤日日新 (SenseNova)",
        "endpoint": "https://api.sensenova.cn/v1/llm/chat-completions",
        "model": "SenseChat-5",
        "auth": "Bearer",
    },
}

# Keys that start with this prefix are considered un-filled placeholders
PLACEHOLDER_PREFIX = "your-"


def _load_dotenv(path: str = ".env") -> dict:
    """Minimal .env parser (no external deps)."""
    env = {}
    if not os.path.exists(path):
        return env
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            k, _, v = line.partition("=")
            k = k.strip()
            v = v.strip().strip('"').strip("'")
            env[k] = v
    return env


def _test_vendor(vendor: str, api_key: str, timeout: int = 20) -> tuple[bool, str]:
    """
    Make a minimal chat request to verify the API key.
    Returns (success: bool, message: str).
    """
    import json
    import ssl
    import urllib.error
    import urllib.request

    cfg = VENDOR_CONFIGS[vendor]
    payload = json.dumps({
        "model": cfg["model"],
        "messages": [{"role": "user", "content": "Reply with just the word OK."}],
        "max_tokens": 10,
        "stream": False,
    }).encode()

    req = urllib.request.Request(
        cfg["endpoint"],
        data=payload,
        headers={
            "Authorization": f"{cfg['auth']} {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    ctx = ssl.create_default_context()
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
            body = json.loads(resp.read())
            reply = (
                body.get("choices", [{}])[0]
                    .get("message", {})
                    .get("content", "")
                    .strip()
            )
            return True, f'OK ✅  Model reply: "{reply}"'
    except urllib.error.HTTPError as exc:
        try:
            err_body = json.loads(exc.read())
        except Exception:
            err_body = {}
        err_msg = (
            err_body.get("error", {}).get("message")
            or err_body.get("message")
            or exc.reason
        )
        if exc.code in (401, 403):
            return False, f"Auth failed ❌  HTTP {exc.code}: {err_msg}  →  API key is invalid or expired"
        if exc.code == 429:
            # Rate-limited, but key itself is valid
            return True, f"Rate limited ⚠️  HTTP 429 — key is valid, but too many requests; try again later"
        return False, f"API error ❌  HTTP {exc.code}: {err_msg}"
    except OSError as exc:
        return False, f"Network error ❌  {exc}  →  check your connection or the API endpoint"


def main():
    parser = argparse.ArgumentParser(
        description="Verify AI provider API keys for Banana Slides",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="\n".join(
            f"  {v:<14} {VENDOR_CONFIGS[v]['name']}"
            for v in VENDOR_CONFIGS
        ),
    )
    parser.add_argument(
        "--vendor", "-v",
        choices=list(VENDOR_CONFIGS),
        help="Vendor to test (default: auto-detect from .env)",
    )
    parser.add_argument(
        "--key", "-k",
        help="API key to test (default: read from .env / environment)",
    )
    parser.add_argument(
        "--env-file", "-e",
        default=".env",
        help="Path to .env file (default: .env)",
    )
    parser.add_argument(
        "--timeout", "-t",
        type=int,
        default=20,
        help="Request timeout in seconds (default: 20)",
    )
    args = parser.parse_args()

    # Load .env
    dotenv = _load_dotenv(args.env_file)

    # Decide which vendors to test
    if args.vendor and args.key:
        candidates = [(args.vendor, args.key)]
    elif args.vendor:
        env_key_name = f"{args.vendor.upper()}_API_KEY"
        api_key = os.environ.get(env_key_name) or dotenv.get(env_key_name, "")
        if not api_key:
            print(f"❌  找不到 {env_key_name}，请在 .env 中设置或用 --key 参数传入")
            sys.exit(1)
        candidates = [(args.vendor, api_key)]
    elif args.key:
        print("❌  使用 --key 时必须同时指定 --vendor")
        sys.exit(1)
    else:
        # Auto-detect: test all vendors with keys present in .env / env
        candidates = []
        for vendor in VENDOR_CONFIGS:
            env_key_name = f"{vendor.upper()}_API_KEY"
            api_key = os.environ.get(env_key_name) or dotenv.get(env_key_name, "")
            if api_key and not api_key.startswith(PLACEHOLDER_PREFIX):
                candidates.append((vendor, api_key))
        if not candidates:
            print("⚠️  在 .env 中未找到任何厂商 API Key。")
            print("   请先在 .env 中配置，例如: QWEN_API_KEY=sk-xxx")
            sys.exit(1)

    # Run tests
    print()
    print("=" * 60)
    print("  Banana Slides — API Key Checker")
    print("=" * 60)

    all_ok = True
    for vendor, api_key in candidates:
        cfg = VENDOR_CONFIGS[vendor]
        key_display = api_key[:8] + "****" + api_key[-4:] if len(api_key) > 12 else "****"
        print(f"\n[ {cfg['name']} ]")
        print(f"  Key   : {key_display}")
        print(f"  Model : {cfg['model']}")
        print(f"  Testing... ", end="", flush=True)
        ok, msg = _test_vendor(vendor, api_key, timeout=args.timeout)
        print(msg)
        if not ok:
            all_ok = False

    print()
    print("=" * 60)
    if all_ok:
        print("  All checks passed ✅")
    else:
        print("  Some checks failed ❌  See details above")
    print("=" * 60)
    print()

    sys.exit(0 if all_ok else 1)


if __name__ == "__main__":
    main()
