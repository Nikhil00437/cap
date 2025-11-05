# test_hf.py (UPDATED)
from huggingface_hub import InferenceClient
import os
from dotenv import load_dotenv

load_dotenv()

token = os.getenv("HUGGINGFACEHUB_API_TOKEN")
if not token:
    print("❌ ERROR: HUGGINGFACEHUB_API_TOKEN not found in .env")
    exit(1)

print(f"✅ Token loaded (starts with: {token[:6]}...)")
print("🧪 Testing connection to Hugging Face with flan-t5-base...")

client = InferenceClient(
    model="google/flan-t5-base",  # ← CHANGED HERE
    token=token
)

try:
    response = client.text_generation("What is API authentication?", max_new_tokens=20)
    print("🎉 SUCCESS! Model responded:")
    print(f"💬 '{response}'")
except Exception as e:
    print("❌ FAILED to reach Hugging Face:")
    print(f"❗ {type(e).__name__}: {str(e)}")
    print("\n🛠️  QUICK FIXES:")
    print("- Go to https://huggingface.co/google/flan-t5-base and accept terms if prompted")
    print("- Regenerate token at https://huggingface.co/settings/tokens")
    print("- Still failing? Use LOCAL MODEL (instructions below)")