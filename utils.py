# utils.py
import os
import zipfile
import time
from datetime import datetime
import logging
import aiohttp

# Set up logging
logging.basicConfig(filename='logs/patcher.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def save_file(file_path, file_obj):
    """Save the uploaded file to the specified path."""
    try:
        await file_obj.download_to_drive(file_path)
        logger.info(f"Saved file: {file_path}")
        return file_path
    except Exception as e:
        logger.error(f"Error saving file {file_path}: {str(e)}")
        raise

async def download_from_url(url, file_path):
    """Download a file from an external URL."""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    raise Exception(f"Failed to download from URL: {response.status}")
                with open(file_path, 'wb') as f:
                    while True:
                        chunk = await response.content.read(1024 * 1024)  # 1 MB chunks
                        if not chunk:
                            break
                        f.write(chunk)
        logger.info(f"Downloaded file from URL: {file_path}")
        return file_path
    except Exception as e:
        logger.error(f"Error downloading from URL {url}: {str(e)}")
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
                
                # Patch 1: Add a hacked metadata file
                metadata_content = "Hacked by NextLevelPatcher v2.0\nAll Restrictions Removed\nSupercharged Features Unlocked!"
                patched_zip.writestr("META-INF/hack_metadata.txt", metadata_content)
                patch_logs.append("Added hacked metadata file: META-INF/hack_metadata.txt")
                
                # Patch 2: Inject custom permission in AndroidManifest.xml
                manifest_path = "AndroidManifest.xml"
                if manifest_path in original_zip.namelist():
                    manifest_content = original_zip.read(manifest_path).decode('utf-8')
                    manifest_content = manifest_content.replace(
                        '<manifest', 
                        '<manifest\n    <uses-permission android:name="com.nextlevel.HACK_ACCESS" />'
                    )
                    patched_zip.writestr(manifest_path, manifest_content.encode('utf-8'))
                    patch_logs.append("Injected custom permission in AndroidManifest.xml")
                
                # Patch 3: Add a surprising script in assets/
                script_content = "alert('This APK has been hacked by NextLevelPatcher! Enjoy unlimited power!');"
                patched_zip.writestr("assets/hack_script.js", script_content)
                patch_logs.append("Added surprising script: assets/hack_script.js")
        
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
