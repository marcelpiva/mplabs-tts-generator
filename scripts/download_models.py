#!/usr/bin/env python3
"""Download F5-TTS model weights from HuggingFace.

This is a thin wrapper around `mplabs-tts download-models` for users who'd
rather invoke a script directly than the CLI. Both do the same thing.

Examples:
    python scripts/download_models.py                       # base F5-TTS
    python scripts/download_models.py --variant ptbr-multispeaker
    python scripts/download_models.py --repo myorg/myrepo --filename model.safetensors
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


VARIANTS = {
    "base": "SWivid/F5-TTS",
    "ptbr-multispeaker": "Tharyck/multispeaker-ptbr-f5tts",
    "ptbr-firstpixel": "FirstPixel/F5-TTS-pt-br",
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--variant", choices=list(VARIANTS), default="base",
                        help="Convenience preset for known repos.")
    parser.add_argument("--repo", default=None,
                        help="HuggingFace repo (overrides --variant).")
    parser.add_argument("--filename", default=None,
                        help="Specific file to download (otherwise the full snapshot).")
    parser.add_argument("--output-dir", "-o", default="./models",
                        help="Where to put the downloaded files (default: ./models).")
    args = parser.parse_args()

    try:
        from huggingface_hub import hf_hub_download, snapshot_download
    except ImportError:
        print("huggingface_hub not installed. Run: pip install huggingface_hub", file=sys.stderr)
        return 1

    repo = args.repo or VARIANTS[args.variant]
    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)

    print(f"Downloading from {repo} → {out}")
    if args.filename:
        path = hf_hub_download(repo_id=repo, filename=args.filename, local_dir=str(out))
        print(f"Downloaded: {path}")
    else:
        path = snapshot_download(repo_id=repo, local_dir=str(out))
        print(f"Downloaded snapshot to: {path}")

    print()
    print("Next steps:")
    print(f"  export MPLABS_TTS_MODEL={out}/model_last.safetensors")
    print(f"  export MPLABS_TTS_VOCAB={out}/vocab.txt")
    print("  mplabs-tts synth 'Olá mundo' -o /tmp/test.mp3")
    return 0


if __name__ == "__main__":
    sys.exit(main())
