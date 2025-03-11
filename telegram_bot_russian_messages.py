from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ConversationHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from telegram.constants import ParseMode
import os

SELECT_OPTION, WAITING_FOR_ANON_QUESTION, WAITING_FOR_ADM_QUESTION, WAITING_FOR_NAME, WAITING_FOR_NAME_QUESTION = range(5)
ADMIN_IDS = {os.environ.get("ADMIN_1"), os.environ.get("ADMIN_2")} #id of admins
TOKEN = os.environ.get("TOKEN") #your token from BotFather
GROUP_CHAT_ID = os.environ.get("GROUP_ID") #id of the group you've added the bot to. starts with a minus sign
START_MESSAGE = "Здравствуйте! Здесь вы можете задать публичный или анонимный вопрос спикеру или администрации клуба N. \
Последняя встреча состоялась с K., в четверг, p/q/2025. \
Следующая встреча будет объявлена в ближайшее время.\n\nПубличный вопрос будет задан от вашего лица. Отменить вопрос можно командой /cancel."

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Анонимный вопрос", callback_data='anon')],
        [InlineKeyboardButton("Публичный вопрос", callback_data='public')],
        [InlineKeyboardButton("Вопрос организаторам", callback_data='admin')]
    ]
    text = START_MESSAGE
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(text=text, reply_markup=reply_markup)
    return SELECT_OPTION

async def option_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    selection = query.data
    context.user_data['selection'] = selection
    quest_dict = {'anon': "анонимный вопрос", 'admin': "вопрос организатору"}

    if selection == 'admin':
        await query.message.reply_text("Введите ваш вопрос организатору.")
        return WAITING_FOR_ADM_QUESTION
    elif selection == 'anon':
        await query.message.reply_text("Введите ваш анонимный вопрос.")
        return WAITING_FOR_ANON_QUESTION
    elif selection == 'public':
        await query.message.reply_text("Введите ваше имя.")
        return WAITING_FOR_NAME
    else:
        await query.message.reply_text("Невалидный ответ. Попробуйте заново.")
        return ConversationHandler.END

async def receive_anon(update: Update, context: ContextTypes.DEFAULT_TYPE):
    question = update.message.text
    message_to_group = f"Анонимный вопрос:\n{question}"
    await context.bot.send_message(chat_id=GROUP_CHAT_ID, text=message_to_group, parse_mode=ParseMode.HTML)
    await update.message.reply_text("Ваш вопрос записан анонимно. Спасибо!\nЧтобы задать новый вопрос, нажмите /start.")
    return ConversationHandler.END

async def receive_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    question = update.message.text
    user = update.message.from_user
    profile_link = f'<a href="tg://user?id={user.id}">{user.first_name}</a>'
    message_to_group = (f"Публичный вопрос от {profile_link} (<code>{user.id}</code>):\n{question}")
    await context.bot.send_message(chat_id=GROUP_CHAT_ID, text=message_to_group, parse_mode=ParseMode.HTML)
    await update.message.reply_text("Ваш вопрос организатору записан. Спасибо!\nЧтобы задать новый вопрос, нажмите /start.")
    return ConversationHandler.END

async def receive_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.message.text
    context.user_data['name'] = name
    await update.message.reply_text("Введите ваш публичный вопрос.")
    return WAITING_FOR_NAME_QUESTION

async def receive_public(update: Update, context: ContextTypes.DEFAULT_TYPE):
    question = update.message.text
    user = update.message.from_user
    name = context.user_data.get('name', 'Unknown')
    profile_link = f'<a href="tg://user?id={user.id}">{user.first_name}</a>'
    message_to_group = (f"<b>Публичный</b> вопрос от {profile_link} (<code>{user.id}</code>):\n{question}\n(c) {name}")
    await context.bot.send_message(chat_id=GROUP_CHAT_ID, text=message_to_group, parse_mode=ParseMode.HTML)
    await update.message.reply_text("Ваш вопрос записан. Спасибо!\nЧтобы задать новый вопрос, нажмите /start.")
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Вопрос отменен. Чтобы задать новый вопрос, нажмите /start")
    return ConversationHandler.END

async def send_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.message.from_user.id not in ADMIN_IDS:
        user = update.message.from_user
        profile_link = f'<a href="tg://user?id={user.id}">{user.first_name}</a>'
        await update.message.reply_text("У вас нет права на эту команду.")
        await context.bot.send_message(chat_id=GROUP_CHAT_ID, text=f'Попытка использования команды send от {profile_link} (<code>{user.id}</code>).')
        return
    
    parts = update.message.text.split(maxsplit=2)
    if len(parts) < 3:
        await update.message.reply_text("Неправильный формат сообщения. Правильно: <code>/send <user_id> <your message></code>", parse_mode=ParseMode.HTML)
        return
    
    try:
        target_id = int(parts[1])
    except ValueError:
        await update.message.reply_text("Неправильный айди пользователя. Введите число")
        return
    message_text = parts[2]

    try:
        await context.bot.send_message(chat_id=target_id, text=message_text)
        await update.message.reply_text("Сообщение успешно отправлено.")
    except Exception as e:
        await update.message.reply_text(f"Сообщение не отправлено с ошибкой: {e}.")

async def reset_start_message_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global START_MESSAGE

    if update.message.from_user.id not in ADMIN_IDS:
        await update.message.reply_text("У вас нет права на эту команду.")
        await context.bot.send_message(chat_id=GROUP_CHAT_ID, text=f'Попытка использования команды send от tg://user?id={update.message.from_user.id}.')
        return
    
    parts = update.message.text.split(maxsplit=1)
    if len(parts) < 2:
        await update.message.reply_text("Неправильный формат сообщения. Правильно: <code>/reset <new start message></code>", parse_mode=ParseMode.HTML)
        return
    
    try:
        START_MESSAGE = str(parts[1])
        await update.message.reply_text(f"Стартовое сообщение успешно изменено на:\n<em>{START_MESSAGE}</em>", parse_mode=ParseMode.HTML)
    except Exception as e:
        await update.message.reply_text(f"Сообщение не отправлено с ошибкой: {e}.")

        

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            SELECT_OPTION: [CallbackQueryHandler(option_handler)],
            WAITING_FOR_ADM_QUESTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_admin)],
            WAITING_FOR_ANON_QUESTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_anon)],
            WAITING_FOR_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_name)],
            WAITING_FOR_NAME_QUESTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_public)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)
    app.add_handler(CommandHandler("send", send_command))
    app.add_handler(CommandHandler("reset", reset_start_message_command))
    app.run_polling()
