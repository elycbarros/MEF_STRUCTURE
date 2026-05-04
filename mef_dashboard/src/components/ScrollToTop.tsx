"use client";

import React, { useState, useEffect } from "react";
import { ArrowUp } from "lucide-react";
import { cn } from "@/lib/utils";

export function ScrollToTop() {
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    const toggleVisibility = () => {
      if (window.pageYOffset > 300) {
        setIsVisible(true);
      } else {
        setIsVisible(false);
      }
    };

    window.addEventListener("scroll", toggleVisibility);
    return () => window.removeEventListener("scroll", toggleVisibility);
  }, []);

  const scrollToTop = () => {
    window.scrollTo({
      top: 0,
      behavior: "smooth",
    });
  };

  return (
    <button
      onClick={scrollToTop}
      className={cn(
        "fixed bottom-8 right-8 z-50 flex h-12 w-12 items-center justify-center rounded-full bg-white shadow-2xl transition-all duration-300 hover:scale-110 active:scale-95 border border-[#e0e7ef]",
        isVisible ? "translate-y-0 opacity-100" : "translate-y-20 opacity-0 pointer-events-none"
      )}
      aria-label="Voltar ao topo"
    >
      <div className="absolute inset-0 rounded-full bg-gradient-to-tr from-[#f8fafc] to-white opacity-0 transition-opacity hover:opacity-100" />
      <ArrowUp className="relative h-6 w-6 text-[#1a1f2e] transition-transform hover:-translate-y-1" />
      
      {/* Subtle pulse effect */}
      <div className="absolute -inset-1 rounded-full bg-blue-500/5 blur-xl animate-pulse" />
    </button>
  );
}
