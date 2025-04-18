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
from config import BOT_TOKEN
from utils import save_file, patch_apk, cleanup

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /start command."""
    await update.message.reply_text("Welcome! Send me an APK file, and I'll patch it for you.")

async def handle_apk(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle APK file uploads."""
    message = update.message
    file = message.document

    # Check if the file is an APK
    if not file.file_name.endswith('.apk'):
        await message.reply_text("Please send a valid .apk file.")
        return

    await message.reply_text("Received your APK. Processing...")

    # Download the file
    file_obj = await file.get_file()
    file_path = f"downloads/{file.file_name}"
    os.makedirs("downloads", exist_ok=True)
    saved_path = save_file(file_path, file_obj)

    try:
        # Patch the APK
        patched_path = patch_apk(saved_path)

        # Send the patched APK back
        with open(patched_path, 'rb') as patched_file:
            await message.reply_document(document=patched_file, filename=os.path.basename(patched_path))
        await message.reply_text("Patched APK sent successfully!")

        # Clean up
        cleanup(saved_path)
        cleanup(patched_path)

    except Exception as e:
        await message.reply_text(f"Error processing the APK: {str(e)}")
        cleanup(saved_path)

def main():
    """Run the bot."""
    application = Application.builder().token(BOT_TOKEN).build()

    # Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.Document.ALL, handle_apk))

    # Start the bot
    print("Bot is running...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
