# Состояния диалогов
EVENT_NAME, EVENT_DATE, EVENT_TIME, EVENT_DESC, DELETE_NAME = range(5)
EDIT_NAME, EDIT_DATE, EDIT_TIME = range(5, 8)

# Тексты справки
HELP_TEXT = (
    "Доступные команды:\n"
    "/start — приветствие\n"
    "/help — эта справка\n"
    "/register — зарегистрироваться\n"
    "/add — создать событие\n"
    "/events — показать все события\n"
    "/edit — редактировать событие\n"
    "/delete — удалить событие\n"
    "/cancel — отменить текущий диалог"
)

# Тексты ошибок валидации
INVALID_DATE = "Неверный формат. Введите дату как ГГГГ-ММ-ДД:"
INVALID_TIME = "Неверный формат. Введите время как ЧЧ:ММ:"