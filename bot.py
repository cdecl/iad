import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters, CallbackQueryHandler

import os
from run import place, home, homesave, telno, info, homesavetelno
from run_ex import goods
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


# async def handle_homesave(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     try:
#         q = ' '.join(context.args)
#         if not q:
#             raise Exception('질문오류 → /f 장소이름')

#         r = homesave(q)
#         await update.message.reply_text(f'{r}')

#     except Exception as e:
#         await update.message.reply_text(f"except: {e}")


# # 알 수 없는 명령어 처리
# async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     await update.message.reply_text("'/help' 입력 도움말 확인")


#####
def isconsonants(text: str) -> bool:
    if not text:
        return False

    CHOSUNG_LIST = [
        'ㄱ', 'ㄲ', 'ㄴ', 'ㄷ', 'ㄸ', 'ㄹ', 'ㅁ', 'ㅂ', 'ㅃ', 'ㅅ', 'ㅆ', 'ㅇ', 'ㅈ', 'ㅉ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ'
    ]

    for char in text:
        if char not in CHOSUNG_LIST:
            return False
    return True


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """버튼 선택을 처리합니다."""
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    user_input = user_inputs.get(user_id, "")

    if query.data == 'place':
        place_impl(user_input)

    elif query.data == 'home':
        result = home(user_input)

    elif query.data == 'homesave':
        result = homesave(user_input)

    elif query.data == 'info':
        result = "ex) 장소명 초성"
        q, cons = parse_consonants_q(user_input)
        result = info(q, cons)

    elif query.data == 'telno':
        result = telno(user_input)

    elif query.data == 'goods':
        result = goods(str(user_input).split(' '))

    await query.edit_message_text(f"{result}")


def parse_consonants_q(user_input: str):
    args = user_input.split(' ')
    q = ' '.join(args[:-1])
    cons = args[-1]
    return (q, cons)


def place_impl(user_input: str):
    result = "ex) 1 장소명"

    args = user_input.split(' ')
    if len(args) >= 2:
        order_in = args[0]
        if order_in.isnumeric:
            order = int(args[0])
            q = ' '.join(args[1:])
            result = place(order, "100", q)
    return result


def homesavetelno_result(home: str, homesv: str, telno: str):
    result = f"""
> HOME URL
`{home}`

> HOME SAVE URL
`{homesv}`

> TELNO
`{telno}`
"""
    return result


def reply_result(msg: str, title: str):
    result = f"""
> {title}
`{msg}`
"""
    return result


async def handle_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """사용자의 입력을 처리하고 버튼을 표시합니다."""
    user_input = update.message.text
    user_id = update.effective_user.id

    # 사용자 입력 저장
    user_inputs[user_id] = user_input
    mode = 'MarkdownV2'

    try:
        # N번째-명소 유추
        if user_input.split(' ')[0].isnumeric():
            result = place_impl(user_input)
            await update.message.reply_text(reply_result(result, "명소"), parse_mode=mode)
        else:
            q, cons = parse_consonants_q(user_input)
            if isconsonants(cons):
                result = info(q, cons)
                await update.message.reply_text(reply_result(result, "초성"), parse_mode=mode)
            else:
                home, homesv, telno = homesavetelno(user_input)
                result = homesavetelno_result(home, homesv, telno)
                await update.message.reply_text(result, parse_mode=mode)

    except Exception:
        keyboard = [
            [InlineKeyboardButton("N번째-명소 9", callback_data='place')],
            [InlineKeyboardButton("홈URL 10", callback_data='home')],
            [InlineKeyboardButton("홈URL-저장 15", callback_data='homesave')],
            [InlineKeyboardButton("초성퀴즈 6", callback_data='info')],
            [InlineKeyboardButton("전화번호", callback_data='telno')]
            # [InlineKeyboardButton("상품코드(스토어)", callback_data='goods')]
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
    # app.add_handler(CommandHandler(["homesave", "f"], handle_homesave))
    app.add_handler(MessageHandler(filters.COMMAND, start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_input))
    app.add_handler(CallbackQueryHandler(button_callback))

    print('Bot Start ...')
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
