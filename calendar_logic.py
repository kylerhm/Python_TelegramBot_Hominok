from __future__ import annotations


class Calendar:
    def __init__(self, conn):
        self.conn = conn

    def create_event(self, user_id, name, date, time, description=""):
        with self.conn.cursor() as cur:
            cur.execute(
                "INSERT INTO events (user_id, name, date, time, description) "
                "VALUES (%s, %s, %s, %s, %s)",
                (user_id, name, date, time, description)
            )
        self.conn.commit()
        return f"Событие «{name}» создано на {date} в {time}."

    def get_events(self, user_id):
        with self.conn.cursor() as cur:
            cur.execute(
                "SELECT name, date, time, description FROM events "
                "WHERE user_id = %s ORDER BY date, time",
                (user_id,)
            )
            rows = cur.fetchall()
        if not rows:
            return "У вас пока нет событий."
        lines = []
        for name, date, time, description in rows:
            if hasattr(date, "strftime"):
                date_str = date.strftime("%d.%m.%Y")
            else:
                date_str = str(date)
            if hasattr(time, "strftime"):
                time_str = time.strftime("%H:%M")
            else:
                time_str = str(time)
            desc = f" ({description})" if description else ""
            lines.append(f"📅 {date_str} в {time_str} — {name}{desc}")
        return "\n".join(lines)

    def edit_event(self, user_id, name, new_date=None, new_time=None):
        with self.conn.cursor() as cur:
            cur.execute(
                "UPDATE events SET "
                "date = COALESCE(%s, date), "
                "time = COALESCE(%s, time) "
                "WHERE user_id = %s AND lower(name) = lower(%s) "
                "RETURNING date, time",
                (new_date, new_time, user_id, name)
            )
            row = cur.fetchone()
        self.conn.commit()
        if row:
            return f"Событие «{name}» обновлено: {row[0]} {row[1]}."
        return f"Событие «{name}» не найдено."

    def delete_event(self, user_id, name):
        with self.conn.cursor() as cur:
            cur.execute(
                "DELETE FROM events WHERE user_id = %s AND lower(name) = lower(%s)",
                (user_id, name)
            )
            deleted = cur.rowcount
        self.conn.commit()
        if deleted:
            return f"Событие «{name}» удалено."
        return f"Событие «{name}» не найдено."