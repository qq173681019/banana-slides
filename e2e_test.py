#!/usr/bin/env python3
"""Banana Slides E2E Test - Create project to export PPT"""
import sys
import json
import time
import requests
from pathlib import Path

# Set UTF-8 encoding for output
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

print("=== Banana Slides E2E Test ===\n")

# Step 1: Use test outline (skip DOCX reading)
print("[1/6] Using test outline...")
outline_text = """Openclaw is an AI assistant

Main Features
- Smart conversation
- Project management
- Task collaboration
- Workflow automation

Tech Stack
- Python
- Flask
- React
- Docker

Goals
- Improve efficiency
- Reduce repetitive work
- Smart decision making

Future Plans
- Deep learning
- Multi-modal understanding
- Autonomous task execution
"""
print(f"Outline preview (first 200 chars):\n{outline_text[:200]}...")
print(f"Outline length: {len(outline_text)} chars\n")

# API base URL
BASE_URL = "http://localhost:5461"

# Step 2: Create project
print("[2/6] Creating project...")
try:
    create_response = requests.post(
        f"{BASE_URL}/api/projects",
        json={
            "creation_type": "outline",  # Required: "idea", "outline", or "descriptions"
            "outline_text": outline_text,  # Required for outline type
            "title": "Openclaw PPT Test",
            "image_aspect_ratio": "16:9"
        },
        timeout=30
    )

    print(f"Response status: {create_response.status_code}")

    try:
        project_data = create_response.json()
    except json.JSONDecodeError as e:
        print(f"Failed to decode JSON: {e}")
        print(f"Response text: {create_response.text[:500]}")
        sys.exit(1)

    print(f"Full response: {json.dumps(project_data, indent=2, ensure_ascii=False)[:1000]}")

    # Response format: { success: true, data: { project_id: "...", pages: [], status: "DRAFT" } }
    if 'data' in project_data and 'project_id' in project_data['data']:
        project_id = project_data['data']['project_id']
        print(f"[OK] Project created successfully")
        print(f"  Project ID: {project_id}")
        print(f"  Status: {project_data['data'].get('status', 'N/A')}\n")
    else:
        print(f"[ERROR] Unexpected response structure")
        print(f"Available keys: {list(project_data.keys())}")
        print(f"Data keys: {list(project_data.get('data', {}).keys())}")
        sys.exit(1)

except Exception as e:
    print(f"[ERROR] Failed to create project: {e}")
    if 'create_response' in locals():
        print(f"Response: {create_response.text if hasattr(create_response, 'text') else create_response}")
    sys.exit(1)

# Step 3: Generate outline
print("[3/6] Generating outline...")
try:
    outline_response = requests.post(
        f"{BASE_URL}/api/projects/{project_id}/generate/outline",
        json={
            "language": "zh"
        },
        timeout=60
    )
    outline_data = outline_response.json()

    if 'data' in outline_data and 'pages' in outline_data['data']:
        print(f"[OK] Outline generated successfully")
        print(f"  Number of pages: {len(outline_data['data']['pages'])}\n")
    else:
        print(f"[ERROR] Failed to generate outline")
        print(f"Response: {json.dumps(outline_data, indent=2, ensure_ascii=False)[:500]}")
        sys.exit(1)

except Exception as e:
    print(f"[ERROR] Failed to generate outline: {e}")
    print(f"Response: {outline_response.text if hasattr(outline_response, 'text') else outline_response}")
    sys.exit(1)

# Step 4: Generate descriptions
print("[4/6] Generating descriptions...")
try:
    desc_response = requests.post(
        f"{BASE_URL}/api/projects/{project_id}/generate/descriptions",
        json={
            "language": "zh",
            "detail_level": "default"
        },
        timeout=120
    )
    desc_data = desc_response.json()

    if 'data' in desc_data and 'task_id' in desc_data['data']:
        task_id = desc_data['data']['task_id']
        print(f"[OK] Description generation task submitted")
        print(f"  Task ID: {task_id}\n")
    else:
        print(f"[ERROR] Failed to submit description task")
        print(f"Response: {json.dumps(desc_data, indent=2, ensure_ascii=False)[:500]}")
        sys.exit(1)

except Exception as e:
    print(f"[ERROR] Failed to generate descriptions: {e}")
    print(f"Response: {desc_response.text if hasattr(desc_response, 'text') else desc_response}")
    sys.exit(1)

# Wait for task completion
print("Waiting for description generation to complete...")
max_wait = 180  # Max wait 3 minutes
start_time = time.time()

