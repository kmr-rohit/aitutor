from app.schemas.practice import PracticeEvaluateRequest, PracticeEvaluateResponse


def _bounded(value: int) -> int:
    return max(1, min(value, 10))


class PracticeService:
    def evaluate_hld(self, payload: PracticeEvaluateRequest) -> PracticeEvaluateResponse:
        answer = payload.answer.lower()
        clarity = 8 if any(k in answer for k in ["requirement", "assumption", "scope"]) else 6
        tradeoffs = 8 if "tradeoff" in answer or "latency" in answer or "cost" in answer else 5
        scalability = 8 if any(k in answer for k in ["shard", "cache", "replica", "queue"]) else 5

        scores = {
            "clarity": _bounded(clarity),
            "tradeoffs": _bounded(tradeoffs),
            "scalability": _bounded(scalability),
        }
        overall = round(sum(scores.values()) / len(scores))

        return PracticeEvaluateResponse(
            overall_score=overall,
            scores=scores,
            strengths=[
                "Structured attempt with architecture framing",
                "Shows awareness of scaling concerns",
            ],
            improvements=[
                "State assumptions and constraints upfront",
                "Quantify tradeoffs with metrics",
            ],
            sample_better_answer=(
                "Pehle requirements clear karte hain: read/write ratio, latency target, and availability SLA. "
                "Then high-level components define karenge with queue + cache + DB replication and tradeoff discussion."
            ),
        )

    def evaluate_language(self, payload: PracticeEvaluateRequest) -> PracticeEvaluateResponse:
        answer = payload.answer.lower()
        correctness = 8 if any(k in answer for k in ["time complexity", "memory", "edge case"]) else 6
        depth = 8 if any(k in answer for k in ["internals", "runtime", "compiler", "garbage collector"]) else 5
        communication = 8 if len(payload.answer.split()) > 40 else 6

        scores = {
            "correctness": _bounded(correctness),
            "depth": _bounded(depth),
            "communication": _bounded(communication),
        }
        overall = round(sum(scores.values()) / len(scores))

        return PracticeEvaluateResponse(
            overall_score=overall,
            scores=scores,
            strengths=["Concept explanation is mostly clear", "Covers practical implications"],
            improvements=["Include one concrete code example", "Call out edge cases explicitly"],
            sample_better_answer=(
                "Simple terms me: pehle concept define karo, phir ek chhota code snippet, "
                "fir complexity aur edge cases discuss karo interview style me."
            ),
        )


practice_service = PracticeService()
