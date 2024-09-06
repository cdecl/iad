import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

import os
from run import place, home, fav
from dotenv import load_dotenv

# 로깅 설정
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


# /start 및 /help 명령어 핸들러
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    command_list = ["/start", "/place", "/home", "/fav"]
    response = "사용 가능한 명령어 목록:\n" + "\n".join(command_list)
    await update.message.reply_text(response)


# /r12 명령어 핸들러
async def handle_place(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if len(context.args) >= 2:
            order_in = context.args[0]

            if not order_in.isnumeric:
                raise Exception("순서값 에러")
            order = int(context.args[0])
            q = ' '.join(context.args[1:])

            r = place(order, "100", q)
            await update.message.reply_text(f'{r}')
        else:
            raise Exception("질문 형식 오류")
    except Exception as e:
        await update.message.reply_text(f"except : {e}")


async def handle_home(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        q = ' '.join(context.args)
        if not q:
            raise Exception('질문 오류')

        r = home(q)
        await update.message.reply_text(f'{r}')

    except Exception as e:
        await update.message.reply_text(f"except : {e}")


async def handle_fav(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        q = ' '.join(context.args)
        if not q:
            raise Exception('질문 오류')

        r = fav(q)
        await update.message.reply_text(f'{r}')

    except Exception as e:
        await update.message.reply_text(f"except : {e}")


# 알 수 없는 명령어 처리
async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("'/help' 입력 도움말 확인")


def main():
    load_dotenv()
    TOKEN = os.getenv('TELEGRAM_TOKEN')
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler(["start", "help"], start))
    app.add_handler(CommandHandler("place", handle_place))
    app.add_handler(CommandHandler("home", handle_home))
    app.add_handler(CommandHandler("fav", handle_fav))
    app.add_handler(MessageHandler(filters.COMMAND, unknown))

    print('봇이 실행되었습니다...')
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
