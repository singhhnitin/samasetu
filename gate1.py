import os, json, requests

KEY = os.environ["GNANI_API_KEY"].strip()
H = {"X-API-Key-ID": KEY}

with open("ref.wav", "rb") as f:
    r = requests.post("https://api.vachana.ai/api/v1/tts/voice-clone/embeddings",
                      headers=H, files={"audio_file": f})
emb = r.json()["data"]["voice_clone_embedding"]
json.dump(emb, open("embedding.json", "w"))
print("embedding ok, shape", emb.get("shape"))

tests = {
    "hi": "नमस्ते, मैं कल सुबह दस बजे आपसे मिलूंगा।",
    "ta": "வணக்கம், நாளை காலை பத்து மணிக்கு உங்களை சந்திப்பேன்.",
    "mr": "नमस्कार, मी उद्या सकाळी दहा वाजता तुम्हाला भेटेन.",
}

for lang, text in tests.items():
    r = requests.post(
        "https://api.vachana.ai/api/v1/tts/inference",
        headers={**H, "Content-Type": "application/json"},
        json={"text": text,
              "model": "vachana-vc-v1",
              "speaker_embedding": emb,
              "audio_config": {"sample_rate": 44100, "num_channels": 1,
                               "sample_width": 2, "encoding": "linear_pcm",
                               "container": "wav"}})
    print(lang, r.status_code, len(r.content))
    if r.status_code == 200:
        open(f"out_{lang}.wav", "wb").write(r.content)
    else:
        print("  ", r.text[:200])
