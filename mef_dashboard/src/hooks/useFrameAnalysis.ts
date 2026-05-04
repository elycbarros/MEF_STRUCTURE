import { useState } from "react";

export function useFrameAnalysis() {
  const [windParams, setWindParams] = useState({
    v0: 30,
    altura_total: 30,
    largura: 12,
    profundidade: 18,
    step: 3,
    categoria: 2,
    classe: "B",
    s1: 1,
    s3: 1,
    is_dynamic: false,
    f1: 0.5,
    zeta: 0.01,
    total_p_kN: 12000,
  });

  const [frameResults, setFrameResults] = useState<any>(null);
  const [stabilityResults, setStabilityResults] = useState<any>(null);
  const [windResults, setWindResults] = useState<any>(null);

  return {
    windParams,
    setWindParams,
    frameResults,
    setFrameResults,
    stabilityResults,
    setStabilityResults,
    windResults,
    setWindResults
  };
}
