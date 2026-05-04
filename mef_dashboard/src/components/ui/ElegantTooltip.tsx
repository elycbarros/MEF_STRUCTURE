"use client";

import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Info } from "lucide-react";

interface ElegantTooltipProps {
  content: string;
  children: React.ReactNode;
}

export function ElegantTooltip({ content, children }: ElegantTooltipProps) {
  const [isVisible, setIsVisible] = useState(false);

  return (
    <div 
      className="relative inline-flex items-center group"
      onMouseEnter={() => setIsVisible(true)}
      onMouseLeave={() => setIsVisible(false)}
    >
      {children}
      <AnimatePresence>
        {isVisible && (
          <motion.div
            initial={{ opacity: 0, y: 5, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 5, scale: 0.95 }}
            transition={{ duration: 0.15, ease: "easeOut" }}
            className="absolute z-[100] bottom-full left-1/2 -translate-x-1/2 mb-2 w-48 p-3 rounded-xl bg-slate-900/95 backdrop-blur-md text-white text-[10px] leading-relaxed shadow-2xl pointer-events-none border border-white/10"
          >
            <div className="relative">
              {content}
              {/* Arrow */}
              <div className="absolute top-full left-1/2 -translate-x-1/2 border-8 border-transparent border-t-slate-900/95" />
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
