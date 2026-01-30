import sys
import os

# Hack to finding packages installed in user location
sys.path.insert(0, r"C:\Users\ASMIT\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0\LocalCache\local-packages\Python313\site-packages")

import fitz

doc = fitz.open()
page = doc.new_page()
page.insert_text((100, 100), "This is a test PDF for visualization.\nLines for chunking.\nMore text.", fontsize=20)
doc.save("frontend_test.pdf")
print("PDF generated: frontend_test.pdf")
