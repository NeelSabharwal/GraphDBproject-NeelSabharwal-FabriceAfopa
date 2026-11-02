"""Execute the demo without committing private outputs or replacing its source."""

import os
from pathlib import Path

import nbformat
from nbclient import NotebookClient


def main():
    """Use real local services; save even failed execution for honest diagnosis."""
    os.environ.setdefault("DEMO_API_URL", "http://api:8000")
    notebook = nbformat.read("demo.ipynb", as_version=4)
    output = Path("data/processed/demo.executed.ipynb")
    output.parent.mkdir(parents=True, exist_ok=True)
    try:
        NotebookClient(notebook, timeout=360, kernel_name="python3").execute()
    finally:
        nbformat.write(notebook, output)
    print(f"Executed {len(notebook.cells)} cells; authentic output saved to {output}")


if __name__ == "__main__":
    main()
