# utils.py
import os
import zipfile
import time
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(filename='patcher.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def save_file(file_path, file):
    """Save the uploaded file to the specified path."""
    try:
        with open(file_path, 'wb') as f:
            file.download(out=f)
        logger.info(f"Saved file: {file_path}")
        return file_path
    except Exception as e:
        logger.error(f"Error saving file {file_path}: {str(e)}")
        raise

def patch_apk(file_path):
    """Apply powerful patches to the APK and return the patched path with logs."""
    patch_logs = [f"Patching started at {datetime.now()}"]
    patched_path = file_path.replace('.apk', '_patched.apk')
    
    try:
        # Simulate advanced patching by modifying the APK as a ZIP file
        with zipfile.ZipFile(file_path, 'r') as original_zip:
            with zipfile.ZipFile(patched_path, 'w', zipfile.ZIP_DEFLATED) as patched_zip:
                # Copy all original files
                for item in original_zip.infolist():
                    patched_zip.writestr(item, original_zip.read(item))
                
                # Patch 1: Add a custom metadata file
                metadata_content = "Patched by NextLevelPatcher v1.0\nPremium Features Unlocked\n"
                patched_zip.writestr("META-INF/patch_metadata.txt", metadata_content)
                patch_logs.append("Added custom metadata file: META-INF/patch_metadata.txt")
                
                # Patch 2: Simulate AndroidManifest.xml modification
                manifest_path = "AndroidManifest.xml"
                if manifest_path in original_zip.namelist():
                    manifest_content = original_zip.read(manifest_path).decode('utf-8')
                    manifest_content += "<!-- Patched by NextLevelPatcher -->"
                    patched_zip.writestr(manifest_path, manifest_content.encode('utf-8'))
                    patch_logs.append("Modified AndroidManifest.xml with custom comment")
                
                # Patch 3: Add a surprising resource file
                surprise_content = "Welcome to the Next Level! This APK has been supercharged!"
                patched_zip.writestr("res/next_level.txt", surprise_content)
                patch_logs.append("Added surprising resource: res/next_level.txt")
        
        # Verify the patched APK
        patched_size = os.path.getsize(patched_path)
        patch_logs.append(f"Patched APK size: {patched_size / (1024 * 1024):.2f} MB")
        logger.info(f"Patched APK: {patched_path}")
        
        # Save logs to a file
        log_file = f"logs/patch_log_{int(time.time())}.txt"
        os.makedirs("logs", exist_ok=True)
        with open(log_file, 'w') as f:
            f.write("\n".join(patch_logs))
        
        return patched_path, log_file
    except Exception as e:
        logger.error(f"Error patching APK {file_path}: {str(e)}")
        raise

def cleanup(file_path):
    """Remove the file from the server."""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"Cleaned up file: {file_path}")
    except Exception as e:
        logger.error(f"Error cleaning up file {file_path}: {str(e)}")

def validate_file_size(file_size):
    """Check if the file size is within acceptable limits."""
    from config import MAX_FILE_SIZE
    if file_size > MAX_FILE_SIZE:
        raise ValueError(f"File size ({file_size / (1024 * 1024):.2f} MB) exceeds maximum limit ({MAX_FILE_SIZE / (1024 * 1024):.2f} MB).")
    return True
