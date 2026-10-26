import os, json, time, statistics, requests, torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

KEY = os.environ["GNANI_API_KEY"].strip()
H = {"X-API-Key-ID": KEY}
emb = json.load(open("embedding.json"))

M = "ai4bharat/indictrans2-indic-indic-dist-320M"
tok = AutoTokenizer.from_pretrained(M, trust_remote_code=True)
mt = AutoModelForSeq2SeqLM.from_pretrained(M, trust_remote_code=True)
mt.eval()
print("loaded")

def time_it(fn, n=5):
    ts = []
    for _ in range(n):
        t0 = time.time()
        fn()
        ts.append((time.time() - t0) * 1000)
    return round(statistics.median(ts))

def stt():
    with open("test.wav", "rb") as f:
        requests.post("https://api.vachana.ai/stt/v3", headers=H,
                      files={"audio_file": f}, data={"language_code": "hi-IN"})

b = tok("hin_Deva tam_Taml मुझे कल सुबह दस बजे आपसे मिलना है।", return_tensors="pt")

def mtrans():
    with torch.no_grad():
        mt.generate(**b, max_length=128, num_beams=1)

def tts():
    requests.post("https://api.vachana.ai/api/v1/tts/inference",
        headers={**H, "Content-Type": "application/json"},
        json={"text": "நாளை காலை பத்து மணிக்கு உங்களைச் சந்திக்க வேண்டும்.",
              "model": "vachana-vc-v1", "speaker_embedding": emb,
              "audio_config": {"sample_rate": 44100, "num_channels": 1,
                               "sample_width": 2, "encoding": "linear_pcm",
                               "container": "wav"}})

a = time_it(stt)
c = time_it(mtrans)
d = time_it(tts)
print("STT       :", a, "ms")
print("Translate :", c, "ms")
print("TTS       :", d, "ms")
print("Total     :", a + c + d, "ms")
print("Budget 2000 ms:", "PASS" if a + c + d < 2000 else "OVER")
