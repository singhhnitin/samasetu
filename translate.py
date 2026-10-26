from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
from indicnlp.transliterate.unicode_transliterate import UnicodeIndicTransliterator
import torch

M = "ai4bharat/indictrans2-indic-indic-dist-320M"
tok = AutoTokenizer.from_pretrained(M, trust_remote_code=True)
model = AutoModelForSeq2SeqLM.from_pretrained(M, trust_remote_code=True)
model.eval()

def translate(text, src="hin_Deva", tgt="tam_Taml"):
    batch = tok(f"{src} {tgt} {text}", return_tensors="pt")
    with torch.no_grad():
        out = model.generate(**batch, max_length=128, num_beams=5)
    dev = tok.batch_decode(out, skip_special_tokens=True)[0]
    script = {"tam_Taml": "ta", "tel_Telu": "te", "kan_Knda": "kn",
              "mal_Mlym": "ml", "ben_Beng": "bn", "mar_Deva": "hi"}[tgt]
    return UnicodeIndicTransliterator.transliterate(dev, "hi", script)

src = "मुझे कल सुबह दस बजे आपसे मिलना है।"
print("tamil  :", translate(src, tgt="tam_Taml"))
print("telugu :", translate(src, tgt="tel_Telu"))
print("marathi:", translate(src, tgt="mar_Deva"))
