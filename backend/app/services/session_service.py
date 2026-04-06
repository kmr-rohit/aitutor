from datetime import UTC, datetime
from uuid import UUID, uuid4

from app.schemas.common import SessionMode
from app.schemas.sessions import SessionCreateRequest, SessionReportResponse, SessionTurn
from app.services.providers import get_llm_provider
from app.services.report_generator import generate_deep_report
from app.services.text_normalizer import normalize_hinglish_text
from app.services.text_refiner import refine_hinglish_list, refine_hinglish_text


class SessionService:
    def __init__(self) -> None:
        self.sessions: dict[UUID, dict] = {}
        self.reports: dict[UUID, SessionReportResponse] = {}

    def create(self, payload: SessionCreateRequest) -> dict:
        session_id = uuid4()
        session = {
            "id": session_id,
            "mode": payload.mode,
            "topic": payload.topic,
            "difficulty": payload.difficulty,
            "created_at": datetime.now(UTC),
            "status": "active",
            "turns": [],
        }
        self.sessions[session_id] = session
        return session

    async def add_turn_and_reply(self, session_id: UUID, turn: SessionTurn) -> dict:
        if session_id not in self.sessions:
            raise KeyError("Session not found")

        session = self.sessions[session_id]
        learner_text = (turn.text or "").strip()
        if len(learner_text) > 1200:
            learner_text = learner_text[:1200]
        session["turns"].append(
            {
                "role": turn.role,
                "text": learner_text,
                "language_style": turn.language_style,
            }
        )

        llm = get_llm_provider()
        result = await llm.respond(
            context=session["turns"],
            mode=session["mode"].value if isinstance(session["mode"], SessionMode) else str(session["mode"]),
            rubric={"clarity": 10, "tradeoffs": 10, "scalability": 10},
        )

        answer = await refine_hinglish_text(result.answer)
        hints = await refine_hinglish_list(result.hints)
        followups = await refine_hinglish_list(result.followups)

        tutor_turn = {
            "role": "tutor",
            "text": answer,
            "hints": hints,
            "followups": followups,
        }
        session["turns"].append({"role": "tutor", "text": answer})
        return tutor_turn

    async def end(self, session_id: UUID) -> SessionReportResponse:
        if session_id not in self.sessions:
            raise KeyError("Session not found")

        session = self.sessions[session_id]
        session["status"] = "completed"
        deep_report = await generate_deep_report(topic=session["topic"], turns=session["turns"])

        report = SessionReportResponse(
            session_id=session_id,
            summary=normalize_hinglish_text(
                f"Session on {session['topic']} completed with focus on interview clarity. "
                "Agar aap consistent raho to zyada improvement dikhega."
            ),
            strengths=["Structured thinking", "Asked clarifying questions"],
            improvement_areas=["Quantify tradeoffs", "Explain bottlenecks earlier"],
            next_20_min_plan=[
                "Revise requirements gathering template",
                "Practice one caching tradeoff example",
                "Answer 3 rapid-fire follow-up questions",
            ],
            quiz_questions=[
                "When do you prefer read-replicas over sharding?",
                "How do you identify single points of failure?",
                "What metrics validate scalability assumptions?",
            ],
            rubric_scores={"clarity": 7, "tradeoffs": 6, "scalability": 7},
            detailed_report=deep_report,
        )
        self.reports[session_id] = report
        return report

    def report(self, session_id: UUID) -> SessionReportResponse:
        if session_id not in self.reports:
            raise KeyError("Report not found")
        return self.reports[session_id]


session_service = SessionService()
