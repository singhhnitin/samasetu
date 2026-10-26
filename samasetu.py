import asyncio, json, os, queue, base64, threading
import numpy as np
import sounddevice as sd
import websockets, requests, torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
from indicnlp.transliterate.unicode_transliterate import UnicodeIndicTransliterator

KEY = os.environ["GNANI_API_KEY"].strip()
H = {"X-API-Key-ID": KEY}
emb = json.load(open("embedding.json"))
RATE, FRAME, OUT_RATE = 16000, 512, 44100

print("loading translator...")
M = "ai4bharat/indictrans2-indic-indic-dist-320M"
tok = AutoTokenizer.from_pretrained(M, trust_remote_code=True)
mt = AutoModelForSeq2SeqLM.from_pretrained(M, trust_remote_code=True)
mt.eval()

def translate(text):
    b = tok(f"hin_Deva tam_Taml {text}", return_tensors="pt")
    with torch.no_grad():
        o = mt.generate(**b, max_length=128, num_beams=1)
    dev = tok.batch_decode(o, skip_special_tokens=True)[0]
    return UnicodeIndicTransliterator.transliterate(dev, "hi", "ta")

def speak(text):
    r = requests.post("https://api.vachana.ai/api/v1/tts/sse",
        headers={**H, "Content-Type": "application/json"},
        json={"text": text, "model": "vachana-vc-v1", "speaker_embedding": emb,
              "audio_config": {"sample_rate": OUT_RATE, "encoding": "linear_pcm"}},
        stream=True)
    buf = []
    for line in r.iter_lines():
        if not line:
            continue
        s = line.decode("utf-8", "ignore")
        if s.startswith("data:"):
            try:
                a = json.loads(s[5:].strip()).get("audio")
            except Exception:
                continue
            if a:
                buf.append(base64.b64decode(a))
    if buf:
        sd.play(np.frombuffer(b"".join(buf), dtype=np.int16), OUT_RATE)
        sd.wait()

q = queue.Queue()
def cb(indata, frames, t, status):
    q.put(bytes(indata))

def handle(text):
    try:
        ta = translate(text)
        print("   ->", ta)
        speak(ta)
    except Exception as e:
        print("   ! error:", e)

async def session():
    headers = {"x-api-key-id": KEY, "lang_code": "hi-IN",
               "x-sample-rate": str(RATE), "x-vad-threshold": "0.45", "x-max-speech-s": "30",
               "x-min-silence-ms": "700"}
    async with websockets.connect("wss://api.vachana.ai/stt/v3/stream",
                                  additional_headers=headers) as ws:
        print("[connected]")

        async def send():
            with sd.RawInputStream(samplerate=RATE, blocksize=FRAME,
                                   dtype="int16", channels=1, callback=cb):
                while True:
                    await asyncio.sleep(0.032)
                    while not q.empty():
                        await ws.send(q.get())

        async def recv():
            async for msg in ws:
                d = json.loads(msg)
                if d["type"] == "transcript" and d["text"].strip():
                    print("HI:", d["text"])
                    threading.Thread(target=handle, args=(d["text"],)).start()

        await asyncio.gather(send(), recv())

async def main():
    print("SPEAK HINDI - Ctrl+C to stop")
    while True:
        try:
            await session()
        except Exception as e:
            print("[reconnecting]", type(e).__name__)
            while not q.empty():
                q.get()
            await asyncio.sleep(1)

asyncio.run(main())
