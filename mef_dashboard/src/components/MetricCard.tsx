"use client";

import React from 'react';
import { motion } from 'framer-motion';

interface MetricCardProps {
  label: string;
  value: string;
  unit?: string;
  status?: 'ok' | 'warn' | 'danger';
  trend?: string;
}

export function MetricCard({ label, value, unit, status = 'ok', trend }: MetricCardProps) {
  const statusColors = {
    ok: 'bg-apple-green',
    warn: 'bg-apple-orange',
    danger: 'bg-apple-red',
  };

  return (
    <motion.div 
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="glass p-5 rounded-apple shadow-apple flex flex-col gap-1 min-w-[200px]"
    >
      <span className="text-slate-600 text-xs font-semibold uppercase tracking-wider">{label}</span>
      <div className="flex items-baseline gap-1 mt-1">
        <span className="text-2xl font-bold text-slate-900">{value}</span>
        {unit && <span className="text-slate-600 text-sm font-medium">{unit}</span>}
      </div>
      <div className="flex items-center gap-2 mt-2">
        <div className={`w-2 h-2 rounded-full ${statusColors[status]}`} />
        <span className="text-[11px] font-bold text-slate-600 uppercase tracking-tighter">
          {status === 'ok' ? 'Dentro do Limite' : status === 'warn' ? 'Atenção' : 'Crítico'}
        </span>
        {trend && <span className="text-[11px] text-apple-blue font-bold ml-auto">{trend}</span>}
      </div>
    </motion.div>
  );
}
