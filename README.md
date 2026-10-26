# SamaSetu

Live speech-to-speech translation between Indian languages, preserving the
speaker's own voice. Hindi in, Tamil out, in roughly 1.5 seconds.

Built for the Great Indian AI Internship Challenge 2026.

## Why

Most translation between Indian languages routes through English. Hindi is
SOV, English is SVO, Tamil is SOV, so pivoting crosses the word-order
boundary twice. Direct Indic-to-Indic translation stays inside one word
order - which matters when the system has to start speaking before the
sentence is finished.

## Pipeline

| Stage | Model | Measured |
| --- | --- | --- |
| Speech to text | Gnani Prisma v2.5 (realtime) | ~110 ms per segment |
| Translation | AI4Bharat IndicTrans2 320M | ~395 ms greedy |
| Speech out | Gnani Timbre, cloned voice | ~407 ms to first audio |

Total to first sound: about 1.5 s, on CPU.

## Running it

    pip install -r requirements.txt
    $env:GNANI_API_KEY="your-key"
    python embed.py        # build a voice embedding from ref.wav
    python samasetu.py     # live Hindi to Tamil

Two-way mode runs one process per side:

    python twoway.py hi
    python twoway.py ta

## Status

System works end to end. Benchmark and evaluation in progress.
