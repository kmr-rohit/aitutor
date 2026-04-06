import os

# Keep tests deterministic and offline irrespective of developer .env values.
os.environ["LLM_PROVIDER"] = "mock"
os.environ["STT_PROVIDER"] = "mock"
os.environ["TTS_PROVIDER"] = "mock"
os.environ["OPENAI_API_KEY"] = ""
os.environ["SARVAM_API_KEY"] = ""
