"use client";

import { useState } from "react";

import { motion } from "framer-motion";

import { scheduleNudge } from "@/lib/api";

export default function NudgePanel() {
  const [userId, setUserId] = useState("11111111-1111-1111-1111-111111111111");
  const [message, setMessage] = useState("10 minute quick win: aaj HLD ka ek flow explain karo.");
  const [time, setTime] = useState(new Date(Date.now() + 30 * 60 * 1000).toISOString().slice(0, 16));
  const [status, setStatus] = useState("");

  const onSchedule = async () => {
    try {
      const payload = {
        user_id: userId,
        channel: "whatsapp",
        message,
        scheduled_for: new Date(time).toISOString(),
      };
      const res = await scheduleNudge(payload);
      setStatus(`Scheduled: ${res.nudge_id}`);
    } catch (err) {
      setStatus(err instanceof Error ? err.message : "Failed to schedule");
    }
  };

  return (
    <motion.section
      className="tool-card"
      initial={{ opacity: 0, y: 12 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      transition={{ duration: 0.35, delay: 0.05 }}
    >
      <h3>Daily Nudge</h3>
      <p className="card-sub">Schedule a WhatsApp accountability reminder.</p>

      <label>
        <span>User ID</span>
        <input value={userId} onChange={(e) => setUserId(e.target.value)} />
      </label>
      <label>
        <span>Message</span>
        <input value={message} onChange={(e) => setMessage(e.target.value)} />
      </label>
      <label>
        <span>Time</span>
        <input type="datetime-local" value={time} onChange={(e) => setTime(e.target.value)} />
      </label>

      <div className="row actions">
        <button className="btn btn-ghost" onClick={onSchedule}>
          Schedule
        </button>
      </div>

      {status && <p className="status-text">{status}</p>}
    </motion.section>
  );
}
