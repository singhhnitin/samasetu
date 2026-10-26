import soundfile as sf

raw = open("ref.mp3", "rb").read()[:950000]
open("ref_trim.mp3", "wb").write(raw)

data, sr = sf.read("ref_trim.mp3")
if data.ndim > 1:
    data = data.mean(axis=1)
data = data[: int(sr * 20)]
sf.write("ref.wav", data, sr, subtype="PCM_16")
print("ok", round(len(data) / sr, 1), "seconds at", sr, "Hz")
