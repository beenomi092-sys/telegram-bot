from telegram import Update
from telegram.ext import CommandHandler
from config import ADMIN_IDS, DEPARTMENT_NAME, EXCEL_FILE_PATH
from utils.excel_handler import get_all_users, search_users

def admin_only(func):
    async def wrapper(update: Update, context):
        user_id = update.effective_user.id
        if user_id not in ADMIN_IDS:
            await update.message.reply_text("❌ You are not authorized.")
            return
        return await func(update, context)
    return wrapper

@admin_only
async def view_all_users(update: Update, context):
    users = get_all_users(EXCEL_FILE_PATH)
    if not users:
        await update.message.reply_text("📭 No users found.")
        return
    message = "📊 *All Users List*\n\n"
    for i, user in enumerate(users[:10], 1):
        message += f"{i}. 👤 {user.get('name', 'N/A')} - 💼 {user.get('job_type', 'N/A')}\n"
    await update.message.reply_text(message, parse_mode='Markdown')

@admin_only
async def search_user(update: Update, context):
    if not context.args:
        await update.message.reply_text("🔍 *Usage:* `/search <name or job type>`", parse_mode='Markdown')
        return
    search_term = ' '.join(context.args)
    results = search_users(search_term, EXCEL_FILE_PATH)
    if not results:
        await update.message.reply_text(f"❌ No users found with '{search_term}'")
        return
    message = f"🔍 *Search Results for '{search_term}':*\n\n"
    for i, user in enumerate(results[:10], 1):
        message += f"{i}. 👤 *{user.get('name', 'N/A')}*\n   💼 {user.get('job_type', 'N/A')}\n   📍 {user.get('city', 'N/A')}\n\n"
    await update.message.reply_text(message, parse_mode='Markdown')

@admin_only
async def export_users(update: Update, context):
    users = get_all_users(EXCEL_FILE_PATH)
    if not users:
        await update.message.reply_text("📭 No users to export.")
        return
    await update.message.reply_document(document=open(EXCEL_FILE_PATH, 'rb'), filename="users_data.xlsx", caption="📊 Users data export")

@admin_only
async def send_message_to_user(update: Update, context):
    if len(context.args) < 2:
        await update.message.reply_text("📨 *Usage:* `/msg <user_id> <message>`", parse_mode='Markdown')
        return
    try:
        user_id = int(context.args[0])
        message_text = ' '.join(context.args[1:])
        await context.bot.send_message(chat_id=user_id, text=f"📩 *Message from {DEPARTMENT_NAME}:*\n\n{message_text}", parse_mode='Markdown')
        await update.message.reply_text(f"✅ Message sent to user {user_id}")
    except Exception as e:
        await update.message.reply_text(f"❌ Failed: {str(e)}")

def get_admin_handlers():
    return [
        CommandHandler('users', view_all_users),
        CommandHandler('search', search_user),
        CommandHandler('export', export_users),
        CommandHandler('msg', send_message_to_user),
    ]
