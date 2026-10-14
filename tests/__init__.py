from importlib.util import find_spec
import sys
from pathlib import Path


if find_spec("typesafe_decisions") is None:
    project_root = Path(__file__).resolve().parents[1]
    source_root = project_root / "src"
    sys.path.insert(0, str(source_root))

    for site_packages in (project_root / ".venv" / "lib").glob(
        "python*/site-packages"
    ):
        sys.path.append(str(site_packages))
