import os, json, requests

KEY = os.environ["GNANI_API_KEY"].strip()

with open("ref.mp3", "rb") as f:
    r = requests.post(
        "https://api.vachana.ai/api/v1/tts/voice-clone/embeddings",
        headers={"X-API-Key-ID": KEY},
        files={"audio_file": f},
    )

print(r.status_code)
if r.status_code == 200:
    emb = r.json()
    json.dump(emb, open("embedding.json", "w"))
    print("keys:", list(emb.keys()))
    print("shape:", emb.get("shape"))
    print("dtype:", emb.get("dtype"))
else:
    print(r.text)
