"""Small Make helpers that never delete corpus data, credentials or artifacts."""

import argparse
from pathlib import Path
import shutil


def main():
    """Clean only known caches or print a bounded source tree."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["clean", "tree"])
    args = parser.parse_args()
    roots = [Path(name) for name in ("app", "scripts", "tests")]
    if args.command == "clean":
        caches = [p for root in roots for p in root.rglob("__pycache__")]
        caches += [Path(".pytest_cache")]
        for path in caches:
            if path.is_dir() and not path.is_symlink():
                shutil.rmtree(path)
        print("Removed source/test caches; data, models, .venv and credentials preserved.")
        return
    excluded = {".git", ".venv", "__pycache__", ".pytest_cache", "raw", "processed"}

    def show(root, depth):
        for path in sorted(root.iterdir()):
            if path.name in excluded or path.name.startswith(".env"):
                continue
            print("  " * depth + path.name + ("/" if path.is_dir() else ""))
            if path.is_dir() and not path.is_symlink() and depth < 2:
                show(path, depth + 1)

    show(Path("."), 0)


if __name__ == "__main__":
    main()
