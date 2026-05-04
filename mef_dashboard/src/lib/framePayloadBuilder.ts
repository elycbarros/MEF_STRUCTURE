import { Pillar } from "@/hooks/useRadierAnalysis";

export function buildFramePremiumPayload(
  pillars: Pillar[],
  params: { fck: number },
  windParams: { v0: number; categoria: number; largura: number; altura_total: number; step: number },
) {
  const floorHeight = Math.max(Number(windParams.step) || 3, 1);
  const nFloors = Math.max(Math.round((Number(windParams.altura_total) || 30) / floorHeight), 1);
  const nodes: Array<{ id: number; x: number; y: number; z: number }> = [];
  const members: Array<{
    id: number;
    node_i: number;
    node_j: number;
    type: "column" | "beam";
    section: { b: number; h: number; E: number; G: number };
  }> = [];
  const loads: Array<{ node_id: number; Fx?: number; Fy?: number; Fz?: number }> = [];
  const supports: Record<number, number[]> = {};
  const nodeId = (pillarIndex: number, floor: number) => pillarIndex * (nFloors + 1) + floor + 1;
  const concreteE = 5600 * Math.sqrt(Math.max(params.fck, 20)) * 1e6;
  const concreteG = concreteE / 2.4;

  pillars.forEach((pillar, pillarIndex) => {
    for (let floor = 0; floor <= nFloors; floor += 1) {
      const id = nodeId(pillarIndex, floor);
      nodes.push({ id, x: pillar.x, y: pillar.y, z: floor * floorHeight });
      if (floor === 0) supports[id] = [0, 1, 2, 3, 4, 5];
    }

    for (let floor = 0; floor < nFloors; floor += 1) {
      members.push({
        id: members.length + 1,
        node_i: nodeId(pillarIndex, floor),
        node_j: nodeId(pillarIndex, floor + 1),
        type: "column",
        section: { b: pillar.bx || 0.4, h: pillar.by || 0.4, E: concreteE, G: concreteG },
      });
    }

    loads.push({ node_id: nodeId(pillarIndex, nFloors), Fz: -(pillar.p_kN || 0) * 1000 });
  });

  const connectAlignedPillars = (axis: "x" | "y") => {
    const groupKey = axis === "x" ? "y" : "x";
    const sortKey = axis === "x" ? "x" : "y";
    const groups = new Map<string, Array<{ pillar: Pillar; index: number }>>();
    pillars.forEach((pillar, index) => {
      const key = Number(pillar[groupKey]).toFixed(3);
      groups.set(key, [...(groups.get(key) || []), { pillar, index }]);
    });

    groups.forEach((group) => {
      const ordered = group.sort((a, b) => Number(a.pillar[sortKey]) - Number(b.pillar[sortKey]));
      for (let i = 0; i < ordered.length - 1; i += 1) {
        for (let floor = 1; floor <= nFloors; floor += 1) {
          members.push({
            id: members.length + 1,
            node_i: nodeId(ordered[i].index, floor),
            node_j: nodeId(ordered[i + 1].index, floor),
            type: "beam",
            section: { b: 0.2, h: 0.4, E: concreteE, G: concreteG },
          });
        }
      }
    });
  };

  connectAlignedPillars("x");
  connectAlignedPillars("y");

  return {
    nodes,
    members,
    loads,
    supports,
    use_p_delta: true,
    nbr_stiffness_reduction: true,
    wind_v0: windParams.v0,
    wind_categoria: windParams.categoria,
    wind_cp: 0.8,
    wind_width_m: windParams.largura,
    n_floors_for_wind: nFloors,
    floor_height_m: floorHeight,
  };
}
