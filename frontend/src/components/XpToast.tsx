"use client";

import { useEffect, useState } from "react";

interface XpToastProps {
  xp: number;
  onDone: () => void;
}

export default function XpToast({ xp, onDone }: XpToastProps) {
  const [visible, setVisible] = useState(true);

  useEffect(() => {
    const timer = setTimeout(() => {
      setVisible(false);
      setTimeout(onDone, 300);
    }, 1500);
    return () => clearTimeout(timer);
  }, [onDone]);

  return (
    <div
      className={`fixed top-16 left-1/2 -translate-x-1/2 z-50 transition-all duration-300 ${
        visible ? "opacity-100 translate-y-0" : "opacity-0 -translate-y-4"
      }`}
    >
      <div className="bg-blue-600 text-white px-5 py-2.5 rounded-full shadow-lg shadow-blue-600/30 font-bold text-sm flex items-center gap-2">
        <span>✨</span>
        <span>+{xp} XP</span>
      </div>
    </div>
  );
}
