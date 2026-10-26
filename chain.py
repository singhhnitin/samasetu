import os, json, requests

KEY = os.environ["GNANI_API_KEY"].strip()
H = {"X-API-Key-ID": KEY}
emb = json.load(open("embedding.json"))

with open("test.wav", "rb") as f:
    r = requests.post("https://api.vachana.ai/stt/v3", headers=H,
                      files={"audio_file": f},
                      data={"language_code": "hi-IN"})
heard = r.json()["output"]["literal"]
print("heard     :", heard)

tamil = "நாளை காலை பத்து மணிக்கு நான் உங்களை சந்திக்க வேண்டும்."
print("translated:", tamil)

r = requests.post("https://api.vachana.ai/api/v1/tts/inference",
    headers={**H, "Content-Type": "application/json"},
    json={"text": tamil, "model": "vachana-vc-v1", "speaker_embedding": emb,
          "audio_config": {"sample_rate": 44100, "num_channels": 1,
                           "sample_width": 2, "encoding": "linear_pcm",
                           "container": "wav"}})
open("chain_out.wav", "wb").write(r.content)
print("spoke     :", r.status_code, len(r.content), "bytes")
