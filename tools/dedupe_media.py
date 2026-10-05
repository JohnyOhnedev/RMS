"""Deduplicate media/resumes: keep one copy per unique document.

Safety model:
  1. Read-only inventory; print the plan. No deletions in this phase.
  2. Group by SHA-256 of file CONTENT (not name).
  3. Keep the copy with the shortest/original-looking name; everything else is
     a duplicate.
  4. Only deletes files that are byte-identical to a file being kept.

Usage:
    python tools/dedupe_media.py            # dry run (default)
    python tools/dedupe_media.py --apply    # actually delete
"""

import hashlib
import sys
from collections import defaultdict
from pathlib import Path

MEDIA = Path(__file__).resolve().parent.parent / "media"
APPLY = "--apply" in sys.argv


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def keeper_rank(path: Path):
    """Lower is better. Prefer the un-suffixed original name.

    Django appends a random 7-char suffix (``name_AbC1234.pdf``) on collision,
    so the cleanest name is the one whose stem has no trailing ``_XXXXXXX``.
    """
    stem = path.stem
    has_suffix = len(stem) > 8 and stem[-8] == "_" and stem[-7:].isalnum()
    return (1 if has_suffix else 0, len(path.name), path.name)


def main() -> int:
    if not MEDIA.is_dir():
        print(f"media dir not found: {MEDIA}")
        return 1

    files = [p for p in MEDIA.rglob("*") if p.is_file()]
    print(f"Scanning {len(files)} files under {MEDIA}\n")

    by_hash: dict[str, list[Path]] = defaultdict(list)
    for path in files:
        by_hash[sha256(path)].append(path)

    duplicates: list[Path] = []
    keepers: list[Path] = []
    bytes_before = 0
    bytes_after = 0

    for digest, group in sorted(by_hash.items(), key=lambda kv: -len(kv[1])):
        group.sort(key=keeper_rank)
        keep, dupes = group[0], group[1:]
        keepers.append(keep)
        duplicates.extend(dupes)
        bytes_before += sum(p.stat().st_size for p in group)
        bytes_after += keep.stat().st_size
        if dupes:
            print(f"{len(group):>3} copies  ({keep.stat().st_size:>7} B each)  keep: {keep.name}")
            for d in dupes[:3]:
                print(f"           drop: {d.relative_to(MEDIA)}")
            if len(dupes) > 3:
                print(f"           ... and {len(dupes) - 3} more")

    print("\n" + "=" * 60)
    print(f"unique documents : {len(keepers)}")
    print(f"files now        : {len(files)}")
    print(f"duplicates       : {len(duplicates)}")
    print(f"bytes before     : {bytes_before / 1024 / 1024:.1f} MB")
    print(f"bytes after      : {bytes_after / 1024 / 1024:.1f} MB")
    print(f"reclaimable      : {(bytes_before - bytes_after) / 1024 / 1024:.1f} MB")
    print("=" * 60)

    # Verify every file marked for deletion is byte-identical to its keeper.
    mismatches = 0
    for digest, group in by_hash.items():
        group.sort(key=keeper_rank)
        keep = group[0]
        for d in group[1:]:
            if sha256(d) != sha256(keep):
                mismatches += 1
                print(f"ABORT: {d} does not match keeper {keep}")
    if mismatches:
        print(f"\n{mismatches} mismatch(es) detected - refusing to delete anything.")
        return 1
    print("Integrity check: every file marked for deletion is byte-identical to its keeper.")

    if not APPLY:
        print("\nDRY RUN - nothing deleted. Re-run with --apply to delete.")
        return 0

    freed = 0
    for d in duplicates:
        freed += d.stat().st_size
        d.unlink()
    print(f"\nDeleted {len(duplicates)} duplicate files, freed {freed / 1024 / 1024:.1f} MB.")
    print(f"Files remaining: {sum(1 for p in MEDIA.rglob('*') if p.is_file())}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
