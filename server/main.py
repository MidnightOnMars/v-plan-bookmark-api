import sys, os, glob, importlib.util
root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, root)
app = None
for pattern in ["server_impl.py", "*impl*.py", "*server*.py", "*bookmark*.py"]:
    matches = glob.glob(os.path.join(root, pattern))
    matches = [
        m for m in matches
        if os.path.basename(m) not in ("__init__.py", "main.py")
    ]
    if matches:
        spec = importlib.util.spec_from_file_location("_impl", matches[0])
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        if hasattr(mod, "app"):
            app = mod.app
            break
if app is None:
    raise ImportError("No implementation file with 'app' found in server/")
