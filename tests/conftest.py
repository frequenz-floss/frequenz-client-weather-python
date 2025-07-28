# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Add src directory to the path for tests."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
