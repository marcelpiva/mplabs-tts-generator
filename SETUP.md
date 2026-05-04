# Setup do zero — `mplabs-tts-generator`

Guia para configurar e rodar smoke tests do projeto numa máquina nova (ou
quando a sessão é reiniciada). Tempo estimado: ~15 minutos no primeiro
setup; ~1 minuto se reaproveitar o modelo já baixado.

## 0. Pré-requisitos

| Requisito | Versão | Como instalar (macOS) |
|---|---|---|
| Python | **3.11** (3.10–3.12 ok; 3.14 NÃO funciona — torch/f5-tts sem wheels) | `brew install python@3.11` ou via `pyenv install 3.11.10` |
| ffmpeg | qualquer versão recente | `brew install ffmpeg` |
| git | qualquer | já vem no macOS |
| Disco livre | ~5 GB | (modelo F5-TTS ~1.3 GB + torch ~3 GB) |
| GPU | Apple Silicon (MPS) ou NVIDIA CUDA — CPU funciona, mas é ~10× mais lento | — |

Verificações:

```bash
python3.11 --version    # deve mostrar 3.11.x
ffmpeg -version | head -1
```

## 1. Clonar o repo

```bash
cd ~/Projects
git clone https://github.com/marcelpiva/mplabs-tts-generator.git
cd mplabs-tts-generator
```

## 2. Criar virtualenv com Python 3.11

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
```

(Se aparecer aviso sobre `pip`, ignore.)

## 3. Instalar dependências

Modo completo (inclui `f5-tts` + torch — ~10 min de download):

```bash
pip install -e ".[dev]"
```

Se só quiser rodar testes/CLI sem síntese de áudio (mais rápido):

```bash
pip install -e . --no-deps
pip install click numpy soundfile pytest huggingface_hub pydub
```

Validar instalação:

```bash
mplabs-tts --help
pytest                    # 55 testes devem passar em ~0.1s
```

## 4. Obter o modelo F5-TTS

**Opção A — Reaproveitar o modelo já baixado** (instantâneo, recomendado se
você tem o workspace `cocada3301-workspace/`):

```bash
mkdir -p models
ln -s ~/Projects/cocada3301-workspace/tools/tts-generator/models/model_last.safetensors models/model_last.safetensors
ln -s ~/Projects/cocada3301-workspace/tools/tts-generator/models/vocab.txt models/vocab.txt
ls -la models/    # deve mostrar 2 symlinks
```

**Opção B — Baixar do HuggingFace** (~1.3 GB, 5–15 min):

```bash
python scripts/download_models.py --variant base
# ou para fine-tune pt-BR:
python scripts/download_models.py --variant ptbr-multispeaker
```

## 5. Configurar variáveis de ambiente

Crie `.env` (não vai pro git — está no `.gitignore`):

```bash
cp .env.example .env
```

Edite `.env` confirmando os caminhos. Defaults bons para macOS Apple Silicon:

```bash
MPLABS_TTS_MODEL=./models/model_last.safetensors
MPLABS_TTS_VOCAB=./models/vocab.txt
MPLABS_TTS_VOICE=./voices/male_narrator.wav
MPLABS_TTS_VOICE_TEXT="é muito emocionante os homens se encontrarem à noite no bosque"
MPLABS_TTS_DEVICE=mps
```

Carregar no shell atual:

```bash
set -a; source .env; set +a
```

(Para CUDA, troque `mps` por `cuda`. Para CPU, `cpu`.)

## 6. Smoke tests

### 6.1 Normalização (rápido — não carrega modelo)

```bash
mplabs-tts normalize "O 1o passo custa R\$ 1.500 e voce esta vendo a operacao."
```

Esperado: ordinais, currency e acentos corrigidos.

```bash
mplabs-tts normalize "A cocada e o coco" --plugin coconut3301
```

Esperado: `A cocáda e o côco`.

```bash
mplabs-tts normalize "Administre 500 mg b.i.d." --plugin medical_ptbr
```

Esperado: `Administre quinhentos miligramas duas vezes ao dia.`

### 6.2 Síntese single (carrega modelo — ~30s na 1ª vez)

```bash
mplabs-tts synth "Olá, mundo. Hoje é cinco de maio de 2026 e o teste do mplabs-tts está rodando." \
    -o /tmp/smoke.mp3
