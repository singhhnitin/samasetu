import os, json, time, requests

KEY = os.environ["GNANI_API_KEY"].strip()
emb = json.load(open("embedding.json"))

t0 = time.time()
first = None
chunks = 0

r = requests.post("https://api.vachana.ai/api/v1/tts/sse",
    headers={"X-API-Key-ID": KEY, "Content-Type": "application/json"},
    json={"text": "நாளை காலை பத்து மணிக்கு உங்களைச் சந்திக்க வேண்டும்.",
          "model": "vachana-vc-v1", "speaker_embedding": emb,
          "audio_config": {"sample_rate": 44100, "encoding": "linear_pcm",
                           "container": "wav"}},
    stream=True)

print("status", r.status_code)
for line in r.iter_lines():
    if not line:
        continue
    s = line.decode("utf-8", "ignore")
    if s.startswith("data:") and len(s) > 20:
        chunks += 1
        if first is None:
            first = round((time.time() - t0) * 1000)
            print("first audio chunk:", first, "ms")

print("total chunks:", chunks)
print("full stream  :", round((time.time() - t0) * 1000), "ms")
