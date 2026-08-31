import logging
import sys
import asyncio
from flask import Flask
from threading import Thread
from telegram import Update
from telegram.ext import ApplicationBuilder, ChatMemberHandler, ContextTypes
from telegram.constants import ChatMemberStatus

flask_app = Flask('')

@flask_app.route('/')
def home():
    return "Ultra-Level Zero-Error Telegram Security Engine Active!"

@flask_app.route('/healthz')
def health_check():
    return "OK", 200

def run_flask():
    try:
        flask_app.run(host='0.0.0.0', port=8080, debug=False, use_reloader=False)
    except Exception as e:
        print(f"Flask server fatal error: {e}", file=sys.stderr)

def keep_alive():
    try:
        t = Thread(target=run_flask, daemon=True)
        t.start()
    except Exception as e:
        print(f"Thread error: {e}", file=sys.stderr)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

BOT_TOKEN = "8716958222:AAHgYYcicw1KQUYewlOJPF0RHaFy9CGCct0"
LOCKED_CHANNEL_ID = -1002982567511  
OWNER_USER_ID = 8064395854  

async def execute_ultra_safe_ban(bot, chat_id, user):
    try:
        await bot.ban_chat_member(chat_id=chat_id, user_id=user.id)
        logger.warning(f"[ZERO-ERROR INSTANT BAN] Neutralized threat: {user.full_name} ({user.id})")
        try:
            await bot.send_message(
                chat_id=user.id,
                text="*⚠️ Apni Aukaat Me Raha Karo, Haramzaade Kahin Ke! 🖕🤬*\n\n*⚡ Live stream me scam karne ki koshish karne wale premium user ka pura account aur saari IDs hamesha ke liye mitti me mila di gayi hain! 🔥💣*",
                parse_mode="Markdown"
            )
        except Exception:
            pass
    except Exception as e:
        logger.error(f"Safe ban execution error for {user.id}: {e}")

async def handle_live_stream_entry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if not update.chat_member:
            return

        chat_id = update.chat_member.chat.id
        if LOCKED_CHANNEL_ID is not None and chat_id != LOCKED_CHANNEL_ID:
            return

        old_member = update.chat_member.old_chat_member
        new_member = update.chat_member.new_chat_member
        
        if not new_member or not new_member.user:
            return

        user = new_member.user

        # 1. Absolute Owner Bypass
        if user.id == OWNER_USER_ID:
            return

        # 2. Resilient Admin Check with Exception Guard
        try:
            member_info = await context.bot.get_chat_member(chat_id, user.id)
            if member_info and member_info.status in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR]:
                return
        except Exception:
            pass

        # 3. Defensive Status Evaluation for Old & New Active Members
        old_status = old_member.status if old_member else ChatMemberStatus.LEFT
        new_status = new_member.status if new_member else ChatMemberStatus.MEMBER

        is_entering_live = (
            (old_status in [ChatMemberStatus.LEFT, ChatMemberStatus.BANNED] and new_status in [ChatMemberStatus.MEMBER, ChatMemberStatus.RESTRICTED]) or
            (old_status == ChatMemberStatus.MEMBER and new_status == ChatMemberStatus.MEMBER)
        )

        if is_entering_live:
            if getattr(user, "is_premium", False):
                asyncio.create_task(execute_ultra_safe_ban(context.bot, chat_id, user))
            else:
                logger.info(f"[SAFE NORMAL USER] Permitted: {user.full_name} ({user.id})")

    except Exception as e:
        logger.error(f"Non-fatal exception caught in stream handler: {e}", exc_info=False)

def main():
    keep_alive()
    logger.info("Keep-alive background thread initialized.")

    try:
        telegram_app = ApplicationBuilder().token(BOT_TOKEN).build()
        telegram_app.add_handler(ChatMemberHandler(handle_live_stream_entry, ChatMemberHandler.CHAT_MEMBER))

        logger.info("Zero-Error security engine active and polling...")
        telegram_app.run_polling(
            allowed_updates=[Update.CHAT_MEMBER, Update.MY_CHAT_MEMBER],
            drop_pending_updates=True
        )
    except Exception as e:
        logger.critical(f"Fatal application startup error: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
    
