from telegram import Update
from telegram.ext import ContextTypes


async def register(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    conn = context.bot_data['conn']

    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO users (user_id, username) VALUES (%s, %s) "
            "ON CONFLICT (user_id) DO NOTHING",
            (user.id, user.username)
        )
    conn.commit()

    await update.message.reply_text(
        f"Вы зарегистрированы! Ваш ID: {user.id}"
    )


def is_registered(conn, user_id):
    with conn.cursor() as cur:
        cur.execute("SELECT 1 FROM users WHERE user_id = %s", (user_id,))
        return cur.fetchone() is not None    