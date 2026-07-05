from telegram.error import BadRequest, TelegramError
from functools import wraps
from telegram import ChatAction, ParseMode


def send_to_list(bot, send_to, message, markdown=False, html=False):
    for user_id in set(send_to):
        try:
            if html:
                bot.send_message(user_id, message, parse_mode=ParseMode.HTML)
            elif markdown:
                bot.send_message(user_id, message, parse_mode=ParseMode.MARKDOWN)
            else:
                bot.send_message(user_id, message)
        except TelegramError:
            pass


def send_message(message, text, *args, **kwargs):
    try:
        return message.reply_text(text, *args, **kwargs)
    except BadRequest as err:
        if str(err) == "Reply message not found":
            return message.reply_text(text, quote=False, *args, **kwargs)


def typing_action(func):
    """Sends typing action while processing func command."""

    @wraps(func)
    def command_func(update, context, *args, **kwargs):
        context.bot.send_chat_action(
            chat_id=update.effective_chat.id, action=ChatAction.TYPING,
        )
        return func(update, context, *args, **kwargs)

    return command_func
