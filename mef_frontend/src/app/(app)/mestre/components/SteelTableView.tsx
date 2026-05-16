"use client";

import React from 'react';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

interface SteelRow {
  pos: string;
  phi_mm: number;
  count: number;
  length_m: number;
  total_length_m: number;
  weight_kg: number;
  type: string;
}

interface SteelTableProps {
  data: SteelRow[];
  totals: {
    total_ca50_kg: number;
    total_ca60_kg: number;
    grand_total_kg: number;
  };
}

export function SteelTableView({ data, totals }: SteelTableProps) {
  if (!data || data.length === 0) return null;

  return (
    <Card className="border-none shadow-none bg-transparent">
      <CardHeader className="px-0">
        <CardTitle className="text-lg font-bold flex items-center gap-2">
          <span className="w-2 h-6 bg-orange-500 rounded-full" />
          Tabela de Ferro (CA-50 / CA-60)
        </CardTitle>
      </CardHeader>
      <CardContent className="px-0">
        <div className="rounded-md border bg-white/50 backdrop-blur-sm overflow-hidden">
          <Table>
            <TableHeader className="bg-slate-100/50">
              <TableRow>
                <TableHead className="w-[80px]">Posição</TableHead>
                <TableHead>Bitola (Φ)</TableHead>
                <TableHead className="text-center">Qtd</TableHead>
                <TableHead className="text-right">Unit. (cm)</TableHead>
                <TableHead className="text-right">Total (m)</TableHead>
                <TableHead className="text-right">Peso (kg)</TableHead>
                <TableHead className="text-center">Aço</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {data.map((row) => (
                <TableRow key={row.pos} className="hover:bg-slate-50/50">
                  <TableCell className="font-bold">{row.pos}</TableCell>
                  <TableCell>{row.phi_mm.toFixed(1)} mm</TableCell>
                  <TableCell className="text-center">{row.count}</TableCell>
                  <TableCell className="text-right">{(row.length_m * 100).toFixed(0)}</TableCell>
                  <TableCell className="text-right">{row.total_length_m.toFixed(2)}</TableCell>
                  <TableCell className="text-right font-medium">{row.weight_kg.toFixed(2)}</TableCell>
                  <TableCell className="text-center">
                    <Badge variant={row.type === "CA-50" ? "default" : "secondary"} className="text-[10px]">
                      {row.type}
                    </Badge>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>

        <div className="grid grid-cols-3 gap-4 mt-4">
          <div className="p-3 rounded-lg bg-orange-50 border border-orange-100">
            <p className="text-[10px] text-orange-600 uppercase font-bold">Total CA-50</p>
            <p className="text-xl font-black text-orange-900">{totals.total_ca50_kg.toFixed(2)} <span className="text-sm font-normal">kg</span></p>
          </div>
          <div className="p-3 rounded-lg bg-blue-50 border border-blue-100">
            <p className="text-[10px] text-blue-600 uppercase font-bold">Total CA-60</p>
            <p className="text-xl font-black text-blue-900">{totals.total_ca60_kg.toFixed(2)} <span className="text-sm font-normal">kg</span></p>
          </div>
          <div className="p-3 rounded-lg bg-slate-900 text-white shadow-lg shadow-slate-200">
            <p className="text-[10px] text-slate-400 uppercase font-bold">Peso Total Projeto</p>
            <p className="text-xl font-black">{totals.grand_total_kg.toFixed(2)} <span className="text-sm font-normal">kg</span></p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
