# Reference Voices

F5-TTS clones the voice in the reference WAV when synthesizing — there's no
training step. To get good results you need:

- **5 to 15 seconds** of clear, single-speaker audio
- **No background noise / music**
- **Mono** (or stereo with both channels carrying the same speaker)
- **A matching transcript** of *exactly* what the speaker says, in the same
  language you'll synthesize

Pair each WAV with a `.txt` file of the same basename containing the
transcript. The CLI reads it via `--voice-text "$(cat voices/<name>.txt)"`,
or you can set `MPLABS_TTS_VOICE_TEXT` directly.

## Bundled samples

| File | Voice | Transcript |
|------|-------|-----------|
| `male_narrator.wav` | Male, narrator timbre, pt-BR | see `male_narrator.txt` |
| `female_narrator.wav` | Female, narrator timbre, pt-BR | see `female_narrator.txt` |

These ship as starting points for pt-BR — swap them for your own recordings
when you want a specific voice. For best results record at 24 kHz mono in a
quiet room.

## Adding a new voice

```bash
# 1. Drop the file
cp my_voice.wav voices/my_voice.wav

# 2. Write the transcript verbatim
echo "your spoken text here" > voices/my_voice.txt

# 3. Use it
mplabs-tts synth "Olá, mundo." \
    --voice voices/my_voice.wav \
    --voice-text "$(cat voices/my_voice.txt)" \
    -o /tmp/out.mp3
```

## Where to find more pt-BR voices

- [Tharyck/multispeaker-ptbr-f5tts](https://huggingface.co/Tharyck/multispeaker-ptbr-f5tts)
- [FirstPixel/F5-TTS-pt-br](https://huggingface.co/FirstPixel/F5-TTS-pt-br)
