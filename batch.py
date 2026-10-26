import os, json, csv, glob, time, requests, torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
from indicnlp.transliterate.unicode_transliterate import UnicodeIndicTransliterator

KEY = os.environ["GNANI_API_KEY"].strip()
H = {"X-API-Key-ID": KEY}

M = "ai4bharat/indictrans2-indic-indic-dist-320M"
tok = AutoTokenizer.from_pretrained(M, trust_remote_code=True)
mt = AutoModelForSeq2SeqLM.from_pretrained(M, trust_remote_code=True)
mt.eval()
SCRIPT = {"tam_Taml": "ta", "mar_Deva": "hi", "eng_Latn": None}

def translate(text, tgt):
    b = tok(f"hin_Deva {tgt} {text}", return_tensors="pt")
    with torch.no_grad():
        o = mt.generate(**b, max_length=128, num_beams=5)
    dev = tok.batch_decode(o, skip_special_tokens=True)[0]
    s = SCRIPT[tgt]
    return UnicodeIndicTransliterator.transliterate(dev, "hi", s) if s else dev

rows = []
for path in sorted(glob.glob("clips/*.wav")):
    t0 = time.time()
    with open(path, "rb") as f:
        r = requests.post("https://api.vachana.ai/stt/v3", headers=H,
                          files={"audio_file": f}, data={"language_code": "hi-IN"})
    j = r.json()
    hi = j["output"]["literal"]
    row = {"file": os.path.basename(path), "hindi": hi,
           "stt_ms": round(j.get("end_to_end_latency", 0) * 1000)}
    for tgt in ["tam_Taml", "mar_Deva"]:
        row[tgt] = translate(hi, tgt)
    row["total_ms"] = round((time.time() - t0) * 1000)
    rows.append(row)
    print(row["file"], row["total_ms"], "ms")

if rows:
    with open("results.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print("wrote results.csv —", len(rows), "clips")
else:
    print("no clips found — put .wav files in a clips/ folder")