while time.time() - start_time < max_wait:
    try:
        status_response = requests.get(
            f"{BASE_URL}/api/projects/{project_id}/tasks/{task_id}",
            timeout=10
        )
        status_data = status_response.json()

        if 'data' in status_data:
            task_status = status_data['data'].get('status')

            if task_status == 'COMPLETED':
                print(f"[OK] Description generation completed!")
                print(f"  Time taken: {int(time.time() - start_time)} seconds\n")
                break
            elif task_status == 'FAILED':
                error_msg = status_data['data'].get('error_message', 'Unknown error')
                print(f"[ERROR] Description generation failed: {error_msg}")
                sys.exit(1)

            # Show progress
            progress = status_data['data'].get('progress', {})
            if progress:
                completed = progress.get('completed', 0)
                total = progress.get('total', 1)
                print(f"  Progress: {completed}/{total} ({int(completed/total*100)}%)")

        time.sleep(3)
    except Exception as e:
        print(f"  Error checking status: {e}, retrying...")
        time.sleep(3)
else:
    print(f"[ERROR] Description generation timeout ({max_wait} seconds)")
    sys.exit(1)

# Step 5: Generate images (or skip)
print("[5/6] Image generation settings...")
# Option A: Skip image generation, export text-only PPT
skip_images = True

# Option B: Try to generate images
# skip_images = False

if skip_images:
    print("[INFO] Skipping image generation, will export text-only PPT\n")
else:
    print("[INFO] Trying to generate images...")
    try:
        generate_response = requests.post(
            f"{BASE_URL}/api/projects/{project_id}/generate/images",
            json={
                "language": "zh"
            },
            timeout=10
        )
        generate_data = generate_response.json()

        if 'data' in generate_data and 'task_id' in generate_data['data']:
            task_id = generate_data['data']['task_id']
            print(f"[OK] Image generation task submitted")
            print(f"  Task ID: {task_id}\n")

            # Wait for task completion
            print("Waiting for image generation to complete...")
            max_wait = 300  # Max wait 5 minutes
            start_time = time.time()

            while time.time() - start_time < max_wait:
                try:
                    status_response = requests.get(
                        f"{BASE_URL}/api/projects/{project_id}/tasks/{task_id}",
                        timeout=10
                    )
                    status_data = status_response.json()

                    if 'data' in status_data:
                        task_status = status_data['data'].get('status')

                        if task_status == 'COMPLETED':
                            print(f"[OK] Image generation completed!")
                            print(f"  Time taken: {int(time.time() - start_time)} seconds\n")
                            break
                        elif task_status == 'FAILED':
                            error_msg = status_data['data'].get('error_message', 'Unknown error')
                            print(f"[ERROR] Image generation failed: {error_msg}")
                            print(f"[INFO] Skipping image generation, export text-only PPT\n")
                            skip_images = True
                            break

                        # Show progress
                        progress = status_data['data'].get('progress', {})
                        if progress:
                            completed = progress.get('completed', 0)
                            total = progress.get('total', 1)
                            print(f"  Progress: {completed}/{total} ({int(completed/total*100)}%)")

                    time.sleep(3)
                except Exception as e:
                    print(f"  Error checking status: {e}, retrying...")
                    time.sleep(3)
            else:
                print(f"[ERROR] Image generation timeout ({max_wait} seconds)")
                print(f"[INFO] Skipping image generation, export text-only PPT\n")
                skip_images = True
        else:
            print(f"[ERROR] Failed to submit image generation task")
            print(f"Response: {json.dumps(generate_data, indent=2, ensure_ascii=False)[:500]}")
            skip_images = True

    except Exception as e:
        print(f"[ERROR] Failed to generate images: {e}")
        print(f"[INFO] Skipping image generation, export text-only PPT\n")
        skip_images = True

# Step 6: Export PPT
print("[6/6] Exporting PPT...")
try:
    export_url = f"{BASE_URL}/api/projects/{project_id}/export/pptx?skip_images={'true' if skip_images else 'false'}"
    print(f"Export URL: {export_url}")

    export_response = requests.get(
        export_url,
        timeout=60
    )
    export_data = export_response.json()

    if export_data.get('success'):
        download_url = export_data['data']['download_url_absolute']
        print(f"[OK] PPT export successful!")
        print(f"  Download URL: {download_url}\n")

        # Download PPT file
        print("Downloading PPT file...")
        ppt_response = requests.get(download_url, timeout=60)

        # Save PPT file
        output_path = Path("C:/Users/admin/Documents/GitHub/banana-slides/test_output/test_pptx_export.pptx")
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'wb') as f:
            f.write(ppt_response.content)

        file_size = output_path.stat().st_size
        print(f"[OK] PPT file saved")
        print(f"  Save path: {output_path}")
        print(f"  File size: {file_size / 1024:.2f} KB\n")
    else:
        print(f"[ERROR] Export failed: {export_data.get('message', 'Unknown error')}")
        sys.exit(1)

except Exception as e:
    print(f"[ERROR] Failed to export: {e}")
    print(f"Response: {export_response.text if hasattr(export_response, 'text') else export_response}")
    sys.exit(1)

# Complete
print("=" * 50)
print("[OK] All steps completed!")
print(f"Project ID: {project_id}")
print(f"PPT File: {output_path}")
print("=" * 50)
