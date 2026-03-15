import os
from huggingface_hub import HfApi

token = os.getenv("HF_TOKEN")

try:
    api = HfApi(token=token)
    user_info = api.whoami()
    username = user_info['name']
    repo_id = f"{username}/ai-eye-contact-backend"
    
    print(f"Uploading backend folder to {repo_id}...")
    
    api.upload_folder(
        folder_path="c:\\Users\\Admin\\ai-eye-contact\\backend",
        repo_id=repo_id,
        repo_type="space",
        ignore_patterns=["__pycache__", "temp_frames*", "temp_audio*", "processed_frames*", "*.pyc", ".env"]
    )
    
    print("Upload completed successfully!")
    print(f"Your space is URL is: https://huggingface.co/spaces/{repo_id}")
    
except Exception as e:
    print(f"An error occurred: {e}")
