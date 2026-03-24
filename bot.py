import logging
from telegram.ext import Application
from config import BOT_TOKEN
from handlers.registration import get_registration_handler
from handlers.admin_handlers import get_admin_handlers
from handlers.welcome import get_welcome_handler

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

def main():
    application = Application.builder().token(BOT_TOKEN).build()
    
    application.add_handler(get_registration_handler())
    application.add_handler(get_welcome_handler())
    
    for handler in get_admin_handlers():
        application.add_handler(handler)
    
    print("🤖 Bot is running...")
    application.run_polling()

if __name__ == '__main__':
    main()
