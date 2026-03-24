import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ConversationHandler, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from config import DEPARTMENT_NAME, EXCEL_FILE_PATH, IMAGES_FOLDER
from utils.excel_handler import save_to_excel
from utils.image_handler import save_image
import os

# States
ASK_REASON, ASK_CITY, ASK_NATIONALITY, ASK_NAME, ASK_AGE, ASK_VISA, ASK_JOB_TYPE, ASK_EXPERIENCE, ASK_OTHER_REASON, ASK_CURRENT_POSITION, ASK_LANGUAGE, ASK_SALARY, ASK_PASSPORT, ASK_PHOTO = range(14)

# Visa specific states
ASK_VISA_COUNTRY, ASK_VISA_TYPE, ASK_VISA_DURATION, ASK_VISA_PASSPORT_PHOTO, ASK_VISA_ID_PHOTO = range(14, 19)

user_data = {}

async def start(update: Update, context):
    user = update.effective_user
    
    if update.message.chat.type == "private":
        keyboard = [
            [InlineKeyboardButton("💼 Find Work", callback_data='find_work')],
            [InlineKeyboardButton("🛂 Apply Visa", callback_data='apply_visa')],
            [InlineKeyboardButton("ℹ️ Other Information", callback_data='other_info')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "🎯 *Welcome!*\n\nMay I know why you are here?",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        return ASK_REASON
    
    elif update.message.chat.type in ["group", "supergroup"]:
        await update.message.delete()
        await update.message.reply_text(
            f"👋 Hi {user.first_name}! Please click the button below to start registration in private chat:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔑 Start Registration", url=f"https://t.me/{context.bot.username}")]
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
        user_data[user_id]['reason'] = 'Find Work'
        user_data[user_id]['type'] = 'work'
        await query.edit_message_text("📍 *Where do you want to find work?*\n\nPlease send the city name:", parse_mode='Markdown')
        return ASK_CITY
    elif query.data == 'apply_visa':
        user_data[user_id]['reason'] = 'Apply Visa'
        user_data[user_id]['type'] = 'visa'
        await query.edit_message_text("🌍 *Which country do you want to apply for visa?*\n\nPlease send the country name:", parse_mode='Markdown')
        return ASK_VISA_COUNTRY
    elif query.data == 'other_info':
        user_data[user_id]['reason'] = 'Other Information'
        user_data[user_id]['type'] = 'other'
        await query.edit_message_text("ℹ️ *Please tell us your reason for joining:*\n\nSend your message:", parse_mode='Markdown')
        return ASK_OTHER_REASON

# ==================== VISA SPECIFIC HANDLERS ====================

async def visa_country_handler(update: Update, context):
    user_id = update.message.from_user.id
    user_data[user_id]['visa_country'] = update.message.text
    
    keyboard = [
        [InlineKeyboardButton("✈️ Work Visa", callback_data='visa_work')],
        [InlineKeyboardButton("🏖️ Tourist Visa", callback_data='visa_tourist')],
        [InlineKeyboardButton("📚 Student Visa", callback_data='visa_student')],
        [InlineKeyboardButton("🏥 Medical Visa", callback_data='visa_medical')],
        [InlineKeyboardButton("👨‍👩‍👧 Family Visa", callback_data='visa_family')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🪪 *What type of visa do you need?*",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    return ASK_VISA_TYPE

async def visa_type_handler(update: Update, context):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    
    visa_types = {
        'visa_work': 'Work Visa',
        'visa_tourist': 'Tourist Visa',
        'visa_student': 'Student Visa',
        'visa_medical': 'Medical Visa',
        'visa_family': 'Family Visa'
    }
    user_data[user_id]['visa_type'] = visa_types.get(query.data, 'Other')
    
    keyboard = [
        [InlineKeyboardButton("3 Months", callback_data='3_months')],
        [InlineKeyboardButton("6 Months", callback_data='6_months')],
        [InlineKeyboardButton("1 Year", callback_data='1_year')],
        [InlineKeyboardButton("2 Years", callback_data='2_years')],
        [InlineKeyboardButton("Other", callback_data='other_duration')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "📅 *How long do you need the visa for?*",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    return ASK_VISA_DURATION

async def visa_duration_handler(update: Update, context):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    
    durations = {
        '3_months': '3 Months',
        '6_months': '6 Months',
        '1_year': '1 Year',
        '2_years': '2 Years',
        'other_duration': 'Other'
    }
    user_data[user_id]['visa_duration'] = durations.get(query.data, 'Other')
    
    if query.data == 'other_duration':
        await query.edit_message_text(
            "📅 *Please specify the duration you need:*\n\nSend your answer:",
            parse_mode='Markdown'
        )
        return ASK_VISA_DURATION
    else:
        await query.edit_message_text(
            "📸 *Please send a clear photo of your passport (first page)*\n\n"
            "Make sure all details are visible:",
            parse_mode='Markdown'
        )
        return ASK_VISA_PASSPORT_PHOTO

async def visa_duration_text_handler(update: Update, context):
    user_id = update.message.from_user.id
    user_data[user_id]['visa_duration'] = update.message.text
    await update.message.reply_text(
        "📸 *Please send a clear photo of your passport (first page)*\n\n"
        "Make sure all details are visible:",
        parse_mode='Markdown'
    )
    return ASK_VISA_PASSPORT_PHOTO

async def visa_passport_photo_handler(update: Update, context):
    user_id = update.message.from_user.id
    
    if update.message.photo:
        user_data[user_id]['passport_photo'] = "Yes"
        photo_file = await update.message.photo[-1].get_file()
        saved_path = save_image(photo_file, user_id, IMAGES_FOLDER)
        if saved_path:
            user_data[user_id]['passport_photo_path'] = saved_path
        await update.message.reply_text("✅ *Passport photo saved!*", parse_mode='Markdown')
    else:
        user_data[user_id]['passport_photo'] = "No"
        await update.message.reply_text("⚠️ No photo received. Skipping...", parse_mode='Markdown')
    
    await update.message.reply_text(
        "🪪 *Please send a clear photo of your National ID Card / CNIC*\n\n"
        "Both sides if possible:",
        parse_mode='Markdown'
    )
    return ASK_VISA_ID_PHOTO

async def visa_id_photo_handler(update: Update, context):
    user_id = update.message.from_user.id
    
    if update.message.photo:
        user_data[user_id]['id_photo'] = "Yes"
        photo_file = await update.message.photo[-1].get_file()
        saved_path = save_image(photo_file, user_id, IMAGES_FOLDER)
        if saved_path:
            user_data[user_id]['id_photo_path'] = saved_path
        await update.message.reply_text("✅ *ID photo saved!*", parse_mode='Markdown')
    else:
        user_data[user_id]['id_photo'] = "No"
        await update.message.reply_text("⚠️ No photo received. Skipping...", parse_mode='Markdown')
    
    # Save all visa data to Excel
    save_to_excel(user_data[user_id], EXCEL_FILE_PATH)
    
    # Professional Visa Completion Message
    await update.message.reply_text(
        f"✅ *VISA APPLICATION SUCCESSFULLY SUBMITTED!*\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🎉 *Thank You, {user_data[user_id].get('name', user_data[user_id].get('username', 'User'))}!*\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"📋 *Application Summary:*\n"
        f"┌─────────────────────────────────┐\n"
        f"│ 🌍 *Country:* {user_data[user_id].get('visa_country', 'N/A')}\n"
        f"│ 🪪 *Visa Type:* {user_data[user_id].get('visa_type', 'N/A')}\n"
        f"│ 📅 *Duration:* {user_data[user_id].get('visa_duration', 'N/A')}\n"
        f"│ 📸 *Passport Photo:* {'✅ Received' if user_data[user_id].get('passport_photo') == 'Yes' else '❌ Not Received'}\n"
        f"│ 🪪 *ID Card Photo:* {'✅ Received' if user_data[user_id].get('id_photo') == 'Yes' else '❌ Not Received'}\n"
        f"└─────────────────────────────────┘\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"✈️ *Our Travel Agency Team will contact you within 24-48 hours!*\n\n"
        f"📞 *You will receive:*\n"
        f"• Consultation call from our visa expert\n"
        f"• Document checklist via email\n"
        f"• Visa processing status updates\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"💡 *Need immediate assistance?*\n"
        f"📧 Email: support@travelagency.com\n"
        f"📱 WhatsApp: +1234567890\n\n"
        f"⭐ *Thank you for choosing our services!*\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"*Best of luck with your visa application!* 🍀",
        parse_mode='Markdown'
    )
    return ConversationHandler.END

# ==================== WORK SPECIFIC HANDLERS ====================

async def city_handler(update: Update, context):
    user_id = update.message.from_user.id
    user_data[user_id]['city'] = update.message.text
    await update.message.reply_text("🌍 *What is your nationality?*\n\nPlease send your nationality:", parse_mode='Markdown')
    return ASK_NATIONALITY

async def nationality_handler(update: Update, context):
    user_id = update.message.from_user.id
    user_data[user_id]['nationality'] = update.message.text
    await update.message.reply_text("👤 *What is your name?*\n\nPlease send your full name:", parse_mode='Markdown')
    return ASK_NAME

async def name_handler(update: Update, context):
    user_id = update.message.from_user.id
    user_data[user_id]['name'] = update.message.text
    await update.message.reply_text("🎂 *What is your age?*\n\nPlease send your age:", parse_mode='Markdown')
    return ASK_AGE

async def age_handler(update: Update, context):
    user_id = update.message.from_user.id
    user_data[user_id]['age'] = update.message.text
    keyboard = [[InlineKeyboardButton("✅ Yes", callback_data='visa_yes')], [InlineKeyboardButton("❌ No", callback_data='visa_no')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("🪪 *Do you have a valid visa or passport?*", reply_markup=reply_markup, parse_mode='Markdown')
    return ASK_VISA

async def visa_handler(update: Update, context):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    user_data[user_id]['has_visa'] = "Yes" if query.data == 'visa_yes' else "No"
    keyboard = [
        [InlineKeyboardButton("👨‍💻 Developer", callback_data='job_developer')],
        [InlineKeyboardButton("📝 Translator", callback_data='job_translator')],
        [InlineKeyboardButton("📞 Receptionist", callback_data='job_receptionist')],
        [InlineKeyboardButton("❓ Other", callback_data='job_other')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("💼 *What are your requirements?*\n\nPlease select your desired job position:", reply_markup=reply_markup, parse_mode='Markdown')
    return ASK_JOB_TYPE

async def job_type_handler(update: Update, context):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    
    if query.data == 'job_developer':
        user_data[user_id]['job_type'] = 'Developer'
        await query.edit_message_text("💻 *How many years of experience do you have as a Developer?*", parse_mode='Markdown')
        return ASK_EXPERIENCE
    elif query.data == 'job_translator':
        user_data[user_id]['job_type'] = 'Translator'
        await query.edit_message_text("📝 *How many years of experience do you have as a Translator?*", parse_mode='Markdown')
        return ASK_EXPERIENCE
    elif query.data == 'job_receptionist':
        user_data[user_id]['job_type'] = 'Receptionist'
        await query.edit_message_text("📞 *How many years of experience do you have as a Receptionist?*", parse_mode='Markdown')
        return ASK_EXPERIENCE
    elif query.data == 'job_other':
        user_data[user_id]['job_type'] = 'Other'
        await query.edit_message_text("❓ *Please tell us about your requirements:*", parse_mode='Markdown')
        return ASK_OTHER_REASON

async def experience_handler(update: Update, context):
    user_id = update.message.from_user.id
    user_data[user_id]['experience'] = update.message.text
    await update.message.reply_text("💼 *What is your current position?*", parse_mode='Markdown')
    return ASK_CURRENT_POSITION

async def current_position_handler(update: Update, context):
    user_id = update.message.from_user.id
    user_data[user_id]['current_position'] = update.message.text
    await update.message.reply_text("🗣️ *What languages do you speak?*", parse_mode='Markdown')
    return ASK_LANGUAGE

async def language_handler(update: Update, context):
    user_id = update.message.from_user.id
    user_data[user_id]['languages'] = update.message.text
    await update.message.reply_text("💰 *What is your salary expectation?*", parse_mode='Markdown')
    return ASK_SALARY

async def salary_handler(update: Update, context):
    user_id = update.message.from_user.id
    user_data[user_id]['salary_expectation'] = update.message.text
    await update.message.reply_text("🪪 *Please provide your passport number:*", parse_mode='Markdown')
    return ASK_PASSPORT

async def passport_handler(update: Update, context):
    user_id = update.message.from_user.id
    user_data[user_id]['passport_number'] = update.message.text
    await update.message.reply_text("📸 *Please send your profile picture* (optional)\n\nType /skip to continue:", parse_mode='Markdown')
    return ASK_PHOTO

async def photo_handler(update: Update, context):
    user_id = update.message.from_user.id
    
    if update.message.photo:
        user_data[user_id]['has_photo'] = "Yes"
        photo_file = await update.message.photo[-1].get_file()
        saved_path = save_image(photo_file, user_id, IMAGES_FOLDER)
        if saved_path:
            user_data[user_id]['photo_path'] = saved_path
    else:
        user_data[user_id]['has_photo'] = "No"
    
    save_to_excel(user_data[user_id], EXCEL_FILE_PATH)
    
    await update.message.reply_text(
        f"✅ *Registration Complete!*\n\n"
        f"Thank you {user_data[user_id].get('name', '')}!\n\n"
        f"📋 *Your Information:*\n"
        f"👤 Name: {user_data[user_id].get('name', 'N/A')}\n"
        f"💼 Job: {user_data[user_id].get('job_type', 'N/A')}\n"
        f"📍 City: {user_data[user_id].get('city', 'N/A')}\n"
        f"🌍 Nationality: {user_data[user_id].get('nationality', 'N/A')}\n\n"
        f"Our {DEPARTMENT_NAME} will contact you soon via inbox.\n\n"
        f"Good luck! 🍀",
        parse_mode='Markdown'
    )
    return ConversationHandler.END

async def skip_photo_handler(update: Update, context):
    user_id = update.message.from_user.id
    user_data[user_id]['has_photo'] = "No"
    save_to_excel(user_data[user_id], EXCEL_FILE_PATH)
    await update.message.reply_text(
        f"✅ *Registration Complete!*\n\n"
        f"Thank you {user_data[user_id].get('name', '')}!\n\n"
        f"📋 *Your Information:*\n"
        f"👤 Name: {user_data[user_id].get('name', 'N/A')}\n"
        f"💼 Job: {user_data[user_id].get('job_type', 'N/A')}\n"
        f"📍 City: {user_data[user_id].get('city', 'N/A')}\n"
        f"🌍 Nationality: {user_data[user_id].get('nationality', 'N/A')}\n\n"
        f"Our {DEPARTMENT_NAME} will contact you soon via inbox.\n\n"
        f"Good luck! 🍀",
        parse_mode='Markdown'
    )
    return ConversationHandler.END

async def other_reason_handler(update: Update, context):
    user_id = update.message.from_user.id
    user_data[user_id]['other_reason'] = update.message.text
    await update.message.reply_text("💼 *What is your current position?*", parse_mode='Markdown')
    return ASK_CURRENT_POSITION

async def cancel(update: Update, context):
    await update.message.reply_text("❌ Registration cancelled. Type /start to begin again.")
    return ConversationHandler.END

def get_registration_handler():
    return ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            ASK_REASON: [CallbackQueryHandler(button_handler)],
            # Visa states
            ASK_VISA_COUNTRY: [MessageHandler(filters.TEXT & ~filters.COMMAND, visa_country_handler)],
            ASK_VISA_TYPE: [CallbackQueryHandler(visa_type_handler)],
            ASK_VISA_DURATION: [
                CallbackQueryHandler(visa_duration_handler),
                MessageHandler(filters.TEXT & ~filters.COMMAND, visa_duration_text_handler)
            ],
            ASK_VISA_PASSPORT_PHOTO: [MessageHandler(filters.PHOTO, visa_passport_photo_handler)],
            ASK_VISA_ID_PHOTO: [MessageHandler(filters.PHOTO, visa_id_photo_handler)],
            # Work states
            ASK_CITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, city_handler)],
            ASK_NATIONALITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, nationality_handler)],
            ASK_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, name_handler)],
            ASK_AGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, age_handler)],
            ASK_VISA: [CallbackQueryHandler(visa_handler)],
            ASK_JOB_TYPE: [CallbackQueryHandler(job_type_handler)],
            ASK_EXPERIENCE: [MessageHandler(filters.TEXT & ~filters.COMMAND, experience_handler)],
            ASK_OTHER_REASON: [MessageHandler(filters.TEXT & ~filters.COMMAND, other_reason_handler)],
            ASK_CURRENT_POSITION: [MessageHandler(filters.TEXT & ~filters.COMMAND, current_position_handler)],
            ASK_LANGUAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, language_handler)],
            ASK_SALARY: [MessageHandler(filters.TEXT & ~filters.COMMAND, salary_handler)],
            ASK_PASSPORT: [MessageHandler(filters.TEXT & ~filters.COMMAND, passport_handler)],
            ASK_PHOTO: [MessageHandler(filters.PHOTO, photo_handler), CommandHandler('skip', skip_photo_handler)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

async def start_registration_from_welcome(update: Update, context: ContextTypes.DEFAULT_TYPE, query):
    user_id = query.from_user.id
    user_data[user_id] = {}
    user_data[user_id]['username'] = query.from_user.username or "No username"
    user_data[user_id]['user_id'] = user_id
    
    if query.data == 'find_work':
        user_data[user_id]['reason'] = 'Find Work'
        user_data[user_id]['type'] = 'work'
        await query.edit_message_text("📍 *Where do you want to find work?*\n\nPlease send the city name:", parse_mode='Markdown')
        return ASK_CITY
    elif query.data == 'apply_visa':
        user_data[user_id]['reason'] = 'Apply Visa'
        user_data[user_id]['type'] = 'visa'
        await query.edit_message_text("🌍 *Which country do you want to apply for visa?*\n\nPlease send the country name:", parse_mode='Markdown')
        return ASK_VISA_COUNTRY
    elif query.data == 'other_info':
        user_data[user_id]['reason'] = 'Other Information'
        user_data[user_id]['type'] = 'other'
        await query.edit_message_text("ℹ️ *Please tell us your reason for joining:*\n\nSend your message:", parse_mode='Markdown')
        return ASK_OTHER_REASON
