import sys
import os

# Patch path to include user site-packages
sys.path.insert(0, r"C:\Users\ASMIT\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0\LocalCache\local-packages\Python313\site-packages")
sys.path.append(os.path.join(os.path.dirname(__file__), "backend"))

import uvicorn

if __name__ == "__main__":
    print("Starting Uvicorn via runner script...")
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True, app_dir="backend")
