"""Import the chapter-prefixed FastAPI module from its file path."""

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path


MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "scripts"
    / "python"
    / "05-serving-predictions-api.py"
)
SPEC = spec_from_file_location("chapter_05_api", MODULE_PATH)

if SPEC is None or SPEC.loader is None:
    raise ImportError(f"Could not load API module from {MODULE_PATH}")

api_module = module_from_spec(SPEC)
SPEC.loader.exec_module(api_module)

app = api_module.app

