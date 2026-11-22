"""
Обработчики встреч: приглашения, ответы на приглашения, текстовые сообщения.
"""
import html
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from events.models import Meeting
from services import (
    meeting_context, create_context, edit_context, read_context, delete_context,
    get_user, get_menu_keyboard,
    _process_meeting_step, _finalize_meeting, STATUS_EMOJI,
)

# calendar устанавливается динамически в main.py
import services as _services


def invite_meeting(update, context):
    """Начало создания встречи."""
    user = update.effective_user
    meeting_context[user.id] = {"step": "title"}
    update.message.reply_text("Создание встречи.\nВведите название встречи:")


def my_meetings(update, context):
    """Обработчик команды /my_meetings."""
    user = update.effective_user
    meetings = Meeting.objects.filter(
        participant_id=user.id,
        status__in=['pending', 'confirmed']
    ).order_by('date', 'time')

    if not meetings:
        update.message.reply_text("У вас нет запланированных встреч.")
        return

    lines = ["Ваши встречи:\n"]
    for m in meetings:
        emoji = STATUS_EMOJI.get(m.status, "•")
        lines.append(
            f"{emoji} {html.escape(m.title)}\n"
            f"   Дата: {html.escape(str(m.date))}  Время: {html.escape(str(m.time))}\n"
            f"   Организатор: {html.escape(m.organizer_name)}\n"
            f"   Статус: {html.escape(m.get_status_display())}\n"
        )
    update.message.reply_text("\n".join(lines))


def meeting_message_handler(update, context):
    """Обработчик текстовых сообщений для встреч."""
    user = update.effective_user
    if user.id not in meeting_context:
        return False
    return _process_meeting_step(update, context, meeting_context[user.id], update.message.text)


def meeting_callback_handler(update, context):
    """Обработчик кнопок подтверждения/отклонения встречи."""
    query = update.callback_query
    try:
        query.answer()
    except Exception:
        pass  # Кнопка истекла или невалидна

    action, meeting_id = query.data.split("_")
    meeting_id = int(meeting_id)

    try:
        meeting = Meeting.objects.get(id=meeting_id)
    except Meeting.DoesNotExist:
        query.edit_message_text("Встреча не найдена.")
        return

    if action == "confirm":
        meeting.status = 'confirmed'
        meeting.save()
        query.edit_message_text("Вы подтвердили встречу!")
        _notify_organizer(context, meeting, "подтвердил")
    elif action == "decline":
        meeting.status = 'cancelled'
        meeting.save()
        query.edit_message_text("Вы отклонили встречу.")
        _notify_organizer(context, meeting, "отклонил")


def _notify_organizer(context, meeting, action):
    """Отправляет уведомление организатору о решении участника."""
    try:
        context.bot.send_message(
            chat_id=meeting.organizer_id,
            text=f"Участник {action} встречу «{meeting.title}» "
                 f"на {meeting.date} в {meeting.time}."
        )
    except Exception:
        pass