open /tmp/smoke.mp3      # macOS — abre no QuickTime
```

Esperado: MP3 ~5–8s de áudio, voz masculina pt-BR clara.

### 6.3 Batch + resume + manifest

```bash
mplabs-tts batch examples/batch_input.json -o /tmp/batch_out
ls /tmp/batch_out/
# Esperado: 4 mp3s + progress.json + manifest.json

# Roda de novo — deve ser no-op (testa resume)
mplabs-tts batch examples/batch_input.json -o /tmp/batch_out
# Esperado: "All 4 items already generated."

# Abrir os MP3s
open /tmp/batch_out/*.mp3

# Inspecionar o manifest
cat /tmp/batch_out/manifest.json | python -m json.tool
```

### 6.4 Batch com plugin Coconut

```bash
mplabs-tts batch examples/batch_input.json \
    -o /tmp/coconut_out \
    --plugin coconut3301

# Sintetizar especificamente um exemplo com cocada/coco
echo '[{"id":"cocada_test","text":"A cocada e o coco do cartel."}]' > /tmp/cocada.json
mplabs-tts batch /tmp/cocada.json -o /tmp/coconut_out --plugin coconut3301
open /tmp/coconut_out/cocada_test.mp3
```

Validação acústica: ouvir se "cocada" sai como **cocáda** (tônica em "ca",
não em "co") e "coco" como **côco** (vogal fechada).

### 6.5 Plugin médico

```bash
echo '[{"id":"med_test","text":"Paciente com 38 graus, prescrever 500 mg de paracetamol b.i.d. via VO."}]' > /tmp/med.json
mplabs-tts batch /tmp/med.json -o /tmp/med_out --plugin medical_ptbr
open /tmp/med_out/med_test.mp3
```

Esperado no áudio: "duas vezes ao dia", "via oral", "miligramas" — não as
abreviações cruas.

## 7. Critérios de sucesso

- [ ] `pytest` passa 55/55 em ~0.1s
- [ ] `mplabs-tts normalize` produz texto normalizado correto
- [ ] `mplabs-tts synth` gera MP3 audível em <60s (MPS) ou <300s (CPU)
- [ ] Batch gera N MP3s + `progress.json` + `manifest.json`
- [ ] 2ª execução do batch não regenera nada
- [ ] Plugin Coconut altera pronúncia de "cocada/coco" no áudio
- [ ] Plugin médico expande "b.i.d.", "VO", "mg" no áudio

## 8. Troubleshooting

**`No module named 'f5_tts'`** → instale com `pip install -e ".[dev]"` (não
foi `--no-deps`).

**`ffmpeg not found on PATH`** → `brew install ffmpeg`.

**Áudio com glitches/ruído** → a voz de referência pode estar com ruído.
Tente `--voice voices/female_narrator.wav --voice-text "$(cat voices/female_narrator.txt)"`.

**MPS out-of-memory** → fallback `MPLABS_TTS_DEVICE=cpu`. Geração fica
lenta (~10–20s por frase) mas funciona.

**Python 3.14 / wheels não encontrados** → torch ainda não tem wheels para
3.14. Use 3.11.

**Modelo gigante (~1.3 GB) demorando para baixar** → use a Opção A (symlink
do workspace existente).

## 9. Próximos passos (não-smoke-test)

- Refatorar `coconut3301-workspace/tools/tts-generator/generate_coconut.py`
  para importar `mplabs_tts` em vez de duplicar o pipeline.
- Adicionar GitHub Actions: lint (`ruff`) + `pytest` em PRs.
- Publicar no PyPI (`python -m build && twine upload dist/*`).
- Adicionar módulo de inglês (`languages/en/`) seguindo o padrão de
  `languages/pt_br/`.
