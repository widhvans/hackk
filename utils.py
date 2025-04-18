# utils.py
import os

def save_file(file_path, file):
    """Save the uploaded file to the specified path."""
    with open(file_path, 'wb') as f:
        file.download(out=f)
    return file_path

def patch_apk(file_path):
    """Simulate patching the APK file (replace with actual patching logic)."""
    # For demo purposes, just create a new file with a modified name
    patched_path = file_path.replace('.apk', '_patched.apk')
    with open(file_path, 'rb') as original, open(patched_path, 'wb') as patched:
        patched.write(original.read())  # Copy content (simulate patching)
    return patched_path

def cleanup(file_path):
    """Remove the file from the server."""
    if os.path.exists(file_path):
        os.remove(file_path)
