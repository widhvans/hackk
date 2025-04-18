# bot.py
import os
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
from utils import save_file, patch_apk, cleanup, validate_file_size
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /start command."""
    await update.message.reply_text("Welcome to NextLevelPatcher! Send me an APK file, and I'll patch it with surprising enhancements!")

async def handle_apk(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle APK file uploads."""
    message = update.message
    file = message.document

    # Check if the file is an APK
    if not file.file_name.endswith('.apk'):
        await message.reply_text("Please send a valid .apk file.")
        return

    # Validate file size
    try:
        validate_file_size(file.file_size)
    except ValueError as e:
        await message.reply_text(str(e) + " Consider upgrading to Bot API Premium or splitting the file.")
        logger.warning(f"File too big: {file.file_name}, size: {file.file_size}")
        return

    await message.reply_text(f"Received {file.file_name} ({file.file_size / (1024 * 1024):.2f} MB). Processing...")

    # Download the file
    file_obj = await file.get_file()
    file_path = f"{DOWNLOAD_DIR}/{file.file_name}"
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    
    try:
        saved_path = save_file(file_path, file_obj)

        # Patch the APK
        patched_path, log_file = patch_apk(saved_path)

        # Send the patched APK back
        with open(patched_path, 'rb') as patched_file:
            await message.reply_document(
                document=patched_file,
                filename=os.path.basename(patched_path),
                caption="Your patched APK is ready! Check the logs for details."
            )

        # Send the patch logs
        with open(log_file, 'rb') as log:
            await message.reply_document(
                document=log,
                filename=os.path.basename(log_file),
                caption="Patch logs for your APK"
            )

        await message.reply_text("Patched APK and logs sent successfully! 🚀")

        # Clean up
        cleanup(saved_path)
        cleanup(patched_path)
        cleanup(log_file)

    except BadRequest as e:
        logger.error(f"Telegram BadRequest error: {str(e)}")
        await message.reply_text(f"Error: {str(e)}. Try a smaller file or contact support.")
        cleanup(file_path)
    except Exception as e:
        logger.error(f"Error processing APK {file.file_name}: {str(e)}")
        await message.reply_text(f"Error processing the APK: {str(e)}")
        cleanup(file_path)

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
    application.add_handler(MessageHandler(filters.Document.ALL, handle_apk))
    application.add_error_handler(error_handler)

    # Start the bot
    logger.info("Bot is running...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
