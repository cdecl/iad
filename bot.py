import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters, CallbackQueryHandler

import os
from run import place, home, fav, telno
from dotenv import load_dotenv

# 로깅 설정
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


user_inputs = {}


# /start 및 /help 명령어 핸들러
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # command_list = ["/start /s", "/place /p", "/home /h", "/fav /f"]
    response = "질문을 입력하고 버튼을 누르세요"
    await update.message.reply_text(response)


# async def handle_place(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     try:
#         if len(context.args) >= 2:
#             order_in = context.args[0]

#             if not order_in.isnumeric:
#                 raise Exception("질문오류 → ex> 1 장소명")
#             order = int(context.args[0])
#             q = ' '.join(context.args[1:])

#             r = place(order, "100", q)
#             await update.message.reply_text(f'{r}')
#         else:
#             raise Exception("질문오류 → ex> 1 장소명")
#     except Exception as e:
#         await update.message.reply_text(f"except: {e}")


# async def handle_home(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     try:
#         q = ' '.join(context.args)
#         if not q:
#             raise Exception('질문오류 → /h 장소이름')

#         r = home(q)
#         await update.message.reply_text(f'{r}')

#     except Exception as e:
#         await update.message.reply_text(f"except: {e}")


# async def handle_fav(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     try:
#         q = ' '.join(context.args)
#         if not q:
#             raise Exception('질문오류 → /f 장소이름')

#         r = fav(q)
#         await update.message.reply_text(f'{r}')

#     except Exception as e:
#         await update.message.reply_text(f"except: {e}")


# # 알 수 없는 명령어 처리
# async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     await update.message.reply_text("'/help' 입력 도움말 확인")


#####

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """버튼 선택을 처리합니다."""
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    user_input = user_inputs.get(user_id, "")

    if query.data == 'place':
        result = "ex) 1 장소명"
        args = user_input.split(' ')
        if len(args) >= 2:
            order_in = args[0]
            if order_in.isnumeric:
                order = int(args[0])
                q = ' '.join(args[1:])
                result = place(order, "100", q)
    elif query.data == 'home':
        result = home(user_input)
    elif query.data == 'fav':
        result = fav(user_input)
    elif query.data == 'telno':
        result = telno(user_input)

    await query.edit_message_text(f"{result}")


async def handle_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """사용자의 입력을 처리하고 버튼을 표시합니다."""
    user_input = update.message.text
    user_id = update.effective_user.id

    # 사용자 입력 저장
    user_inputs[user_id] = user_input

    keyboard = [
        [InlineKeyboardButton("N번째-명소", callback_data='place')],
        [InlineKeyboardButton("홈URL", callback_data='home')],
        [InlineKeyboardButton("홈URL-저장", callback_data='fav')],
        [InlineKeyboardButton("전화번호", callback_data='telno')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("어떤 작업을 수행할까요?", reply_markup=reply_markup)


def main():
    load_dotenv()
    TOKEN = os.getenv('TELEGRAM_TOKEN')
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler(["start", "help"], start))
    # app.add_handler(CommandHandler(["place", "p"], handle_place))
    # app.add_handler(CommandHandler(["home", "h"], handle_home))
    # app.add_handler(CommandHandler(["fav", "f"], handle_fav))
    app.add_handler(MessageHandler(filters.COMMAND, start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_input))
    app.add_handler(CallbackQueryHandler(button_callback))

    print('Bot Start ...')
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
