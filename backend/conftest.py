import sys
import os
from pathlib import Path

# Add the project root to the python path
root_dir = Path(__file__).resolve().parent
sys.path.append(str(root_dir))
