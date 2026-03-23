#!/usr/bin/env python3
"""Test AI Service initialization"""
import sys
sys.path.insert(0, "C:/Users/admin/Documents/GitHub/banana-slides/backend")

import os
os.environ.setdefault('FLASK_ENV', 'production')

from services.ai_service_manager import get_ai_service

print("=== Testing AI Service ===\n")

try:
    ai_service = get_ai_service()
    print("[OK] AI Service initialized successfully")
    print(f"  Text model: {ai_service.text_model}")
    print(f"  Image model: {ai_service.image_model}")
    print(f"  Caption model: {ai_service.caption_model}")

    # Test text generation
    print("\nTesting text generation...")
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Say hello in one word."}
    ]
    response = ai_service.generate_json(
        messages=messages,
        temperature=0.7,
        max_tokens=100
    )
    print(f"[OK] Text generation successful")
    print(f"  Response: {str(response)[:100]}...")

except Exception as e:
    print(f"[ERROR] AI Service failed: {e}")
    import traceback
    traceback.print_exc()
