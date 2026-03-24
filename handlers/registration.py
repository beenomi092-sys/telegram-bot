import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ConversationHandler, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from config import DEPARTMENT_NAME, EXCEL_FILE_PATH, IMAGES_FOLDER
from utils.excel_handler import save_to_excel
from utils.image_handler import save_image
import os

ASK_REASON, ASK_FORM = range(2)

user_data = {}

async def start(update: Update, context):
    user = update.effective_user
    
    if update.message.chat.type == "private":
        keyboard = [
            [InlineKeyboardButton("💼 Apply for Job", callback_data='find_work')],
            [InlineKeyboardButton("🛂 Apply for Visa", callback_data='apply_visa')],
            [InlineKeyboardButton("ℹ️ Other Information", callback_data='other_info')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "🎯 *Welcome!*\n\nPlease select an option:",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        return ASK_REASON
    
    elif update.message.chat.type in ["group", "supergroup"]:
        await update.message.delete()
        await update.message.reply_text(
            f"👋 Hi {user.first_name}! Please click the button below:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔑 Start", url=f"https://t.me/{context.bot.username}")]
            ])
        )
        return ConversationHandler.END

async def button_handler(update: Update, context):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    user_data[user_id] = {}
    user_data[user_id]['username'] = query.from_user.username or "No username"
    user_data[user_id]['user_id'] = user_id
    
    if query.data == 'find_work':
        user_data[user_id]['type'] = 'work'
        form = (
            "📝 *Job Application Form*\n\n"
            "Please fill all details below and send:\n\n"
            "1️⃣ *Full Name:*\n"
            "2️⃣ *Age:*\n"
            "3️⃣ *Nationality:*\n"
            "4️⃣ *City:*\n"
            "5️⃣ *Job Position:* (Developer/Translator/Receptionist/Other)\n"
            "6️⃣ *Experience:* (years)\n"
            "7️⃣ *Current Position:*\n"
            "8️⃣ *Languages:*\n"
            "9️⃣ *Salary Expectation:*\n"
            "🔟 *Passport Number:*\n\n"
            "Type /cancel to cancel"
        )
        await query.edit_message_text(form, parse_mode='Markdown')
        return ASK_FORM
        
    elif query.data == 'apply_visa':
        user_data[user_id]['type'] = 'visa'
        form = (
            "✈️ *Visa Application Form*\n\n"
            "Please fill all details below and send:\n\n"
            "1️⃣ *Full Name:*\n"
            "2️⃣ *Age:*\n"
            "3️⃣ *Nationality:*\n"
            "4️⃣ *Country to Apply:*\n"
            "5️⃣ *Visa Type:* (Work/Tourist/Student/Medical/Family)\n"
            "6️⃣ *Duration:* (3/6/12/24 months)\n"
            "7️⃣ *Passport Number:*\n\n"
            "📸 *After filling, please send your Passport Photo and ID Card Photo separately.*\n\n"
            "Type /cancel to cancel"
        )
        await query.edit_message_text(form, parse_mode='Markdown')
        return ASK_FORM
        
    elif query.data == 'other_info':
        user_data[user_id]['type'] = 'other'
        await query.edit_message_text(
            "ℹ️ *Please tell us your reason for contacting us:*\n\n"
            "Send your message below:",
            parse_mode='Markdown'
        )
        return ASK_FORM

