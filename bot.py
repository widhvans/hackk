# bot.py
import os
import re
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
from telegram.error import BadRequest
from config import BOT_TOKEN, DOWNLOAD_DIR
from utils import save_file, patch_apk, cleanup, download_from_url
import logging

# Set up logging
logging.basicConfig(filename='logs/bot.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /start command."""
    await update.message.reply_text(
        "Welcome to NextLevelPatcher! Send me an APK file or a URL to a large APK (>20 MB). I'll patch it with mind-blowing enhancements!"
    )

async def handle_apk(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle APK file uploads or URLs."""
    message = update.message

    # Check if a URL is provided
    if message.text and re.match(r'https?://', message.text):
        await message.reply_text(f"Received URL: {message.text}. Downloading...")
        file_path = f"{DOWNLOAD_DIR}/downloaded_apk_{int(time.time())}.apk"
        os.makedirs(DOWNLOAD_DIR, exist_ok=True)
        
        try:
            saved_path = await download_from_url(message.text, file_path)
            await process_apk(saved_path, message)
        except Exception as e:
            logger.error(f"Error processing URL {message.text}: {str(e)}")
            await message.reply_text(f"Error downloading or processing the APK: {str(e)}")
            cleanup(file_path)
        return

    # Check if a file is uploaded
    file = message.document
    if not file or not file.file_name.endswith('.apk'):
        await message.reply_text("Please send a valid .apk file or a URL to an APK.")
        return

    await message.reply_text(f"Received {file.file_name} ({file.file_size / (1024 * 1024):.2f} MB). Processing...")

    # Download the file
    file_path = f"{DOWNLOAD_DIR}/{file.file_name}"
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    
    try:
        file_obj = await file.get_file()
        saved_path = await save_file(file_path, file_obj)
        await process_apk(saved_path, message)
    except BadRequest as e:
        logger.error(f"Telegram BadRequest error: {str(e)}")
        if "file is too big" in str(e).lower():
            await message.reply_text(
                "The file is too large for direct upload. Please upload it to a cloud service (e.g., Google Drive) and send the URL."
            )
        else:
            await message.reply_text(f"Error: {str(e)}. Try again or contact support.")
        cleanup(file_path)
    except Exception as e:
        logger.error(f"Error processing APK {file.file_name}: {str(e)}")
        await message.reply_text(f"Error processing the APK: {str(e)}")
        cleanup(file_path)

async def process_apk(saved_path, message):
    """Process the APK and send the patched version with logs."""
    try:
        # Patch the APK
        patched_path, log_file = patch_apk(saved_path)

        # Send the patched APK back
        with open(patched_path, 'rb') as patched_file:
            await message.reply_document(
                document=patched_file,
                filename=os.path.basename(patched_path),
                caption="Your patched APK is ready! Check the logs for epic details. 🚀"
            )

        # Send the patch logs
        with open(log_file, 'rb') as log:
            await message.reply_document(
                document=log,
                filename=os.path.basename(log_file),
                caption="Patch logs for your APK"
            )

        await message.reply_text("Patched APK and logs sent successfully! Enjoy the next-level experience!")

        # Clean up
        cleanup(saved_path)
        cleanup(patched_path)
        cleanup(log_file)

    except Exception as e:
        logger.error(f"Error in process_apk: {str(e)}")
        raise

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors globally."""
    logger.error(f"Update {update} caused error: {context.error}")
    if update and update.message:
        await update.message.reply_text("An unexpected error occurred. Please try again or contact support.")

def main():
    """Run the bot."""
    application = Application.builder().token(BOT_TOKEN).build()

    # Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.Document.ALL | filters.TEXT, handle_apk))
    application.add_error_handler(error_handler)

    # Start the bot
    logger.info("Bot is running...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
