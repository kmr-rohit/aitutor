# R&D Blueprint - AI Learning Companion

## Objective
Build a low-cost (<$30/month initial) voice-first interview prep coach that teaches in simple Hinglish and improves consistency via reminders.

## R&D Tracks

### 1) Speech Pipeline Quality
- Benchmark STT:
  - `faster-whisper` local model vs Sarvam STT for Hindi-English mixed technical terms.
- Benchmark TTS:
  - Sarvam TTS vs Piper/Coqui fallback for clarity and naturalness.
- Dataset:
  - 20 short clips (HLD terms, language concepts, mixed Hindi-English prompts).
- Success criteria:
  - >=90% technical keyword capture.
  - Subjective naturalness >=4/5 by learner.

### 2) Tutor Pedagogy Quality
- Prompt patterns:
  - `simple explanation -> analogy -> software example -> check question`.
- Evaluate across 3 modes:
  - HLD practice, language deep dive, concept learning.
- Success criteria:
  - >=80% turns rated easy-to-understand.
  - >=70% sessions produce actionable next-step tasks.

### 3) Latency + Cost
- Track p50/p95 response start latency in conversation loop.
- Simulate 30 min/day usage and estimate monthly cost.
- Success criteria:
  - p95 <=2.5 seconds response start.
  - Run-rate remains below target budget for one learner.

### 4) Habit Loop Effectiveness
- Reminder experiments:
  - A/B `10-min quick win` vs `full session prompt` copy.
- Track active days/week and streak continuity.
- Success criteria:
  - >=4 active learning days/week.

## Risk Register
- Hinglish STT errors on technical words.
- Voice latency on low bandwidth mobile networks.
- Overly generic tutor output reducing interview usefulness.
- Reminder fatigue causing drop-off.

## Mitigation
- Dynamic phrase boost list for domain terms.
- Provider fallback routing (Sarvam <-> open source).
- Rubric-based feedback templates for HLD/language answers.
- Adaptive nudge frequency based on response behavior.
