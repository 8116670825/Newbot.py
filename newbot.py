import logging
import sys
import asyncio
from flask import Flask, request
from telegram import Update
from telegram.ext import ApplicationBuilder, ChatMemberHandler, ContextTypes
from telegram.constants import ChatMemberStatus

flask_app = Flask('')

@flask_app.route('/')
def home():
    return "Ultra-Fast Live Stream Anti-Premium Webhook Bot is active and running!"

@flask_app.route('/healthz')
def health_check():
    return "OK", 200

# Global application reference for webhook initialization
telegram_app = None

@flask_app.route('/webhook', methods=['POST'])
def webhook():
    if telegram_app and request.json:
        try:
            update = Update.de_json(request.json, telegram_app.bot)
            # Process the update asynchronously without blocking the webhook response
            asyncio.run_coroutine_threadsafe(telegram_app.process_update(update), telegram_app.loop)
        except Exception as e:
            logger.error(f"Error processing webhook update: {e}", exc_info=True)
    return "OK", 200

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

BOT_TOKEN = "8716958222:AAHgYYcicw1KQUYewlOJPF0RHaFy9CGCct0"
LOCKED_CHANNEL_ID = -1002982567511  
OWNER_USER_ID = 8064395854  
RENDER_EXTERNAL_URL = "YOUR_RENDER_SERVICE_URL" # उदाहरण: "https://your-app-name.onrender.com"

async def execute_instant_ban(bot, chat_id, user):
    try:
        await bot.ban_chat_member(chat_id=chat_id, user_id=user.id)
        logger.warning(f"[0.1s WEBHOOK INSTANT BAN] Banned premium user: {user.full_name} ({user.id})")
        try:
            await bot.send_message(
                chat_id=user.id,
                text="*⚠️ Apni Aukaat Me Raha Karo, Haramzaade Kahin Ke! 🖕🤬*\n\n*⚡ Live stream me scam karne ki koshish karne wale premium user ka pura account aur saari IDs hamesha ke liye block kar di gayi hain! 🔥💣*",
                parse_mode="Markdown"
            )
        except Exception:
            pass
    except Exception as e:
        logger.error(f"Failed to execute 0.1s instant ban for {user.id}: {e}")

async def handle_live_stream_entry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        chat_member_update = update.chat_member
        if not chat_member_update:
            return

        chat_id = chat_member_update.chat.id
        if LOCKED_CHANNEL_ID is not None and chat_id != LOCKED_CHANNEL_ID:
            return

        old_member = chat_member_update.old_chat_member
        new_member = chat_member_update.new_chat_member
        user = new_member.user if new_member and new_member.user else None

        if not user:
            return

        # 1. Owner bypass (Even if owner has Telegram Premium)
        if user.id == OWNER_USER_ID:
            logger.info(f"[SAFE OWNER] Owner allowed in live stream despite premium status: {user.full_name} ({user.id})")
            return

        # 2. Admin bypass (Even if admins have Telegram Premium)
        try:
            member_info = await context.bot.get_chat_member(chat_id, user.id)
            if member_info.status in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR]:
                logger.info(f"[SAFE ADMIN] Admin allowed in live stream despite premium status: {user.full_name} ({user.id})")
                return
        except Exception:
            pass

        # 3. Check if member is entering/active in live stream (Old & New members both)
        is_entering_live = (
            (old_member.status in [ChatMemberStatus.LEFT, ChatMemberStatus.BANNED] and new_member.status in [ChatMemberStatus.MEMBER, ChatMemberStatus.RESTRICTED]) or
            (old_member.status == ChatMemberStatus.MEMBER and new_member.status == ChatMemberStatus.MEMBER)
        )

        if is_entering_live:
            if getattr(user, "is_premium", False):
                asyncio.create_task(execute_instant_ban(context.bot, chat_id, user))
            else:
                logger.info(f"[SAFE NORMAL USER] Normal user allowed in live stream: {user.full_name} ({user.id})")

    except Exception as e:
        logger.error(f"Critical exception in live stream handler: {e}", exc_info=True)

def main():
    global telegram_app

    try:
        telegram_app = ApplicationBuilder().token(BOT_TOKEN).build()
        telegram_app.add_handler(ChatMemberHandler(handle_live_stream_entry, ChatMemberHandler.CHAT_MEMBER))

        # Initialize bot application
        asyncio.get_event_loop().run_until_complete(telegram_app.initialize())

        # Set Webhook URL with Telegram
        if RENDER_EXTERNAL_URL and RENDER_EXTERNAL_URL != "YOUR_RENDER_SERVICE_URL":
            webhook_url = f"{RENDER_EXTERNAL_URL.rstrip('/')}/webhook"
            asyncio.get_event_loop().run_until_complete(
                telegram_app.bot.set_webhook(url=webhook_url, allowed_updates=[Update.CHAT_MEMBER, Update.MY_CHAT_MEMBER])
            )
            logger.info(f"Webhook successfully set to: {webhook_url}")
        else:
            logger.warning("RENDER_EXTERNAL_URL is not set properly. Please update it with your actual Render URL.")

        logger.info("Starting Flask web server on port 8080...")
        flask_app.run(host='0.0.0.0', port=8080, debug=False, use_reloader=False)

    except Exception as e:
        logger.critical(f"Fatal error starting webhook application: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
    
