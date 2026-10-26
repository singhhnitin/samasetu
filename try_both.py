import os, requests

KEY = os.environ["GNANI_API_KEY"].strip()
URL = "https://api.vachana.ai/api/v1/tts/voice-clone/embeddings"

for name in ["test.wav", "ref.wav"]:
    with open(name, "rb") as f:
        r = requests.post(URL, headers={"X-API-Key-ID": KEY},
                          files={"audio_file": f})
    print(name, "->", r.status_code, r.text[:200])
