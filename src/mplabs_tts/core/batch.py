"""Batch runner with resume + manifest support."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Iterable

from mplabs_tts.core.models import TTSItem
from mplabs_tts.core.pipeline import TTSPipeline


class BatchRunner:
    """Runs a `TTSPipeline` over many items with progress + manifest tracking.

    Output layout:
        output_dir/
            <item_id>.mp3        # one per item
            progress.json        # resume state
            manifest.json        # what was generated, with metadata + durations
    """

    def __init__(self, pipeline: TTSPipeline, output_dir: str | Path):
        self.pipeline = pipeline
        self.output_dir = Path(output_dir)
        self.progress_file = self.output_dir / "progress.json"
        self.manifest_file = self.output_dir / "manifest.json"

    # --- progress -----------------------------------------------------------

    def _load_progress(self) -> dict:
        if self.progress_file.exists():
            with open(self.progress_file) as f:
                return json.load(f)
        return {"generated": {}}

    def _save_progress(self, progress: dict) -> None:
        self.progress_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.progress_file, "w") as f:
            json.dump(progress, f, indent=2, ensure_ascii=False)

    # --- runner -------------------------------------------------------------

    def run(
        self,
        items: Iterable[TTSItem],
        force: bool = False,
        seed: int = 42,
        as_mp3: bool = True,
    ) -> dict:
        """Synthesize all items. Skips ones already in progress.json unless `force`."""
        items = list(items)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        progress = self._load_progress()

        if force:
            for item in items:
                progress["generated"].pop(item.id, None)
            self._save_progress(progress)

        to_do = [it for it in items if it.id not in progress["generated"]]
        already = len(items) - len(to_do)
        total = len(to_do)

        if total == 0:
            print(f"All {len(items)} items already generated.")
            self._write_manifest(items, progress)
            return progress

        print(f"Generating {total} item(s) ({already} already done) → {self.output_dir}")
        ext = ".mp3" if as_mp3 else ".wav"
        start = time.time()

        for i, item in enumerate(to_do, 1):
            elapsed = time.time() - start
            rate = i / max(elapsed, 1)
            eta = (total - i) / max(rate, 0.001)
            eta_h, eta_m = int(eta // 3600), int((eta % 3600) // 60)
            print(f"[{i}/{total}] {item.id} (ETA {eta_h}h{eta_m:02d}m) ", end="", flush=True)

            try:
                out_path = self.output_dir / f"{item.id}{ext}"
                result = self.pipeline.synthesize(item, out_path, seed=seed, as_mp3=as_mp3)
                progress["generated"][item.id] = {
                    "duration_s": result.duration_s,
                    "gen_time_s": result.gen_time_s,
                    "metadata": item.metadata,
                }
                self._save_progress(progress)
                print(f"OK {result.gen_time_s:.0f}s gen, {result.duration_s:.1f}s audio", flush=True)
            except Exception as e:
                print(f"ERROR: {e}", flush=True)

        self._write_manifest(items, progress)
        done = len(progress["generated"])
        print(f"\nDone. {done}/{len(items)} items in {self.output_dir}")
        print(f"Manifest: {self.manifest_file}")
        return progress

    def _write_manifest(self, items: list[TTSItem], progress: dict) -> None:
        manifest = {
            "total_items": len(items),
            "generated": len(progress["generated"]),
            "items": [
                {
                    "id": item.id,
                    "file": f"{item.id}.mp3",
                    "metadata": item.metadata,
                    **progress["generated"].get(item.id, {}),
                }
                for item in items
                if item.id in progress["generated"]
            ],
        }
        self.manifest_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.manifest_file, "w") as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)
