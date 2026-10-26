import os, requests

KEY = os.environ["GNANI_API_KEY"].strip()

r = requests.post(
    "https://api.vachana.ai/api/v1/tts/inference",
    headers={"X-API-Key-ID": KEY, "Content-Type": "application/json"},
    json={
        "text": "मुझे कल सुबह दस बजे आपसे मिलना है।",
        "voice": "Nalini",
        "model": "timbre-v2.5",
        "language": "hi-IN",
        "speed": 1.0,
        "audio_config": {"sample_rate": 48000, "num_channels": 1,
                         "sample_width": 2, "encoding": "linear_pcm",
                         "container": "wav"},
    },
)

print(r.status_code)
if r.status_code == 200:
    open("test.wav", "wb").write(r.content)
    print("saved", len(r.content), "bytes")
else:
    print(r.text)
