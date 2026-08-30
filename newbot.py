import logging
import sys
from flask import Flask
from threading import Thread
from telegram import Update
from telegram.ext import ApplicationBuilder, ChatMemberHandler, ContextTypes
from telegram.constants import ChatMemberStatus

flask_app = Flask('')

@flask_app.route('/')
def home():
    return "Ultra Fast Live Stream Anti-Premium Bot is active and running!"

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

async def handle_live_stream_entry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        chat_member_update = update.chat_member
        if not chat_member_update:
            return

        chat_id = chat_member_update.chat.id
        new_member = chat_member_update.new_chat_member
        user = new_member.user

        if not user:
            return

        if LOCKED_CHANNEL_ID is not None and chat_id != LOCKED_CHANNEL_ID:
            logger.warning(f"[UNAUTHORIZED CHANNEL] Bot used in unauthorized chat ID: {chat_id}. Ignoring action.")
            return

        if new_member.status in [ChatMemberStatus.MEMBER, ChatMemberStatus.RESTRICTED]:
            
            if user.id == OWNER_USER_ID:
                logger.info(f"[SAFE OWNER] Bot Owner connected safely: {user.full_name} ({user.id})")
                return

            try:
                member_info = await context.bot.get_chat_member(chat_id, user.id)
                if member_info.status in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR]:
                    logger.info(f"[SAFE ADMIN] Owner/Admin allowed securely in live stream: {user.full_name} ({user.id})")
                    return
            except Exception as admin_err:
                logger.warning(f"Admin verification warning for {user.id}: {admin_err}")

            if getattr(user, "is_premium", False):
                try:
                    await context.bot.ban_chat_member(chat_id=chat_id, user_id=user.id)
                    logger.warning(f"[ULTRA FAST BAN] Instant banned premium user from live stream: {user.full_name} (ID: {user.id})")

                    try:
                        await context.bot.send_message(
                            chat_id=user.id,
                            text="*⚠️ Apni Aukaat Me Raha Karo, Haramzaade Kahin Ke! 🖕🤬*\n\n*⚡ Bina Ek Pal Gawaye Tumhara Pura Account Aur Tumhari Saari IDs Hamesha Ke Liye Mitti Me Mila Denge! Dobara Is Live Stream Ke Aas-Paas Bhi Dikhe Na, Toh Aisi Aag Lagayenge Ki Zindagi Bhar Telegram Kholne Se Dar Lagega! 🔥💣*\n\n*☠️ Apni Hadh Me Rehna Sikh Lo Warna Is Baar Toh Sirf Nikala Hai, Agli Baar Tumhara Wajood Hi Mitaa Denge! Samajh Me Aaya Ya Phir Is Warning Ko Tumhari G**nd Me Ghusa Doon? 🔪🩸⚠️*",
                            parse_mode="Markdown"
                        )
                        logger.info(f"[DM SENT] Live stream ban warning delivered to premium user ID: {user.id}")
                    except Exception as msg_err:
                        logger.info(f"Could not send DM to {user.id}: {msg_err}")

                except Exception as ban_err:
                    logger.error(f"Failed to execute instant live ban for premium user {user.id}: {ban_err}")
            else:
                logger.info(f"[SAFE USER] Normal non-premium user allowed in live stream: {user.full_name} ({user.id})")

    except Exception as e:
        logger.error(f"Critical unhandled exception in handle_live_stream_entry: {e}", exc_info=True)

def main():
    keep_alive()
    logger.info("Flask keep-alive background thread initialized with UptimeRobot support.")

    try:
        telegram_app = ApplicationBuilder().token(BOT_TOKEN).build()
        telegram_app.add_handler(ChatMemberHandler(handle_live_stream_entry, ChatMemberHandler.CHAT_MEMBER))

        logger.info("Ultra Fast Locked Anti-Premium Bot is active and polling securely...")
        
        telegram_app.run_polling(
            allowed_updates=[Update.CHAT_MEMBER, Update.MY_CHAT_MEMBER],
            drop_pending_updates=True
        )
    except Exception as e:
        logger.critical(f"Fatal error starting Telegram bot application: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()