def text_handler(update, context):
    """Обработчик текстовых сообщений для многошаговых команд."""
    user = update.effective_user

    # Просмотр события
    if user.id in read_context:
        text = update.message.text.strip()
        try:
            event_id = int(text)
            event = _services.calendar.read_event(user.id, event_id)
            if event:
                public_status = "да" if event.get("is_public") else "нет"
                text_response = (
                    f"Событие №{event['id']}\n"
                    f"Название: {event['name']}\n"
                    f"Дата: {event['date']}\n"
                    f"Время: {event['time']}\n"
                    f"Описание: {event['details']}\n"
                    f"Публичное: {public_status}"
                )
                button_text = "Сделать приватным" if event.get("is_public") else "Сделать публичным"
                keyboard = [[InlineKeyboardButton(button_text, callback_data=f"public_{event_id}")]]
                update.message.reply_text(text_response, reply_markup=InlineKeyboardMarkup(keyboard))
            else:
                update.message.reply_text(
                    f"❌ Событие с номером {event_id} не найдено.",
                    reply_markup=get_menu_keyboard()
                )
        except ValueError:
            update.message.reply_text(
                "❌ Неверный формат. Введите только число (ID события).",
                reply_markup=get_menu_keyboard()
            )
        del read_context[user.id]
        return

    # Удаление события
    if user.id in delete_context:
        text = update.message.text.strip()
        try:
            event_id = int(text)
            success = _services.calendar.delete_event(user.id, event_id)

            if success:
                tg_user = get_user(user.id)
                if tg_user:
                    tg_user.events_cancelled += 1
                    remaining_events = _services.calendar.get_all_events(user.id)
                    if not remaining_events:
                        tg_user.events_created = 0
                        tg_user.save()
                        _services.calendar.reset_id_sequence()
                    else:
                        tg_user.save()

                update.message.reply_text(
                    f"✅ Событие №{event_id} удалено.",
                    reply_markup=get_menu_keyboard()
                )
            else:
                update.message.reply_text(
                    f"❌ Событие с номером {event_id} не найдено или не принадлежит вам.",
                    reply_markup=get_menu_keyboard()
                )
        except ValueError:
            update.message.reply_text(
                "❌ Неверный формат. Введите только число (ID события).",
                reply_markup=get_menu_keyboard()
            )
        del delete_context[user.id]
        return

    # Создание события
    if user.id in create_context:
        text = update.message.text.strip()
        parts = text.split()

        if len(parts) >= 3:
            event_name = " ".join(parts[:-2])
            event_date = parts[-2]
            event_time = parts[-1]

            try:
                event_id = _services.calendar.create_event(
                    user.id, event_name, event_date, event_time, ""
                )
                tg_user = get_user(user.id)
                if tg_user:
                    tg_user.events_created += 1
                    tg_user.save()

                update.message.reply_text(
                    f"✅ Событие «{html.escape(event_name)}» создано на {html.escape(event_date)} в {html.escape(event_time)} (№{event_id}).",
                    reply_markup=get_menu_keyboard()
                )
            except Exception as e:
                update.message.reply_text(
                    f"❌ Ошибка при создании события: {e}",
                    reply_markup=get_menu_keyboard()
                )
        else:
            update.message.reply_text(
                "Недостаточно данных. Введите название, дату и время:\n"
                "Пример: Встреча 2026-11-15 15:30",
                reply_markup=get_menu_keyboard()
            )
        del create_context[user.id]
        return

    # Редактирование события
    if user.id in edit_context:
        text = update.message.text.strip()
        parts = text.split()

        if len(parts) >= 4:
            event_id = int(parts[0])
            event_date = parts[1]
            event_time = parts[2]
            event_name = " ".join(parts[3:])

            try:
                success = _services.calendar.edit_event(
                    user.id, event_id,
                    event_name=event_name,
                    event_date=event_date,
                    event_time=event_time
                )

                if success:
                    tg_user = get_user(user.id)
                    if tg_user:
                        tg_user.events_edited += 1
                        remaining_events = _services.calendar.get_all_events(user.id)
                        if not remaining_events:
                            tg_user.events_created = 0
                        tg_user.save()

                    update.message.reply_text(
                        f"✅ Событие №{event_id} отредактировано:\n"
                        f"Название: {html.escape(event_name)}\n"
                        f"Дата: {html.escape(event_date)}\n"
                        f"Время: {html.escape(event_time)}",
                        reply_markup=get_menu_keyboard()
                    )
                else:
                    update.message.reply_text(
                        f"❌ Событие с номером {event_id} не найдено или не принадлежит вам.",
                        reply_markup=get_menu_keyboard()
                    )
            except ValueError:
                update.message.reply_text(
                    "❌ Неверный формат ID. Введите число.",
                    reply_markup=get_menu_keyboard()
                )
            except Exception as e:
                update.message.reply_text(
                    f"❌ Ошибка при редактировании: {e}",
                    reply_markup=get_menu_keyboard()
                )
        else:
            update.message.reply_text(
                "Недостаточно данных. Введите ID, дату, время и название:\n"
                "Пример: 1 2026-12-01 10:00 Новое название",
                reply_markup=get_menu_keyboard()
            )
        del edit_context[user.id]
        return

    # Обработка встреч
    meeting_message_handler(update, context)
