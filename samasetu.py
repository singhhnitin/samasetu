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

def show(state, hi="", ta=""):
    # display.json is read by display.html for the live screen
    try:
        with open("display.json", "w", encoding="utf-8") as f:
            json.dump({"state": state, "hi": hi, "ta": ta}, f, ensure_ascii=False)
    except Exception:
        pass

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

speaking = threading.Event()   # set while Tamil is playing

def speak(text, on_first_audio=None):
    # stream Tamil audio and play each chunk as it arrives
    r = requests.post("https://api.vachana.ai/api/v1/tts/sse",
        headers={**H, "Content-Type": "application/json"},
        json={"text": text, "model": "vachana-vc-v1", "speaker_embedding": emb,
              "audio_config": {"sample_rate": OUT_RATE, "encoding": "linear_pcm"}},
        stream=True)
    carry, started = b"", False
    with sd.RawOutputStream(samplerate=OUT_RATE, channels=1, dtype="int16") as out:
        for line in r.iter_lines():
            if not line:
                continue
            s = line.decode("utf-8", "ignore")
            if not s.startswith("data:"):
                continue
            try:
                a = json.loads(s[5:].strip()).get("audio")
            except Exception:
                continue
            if not a:
                continue
            pcm = carry + base64.b64decode(a)
            cut = len(pcm) - (len(pcm) % 2)   # keep whole 16-bit samples
            pcm, carry = pcm[:cut], pcm[cut:]
            if pcm:
                if not started:
                    started = True
                    if on_first_audio:
                        on_first_audio()
                out.write(pcm)

# one worker handles sentences in order, so two translations never talk over each other
jobs = queue.Queue()

def worker():
    while True:
        text = jobs.get()
        try:
            show("translating", text)
            ta = translate(text)
            print("   ->", ta)
            speaking.set()
            speak(ta, on_first_audio=lambda: show("speaking", text, ta))
            show("listening", text, ta)
        except Exception as e:
            print("   ! error:", e)
            show("listening")
        finally:
            speaking.clear()

threading.Thread(target=worker, daemon=True).start()

q = queue.Queue()
SILENCE = bytes(FRAME * 2)
def cb(indata, frames, t, status):
    # while Tamil plays, send silence so the mic doesn't pick up the speaker's own output
    q.put(SILENCE if speaking.is_set() else bytes(indata))

async def session():
    headers = {"x-api-key-id": KEY, "lang_code": "hi-IN",
               "x-sample-rate": str(RATE), "x-vad-threshold": "0.45",
               "x-min-silence-ms": "700", "x-max-speech-s": "30"}
    async with websockets.connect("wss://api.vachana.ai/stt/v3/stream",
                                  additional_headers=headers) as ws:
        print("[connected]")
        show("listening")

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
                    jobs.put(d["text"])

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
