import os, requests

KEY = os.environ["GNANI_API_KEY"].strip()

with open("test.wav", "rb") as f:
    r = requests.post(
        "https://api.vachana.ai/stt/v3",
        headers={"X-API-Key-ID": KEY},
        files={"audio_file": f},
        data={"language_code": "hi-IN"},
    )

print(r.status_code)
print(r.json())
