import time, torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

M = "ai4bharat/indictrans2-indic-indic-dist-320M"
tok = AutoTokenizer.from_pretrained(M, trust_remote_code=True)
mt = AutoModelForSeq2SeqLM.from_pretrained(M, trust_remote_code=True)
mt.eval()

src = "hin_Deva tam_Taml मुझे कल सुबह दस बजे आपसे मिलना है।"
b = tok(src, return_tensors="pt")

for beams in [5, 3, 1]:
    t0 = time.time()
    with torch.no_grad():
        o = mt.generate(**b, max_length=128, num_beams=beams)
    ms = round((time.time() - t0) * 1000)
    print(beams, "beams:", ms, "ms —", tok.batch_decode(o, skip_special_tokens=True)[0][:60])
