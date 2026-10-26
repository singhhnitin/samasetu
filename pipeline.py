import os, json, requests, torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
from indicnlp.transliterate.unicode_transliterate import UnicodeIndicTransliterator

KEY = os.environ["GNANI_API_KEY"].strip()
H = {"X-API-Key-ID": KEY}
emb = json.load(open("embedding.json"))

M = "ai4bharat/indictrans2-indic-indic-dist-320M"
tok = AutoTokenizer.from_pretrained(M, trust_remote_code=True)
mt = AutoModelForSeq2SeqLM.from_pretrained(M, trust_remote_code=True)
mt.eval()

SCRIPT = {"tam_Taml": "ta", "tel_Telu": "te", "kan_Knda": "kn",
          "mal_Mlym": "ml", "ben_Beng": "bn", "mar_Deva": "hi"}

def translate(text, src="hin_Deva", tgt="tam_Taml"):
    b = tok(f"{src} {tgt} {text}", return_tensors="pt")
    with torch.no_grad():
        o = mt.generate(**b, max_length=128, num_beams=5)
    dev = tok.batch_decode(o, skip_special_tokens=True)[0]
    return UnicodeIndicTransliterator.transliterate(dev, "hi", SCRIPT[tgt])

def listen(path, lang="hi-IN"):
    with open(path, "rb") as f:
        r = requests.post("https://api.vachana.ai/stt/v3", headers=H,
                          files={"audio_file": f}, data={"language_code": lang})
    return r.json()["output"]["literal"]

def speak(text, out):
    r = requests.post("https://api.vachana.ai/api/v1/tts/inference",
        headers={**H, "Content-Type": "application/json"},
        json={"text": text, "model": "vachana-vc-v1", "speaker_embedding": emb,
              "audio_config": {"sample_rate": 44100, "num_channels": 1,
                               "sample_width": 2, "encoding": "linear_pcm",
                               "container": "wav"}})
    open(out, "wb").write(r.content)
    return r.status_code

heard = listen("test.wav")
print("heard  :", heard)
tamil = translate(heard)
print("tamil  :", tamil)
print("spoke  :", speak(tamil, "final_out.wav"), "-> final_out.wav")
