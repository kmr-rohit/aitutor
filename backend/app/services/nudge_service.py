from datetime import UTC, datetime
from uuid import UUID


class NudgeService:
    def __init__(self) -> None:
        self.streaks: dict[UUID, dict] = {}
        self.nudges: dict[UUID, dict] = {}

    def schedule(self, user_id: UUID, nudge_id: UUID, channel: str, message: str, scheduled_for: datetime) -> None:
        self.nudges[nudge_id] = {
            "user_id": user_id,
            "channel": channel,
            "message": message,
            "scheduled_for": scheduled_for,
            "status": "scheduled",
        }

    def acknowledge(self, user_id: UUID, nudge_id: UUID) -> dict:
        nudge = self.nudges.get(nudge_id)
        if not nudge:
            raise KeyError("Nudge not found")
        if nudge["user_id"] != user_id:
            raise PermissionError("Nudge does not belong to user")

        nudge["status"] = "acknowledged"
        row = self.streaks.get(user_id, {"current_streak_days": 0, "last_active_at": None})

        today = datetime.now(UTC).date()
        last = row["last_active_at"].date() if row["last_active_at"] else None
        if last == today:
            pass
        elif last is None or (today - last).days == 1:
            row["current_streak_days"] += 1
        else:
            row["current_streak_days"] = 1

        row["last_active_at"] = datetime.now(UTC)
        self.streaks[user_id] = row
        return row

    def get_streak(self, user_id: UUID) -> dict:
        return self.streaks.get(user_id, {"current_streak_days": 0, "last_active_at": None})


nudge_service = NudgeService()
