from uuid import UUID

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect

from app.schemas.sessions import (
    SessionCreateRequest,
    SessionEndRequest,
    SessionReportResponse,
    SessionResponse,
    SessionTurn,
)
from app.services.session_service import session_service
from app.services.providers import get_stt_provider, get_tts_provider

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.post("", response_model=SessionResponse)
def create_session(payload: SessionCreateRequest) -> SessionResponse:
    session = session_service.create(payload)
    return SessionResponse(**{k: v for k, v in session.items() if k != "turns"})


@router.post("/{session_id}/end", response_model=SessionReportResponse)
async def end_session(session_id: UUID, payload: SessionEndRequest) -> SessionReportResponse:
    _ = payload
    try:
        return await session_service.end(session_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/{session_id}/report", response_model=SessionReportResponse)
def get_report(session_id: UUID) -> SessionReportResponse:
    try:
        return session_service.report(session_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.websocket("/{session_id}/voice")
async def voice_socket(websocket: WebSocket, session_id: UUID) -> None:
    await websocket.accept()
    try:
        while True:
            payload = await websocket.receive_json()
            turn = SessionTurn(**payload)
            if not turn.text and turn.audio_base64:
                import base64

                audio_bytes = base64.b64decode(turn.audio_base64)
                stt = get_stt_provider()
                try:
                    stt_result = await stt.transcribe(
                        audio_bytes=audio_bytes,
                        mime_type=turn.audio_mime_type or "audio/webm",
                        filename=turn.audio_filename or "audio.webm",
                    )
                    turn.text = stt_result.text
                except Exception as exc:
                    await websocket.send_json({"error": f"stt_failed: {exc}"})
                    continue

            if not turn.text:
                await websocket.send_json({"error": "empty_turn"})
                continue

            try:
                tutor_turn = await session_service.add_turn_and_reply(session_id, turn)
            except Exception as exc:
                await websocket.send_json({"error": f"llm_failed: {exc}"})
                continue
            try:
                audio = await get_tts_provider().speak(
                    text=tutor_turn["text"],
                    voice_id="",
                    lang_style=turn.language_style,
                )
                import base64

                tutor_turn["audio_base64"] = base64.b64encode(audio).decode("utf-8")
            except Exception:
                tutor_turn["audio_base64"] = None
            await websocket.send_json(tutor_turn)
    except WebSocketDisconnect:
        return
    except KeyError:
        await websocket.send_json({"error": "session_not_found"})
        await websocket.close()
    except Exception as exc:
        await websocket.send_json({"error": f"voice_socket_failed: {exc}"})
        await websocket.close()
