export const formatNumberBR = (num: number | undefined | null, decimals: number = 2) => {
  if (num === null || num === undefined || isNaN(num)) return "0,00";
  return new Intl.NumberFormat('pt-BR', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  }).format(num);
};

export const normalizeBeamDiagram = (diagrams: any) => {
  if (!diagrams || !diagrams.x_m) return [];
  return diagrams.x_m.map((x: number, i: number) => ({
    name: `${formatNumberBR(x)}m`,
    x: Number(x) || 0,
    moment: Number(diagrams.M_kNm?.[i]) || 0,
    shear: Number(diagrams.V_kN?.[i]) || 0,
  }));
};

export const cn = (...classes: (string | boolean | undefined | null)[]) => {
  return classes.filter(Boolean).join(" ");
};
