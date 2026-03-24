from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, MessageHandler, filters
import asyncio

# Store user states to avoid duplicate messages
user_welcomed = {}

async def welcome_new_members(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Jab koi naya member group join kare to ye chalega"""
    
    # Check karo ke koi naya member aaya hai
    for member in update.message.new_chat_members:
        # Agar bot khud add ho raha hai to ignore karo
        if member.is_bot:
            continue
        
        user_id = member.id
        
        # Agar already welcome message bhej chuke to doobara na bhejein
        if user_id in user_welcomed:
            continue
        
        # Store kar do ke welcome bhej rahe hain
        user_welcomed[user_id] = True
        
        # Buttons banao
        keyboard = [
            [InlineKeyboardButton("💼 Find Work", callback_data='find_work')],
            [InlineKeyboardButton("🛂 Apply Visa", callback_data='apply_visa')],
            [InlineKeyboardButton("ℹ️ Other Information", callback_data='other_info')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Welcome message bhejo
        await update.message.reply_text(
            f"🎯 *Welcome {member.first_name}!*\n\n"
            f"May I know why you joined the group?\n\n"
            f"Please select an option below:",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
        # 5 minute baad state clear karo (agar user ne response nahi diya)
        async def clear_state():
            await asyncio.sleep(300)  # 5 minutes
            if user_id in user_welcomed:
                del user_welcomed[user_id]
        
        asyncio.create_task(clear_state())

def get_welcome_handler():
    """Welcome handler return karna"""
    return MessageHandler(
        filters.StatusUpdate.NEW_CHAT_MEMBERS,
        welcome_new_members
    )
