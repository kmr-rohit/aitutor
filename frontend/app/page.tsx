"use client";

import { motion } from "framer-motion";

import SessionPanel from "@/components/SessionPanel";

export default function HomePage() {
  return (
    <main className="viewport">
      <motion.section
        className="phone-shell"
        initial={{ opacity: 0, y: 24, scale: 0.96 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        transition={{ duration: 0.55, ease: "easeOut" }}
      >
        <SessionPanel />
      </motion.section>
    </main>
  );
}
