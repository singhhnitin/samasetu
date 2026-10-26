import asyncio, json, os, queue
import sounddevice as sd
import websockets

KEY = os.environ["GNANI_API_KEY"].strip()
URL = "wss://api.vachana.ai/stt/v3/stream"
RATE = 16000
FRAME = 512

q = queue.Queue()

def cb(indata, frames, t, status):
    q.put(bytes(indata))

async def main():
    headers = {
        "x-api-key-id": KEY,
        "lang_code": "hi-IN",
        "x-sample-rate": str(RATE),
        "x-vad-threshold": "0.5",
        "x-min-silence-ms": "700",
    }
    async with websockets.connect(URL, additional_headers=headers) as ws:
        print("connected - speak Hindi, Ctrl+C to stop")

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
                if d["type"] == "transcript":
                    print(f"[{d['latency']}ms] {d['text']}")
                elif d["type"] == "connected":
                    print("ready")

        await asyncio.gather(send(), recv())

asyncio.run(main())