async def form_handler(update: Update, context):
    user_id = update.message.from_user.id
    text = update.message.text
    
    if text == '/cancel':
        await update.message.reply_text("❌ Cancelled. Type /start to begin again.")
        return ConversationHandler.END
    
    user_data[user_id]['form_data'] = text
    
    if user_data[user_id]['type'] == 'work':
        # Parse work form data
        lines = text.strip().split('\n')
        data = {}
        for line in lines:
            if line.startswith('1️⃣') or line.startswith('1'):
                data['name'] = line.split(':', 1)[-1].strip() if ':' in line else line.split(')', 1)[-1].strip()
            elif line.startswith('2️⃣') or line.startswith('2'):
                data['age'] = line.split(':', 1)[-1].strip() if ':' in line else line.split(')', 1)[-1].strip()
            elif line.startswith('3️⃣') or line.startswith('3'):
                data['nationality'] = line.split(':', 1)[-1].strip() if ':' in line else line.split(')', 1)[-1].strip()
            elif line.startswith('4️⃣') or line.startswith('4'):
                data['city'] = line.split(':', 1)[-1].strip() if ':' in line else line.split(')', 1)[-1].strip()
            elif line.startswith('5️⃣') or line.startswith('5'):
                data['job_type'] = line.split(':', 1)[-1].strip() if ':' in line else line.split(')', 1)[-1].strip()
            elif line.startswith('6️⃣') or line.startswith('6'):
                data['experience'] = line.split(':', 1)[-1].strip() if ':' in line else line.split(')', 1)[-1].strip()
            elif line.startswith('7️⃣') or line.startswith('7'):
                data['current_position'] = line.split(':', 1)[-1].strip() if ':' in line else line.split(')', 1)[-1].strip()
            elif line.startswith('8️⃣') or line.startswith('8'):
                data['languages'] = line.split(':', 1)[-1].strip() if ':' in line else line.split(')', 1)[-1].strip()
            elif line.startswith('9️⃣') or line.startswith('9'):
                data['salary'] = line.split(':', 1)[-1].strip() if ':' in line else line.split(')', 1)[-1].strip()
            elif line.startswith('🔟') or line.startswith('10'):
                data['passport'] = line.split(':', 1)[-1].strip() if ':' in line else line.split(')', 1)[-1].strip()
        
        for key, value in data.items():
            user_data[user_id][key] = value
        user_data[user_id]['job_type'] = data.get('job_type', 'N/A')
        
        save_to_excel(user_data[user_id], EXCEL_FILE_PATH)
        
        await update.message.reply_text(
            f"✅ *Application Submitted!*\n\n"
            f"Thank you {data.get('name', 'User')}!\n\n"
            f"📋 *Your Application:*\n"
            f"👤 Name: {data.get('name', 'N/A')}\n"
            f"💼 Job: {data.get('job_type', 'N/A')}\n"
            f"📍 City: {data.get('city', 'N/A')}\n\n"
            f"Our {DEPARTMENT_NAME} will contact you soon!\n\n"
            f"Good luck! 🍀",
            parse_mode='Markdown'
        )
        
    elif user_data[user_id]['type'] == 'visa':
        # Parse visa form data
        lines = text.strip().split('\n')
        data = {}
        for line in lines:
            if line.startswith('1️⃣') or line.startswith('1'):
                data['name'] = line.split(':', 1)[-1].strip() if ':' in line else line.split(')', 1)[-1].strip()
            elif line.startswith('2️⃣') or line.startswith('2'):
                data['age'] = line.split(':', 1)[-1].strip() if ':' in line else line.split(')', 1)[-1].strip()
            elif line.startswith('3️⃣') or line.startswith('3'):
                data['nationality'] = line.split(':', 1)[-1].strip() if ':' in line else line.split(')', 1)[-1].strip()
            elif line.startswith('4️⃣') or line.startswith('4'):
                data['visa_country'] = line.split(':', 1)[-1].strip() if ':' in line else line.split(')', 1)[-1].strip()
            elif line.startswith('5️⃣') or line.startswith('5'):
                data['visa_type'] = line.split(':', 1)[-1].strip() if ':' in line else line.split(')', 1)[-1].strip()
            elif line.startswith('6️⃣') or line.startswith('6'):
                data['visa_duration'] = line.split(':', 1)[-1].strip() if ':' in line else line.split(')', 1)[-1].strip()
            elif line.startswith('7️⃣') or line.startswith('7'):
                data['passport'] = line.split(':', 1)[-1].strip() if ':' in line else line.split(')', 1)[-1].strip()
        
        for key, value in data.items():
            user_data[user_id][key] = value
        
        # Ask for photos
        user_data[user_id]['waiting_photo'] = True
        user_data[user_id]['photo_step'] = 'passport'
        await update.message.reply_text(
            f"✅ *Form Received!*\n\n"
            f"Now please send your *Passport Photo* 📸",
            parse_mode='Markdown'
        )
        return ASK_FORM
    
    elif user_data[user_id]['type'] == 'other':
        user_data[user_id]['message'] = text
        save_to_excel(user_data[user_id], EXCEL_FILE_PATH)
        await update.message.reply_text(
            f"✅ *Message Received!*\n\n"
            f"Thank you! We will get back to you soon.",
            parse_mode='Markdown'
        )
    
    return ConversationHandler.END

async def photo_handler(update: Update, context):
    user_id = update.message.from_user.id
    
    if user_id not in user_data or not user_data[user_id].get('waiting_photo'):
        await update.message.reply_text("Please use /start to begin.")
        return ConversationHandler.END
    
    if update.message.photo:
        photo_file = await update.message.photo[-1].get_file()
        saved_path = save_image(photo_file, user_id, IMAGES_FOLDER)
        
        if user_data[user_id].get('photo_step') == 'passport':
            user_data[user_id]['passport_photo'] = saved_path
            user_data[user_id]['photo_step'] = 'id'
            await update.message.reply_text("✅ *Passport photo saved!*\n\nNow please send your *ID Card Photo* 📇", parse_mode='Markdown')
            return ASK_FORM
        else:
            user_data[user_id]['id_photo'] = saved_path
            save_to_excel(user_data[user_id], EXCEL_FILE_PATH)
            await update.message.reply_text(
                f"✅ *Visa Application Complete!*\n\n"
                f"✈️ *Our Travel Agency will contact you soon!*\n\n"
                f"Good luck! 🍀",
                parse_mode='Markdown'
            )
            return ConversationHandler.END
    else:
        await update.message.reply_text("Please send a photo, or type /skip to skip.")
        return ASK_FORM

async def skip_photo_handler(update: Update, context):
    user_id = update.message.from_user.id
    
    if user_data[user_id].get('photo_step') == 'passport':
        user_data[user_id]['passport_photo'] = "Skipped"
        user_data[user_id]['photo_step'] = 'id'
        await update.message.reply_text("⚠️ Passport photo skipped.\n\nNow please send your *ID Card Photo* or type /skip", parse_mode='Markdown')
        return ASK_FORM
    else:
        user_data[user_id]['id_photo'] = "Skipped"
        save_to_excel(user_data[user_id], EXCEL_FILE_PATH)
        await update.message.reply_text(
            f"✅ *Visa Application Complete!*\n\n"
            f"✈️ *Our Travel Agency will contact you soon!*\n\n"
            f"Good luck! 🍀",
            parse_mode='Markdown'
        )
        return ConversationHandler.END

async def cancel(update: Update, context):
    await update.message.reply_text("❌ Cancelled. Type /start to begin again.")
    return ConversationHandler.END

def get_registration_handler():
    return ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            ASK_REASON: [CallbackQueryHandler(button_handler)],
            ASK_FORM: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, form_handler),
                MessageHandler(filters.PHOTO, photo_handler),
                CommandHandler('skip', skip_photo_handler)
            ],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
