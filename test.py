import importlib
import glob

files = glob.glob("app_pages/*.py") + glob.glob("utility/*.py")

for file in files:
    module = file[:-3].replace("\\", ".").replace("/", ".")

    if module.endswith(".__init__"):
        continue

    try:
        importlib.import_module(module)
        print("✅", module)
    except Exception as e:
        print("❌", module)
        print("   ", type(e).__name__, ":", e)