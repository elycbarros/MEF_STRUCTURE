import {
  BeamInput,
  BarEndResult,
  CrossIteration,
  CrossSolveResult,
  DiagramPoint,
  EndMoments,
  SpanInput,
  SpanLoad,
  SupportType,
} from './types';

interface BarState {
  barId: string;
  span: SpanInput;
  aNode: number;
  bNode: number;
  kRel: number;
  mep: EndMoments;
  momentA: number;
  momentB: number;
  aReleased: boolean;
  bReleased: boolean;
}

type ConnectedEnd = { bar: BarState; atEnd: 'A' | 'B' };

function validateInput(input: BeamInput): void {
  if (input.spans.length < 1 || input.spans.length > 5) throw new Error('Número de vãos inválido (MESTRE: 1 a 5).');
  if (input.supports.length !== input.spans.length + 1) throw new Error('Quantidade de apoios deve ser número de vãos + 1.');
  input.spans.forEach((s) => {
    if (s.length <= 0) throw new Error(`Vão ${s.id} com comprimento inválido.`);
    s.loads.forEach((l) => {
      if (l.type === 'point' && (l.position < 0 || l.position > s.length)) {
        throw new Error(`Carga pontual fora do vão ${s.id}.`);
      }
    });
  });
}

function mepForLoad(span: SpanInput, load: SpanLoad): EndMoments {
  const L = span.length;

  if (load.type === 'udl') {
    const q1 = load.value;          // intensity at A
    const q2 = load.q_end ?? q1;   // intensity at B (defaults to uniform)

    if (Math.abs(q1 - q2) < 1e-9) {
      // Uniform: M = ±qL²/12
      const m = (q1 * L * L) / 12;
      return { left: -m, right: m };
    }

    // Trapezoidal: decompose into uniform (q1) + triangular (q2-q1)
    // For triangular load increasing A→B with intensity Δq = q2-q1:
    //   MEP_A = -L²(7q1 + 3q2) / 60    (using standard formula)
    //   MEP_B = +L²(3q1 + 7q2) / 60   (but we use uniform + triangle superposition)
    // Uniform part (q1):
    const mUnif = (q1 * L * L) / 12;
    // Triangular part (Δq = q2-q1, increasing 0 at A to Δq at B):
    const dq = q2 - q1;
    const mTriA = -(dq * L * L) / 20;  // MEP_A for rising triangle
    const mTriB =  (dq * L * L) / 30;  // MEP_B for rising triangle
    return { left: -mUnif + mTriA, right: mUnif + mTriB };
  }

  const P = load.value;
  const a = load.position;
  const b = L - a;
  return { left: -((P * a * b * b) / (L * L)), right: (P * a * a * b) / (L * L) };
}

function fixedEndMoments(span: SpanInput): EndMoments {
  return span.loads.reduce(
    (acc, load) => {
      const m = mepForLoad(span, load);
      return { left: acc.left + m.left, right: acc.right + m.right };
    },
    { left: 0, right: 0 },
  );
}

function endIsReleased(support: SupportType, nodeIndex: number, lastNodeIndex: number): boolean {
  if (support === 'free') return true;
  if (support === 'pin' || support === 'roller') return nodeIndex === 0 || nodeIndex === lastNodeIndex;
  return false;
}

function nodeCanRotate(support: SupportType, nodeIndex: number, lastNodeIndex: number): boolean {
  if (nodeIndex === 0 || nodeIndex === lastNodeIndex) return false;
  return support === 'pin' || support === 'roller';
}

function endMoment(bar: BarState, end: 'A' | 'B'): number {
  return end === 'A' ? bar.momentA : bar.momentB;
}

export function solveCross(input: BeamInput): CrossSolveResult {
  validateInput(input);
  const tolerance = input.tolerance ?? 0.001;
  const maxIterations = input.maxIterations ?? 50;
  const nodes = Array.from({ length: input.spans.length + 1 }, (_, i) => `N${i + 1}`);
  const lastNodeIndex = nodes.length - 1;

  const bars: BarState[] = input.spans.map((span, i) => {
    const mep = fixedEndMoments(span);
    const aReleased = endIsReleased(input.supports[i], i, lastNodeIndex);
    const bReleased = endIsReleased(input.supports[i + 1], i + 1, lastNodeIndex);
    let momentA = mep.left;
    let momentB = mep.right;

    if (aReleased) {
      const releaseCorrection = -momentA;
      momentA = 0;
      if (!bReleased) momentB += 0.5 * releaseCorrection;
    }
    if (bReleased) {
      const releaseCorrection = -momentB;
      momentB = 0;
      if (!aReleased) momentA += 0.5 * releaseCorrection;
    }

    return {
      barId: span.id || `B${i + 1}`,
      span,
      aNode: i,
      bNode: i + 1,
      kRel: (span.inertiaCm4 || input.defaultInertiaCm4) / span.length,
      mep,
      momentA,
      momentB,
      aReleased,
      bReleased,
    };
  });

  const iterations: CrossIteration[] = [];
  let converged = false;
  let finalMaxUnbalanced = Number.POSITIVE_INFINITY;

  for (let iteration = 1; iteration <= maxIterations; iteration += 1) {
    let maxUnbalanced = 0;
    const nodeResults: CrossIteration['nodeResults'] = [];

    for (let n = 0; n < nodes.length; n += 1) {
      if (!nodeCanRotate(input.supports[n], n, lastNodeIndex)) continue;

      const connected: ConnectedEnd[] = bars.flatMap((bar): ConnectedEnd[] => {
        if (bar.aNode === n && !bar.aReleased) return [{ bar, atEnd: 'A' as const }];
        if (bar.bNode === n && !bar.bReleased) return [{ bar, atEnd: 'B' as const }];
        return [];
      });
      if (!connected.length) continue;

      const sumMoment = connected.reduce((sum, c) => sum + endMoment(c.bar, c.atEnd), 0);
      const sumK = connected.reduce((sum, c) => sum + c.bar.kRel, 0);
      if (sumK === 0) continue;

      const distributedMoments: { barId: string; value: number }[] = [];
      const transmittedMoments: { barId: string; value: number }[] = [];

      connected.forEach((c) => {
        const di = c.bar.kRel / sumK;
        const mDist = -sumMoment * di;
        const mCarry = 0.5 * mDist;

        if (c.atEnd === 'A') {
          c.bar.momentA += mDist;
          if (!c.bar.bReleased) c.bar.momentB += mCarry;
        } else {
          c.bar.momentB += mDist;
          if (!c.bar.aReleased) c.bar.momentA += mCarry;
        }

        distributedMoments.push({ barId: c.bar.barId, value: mDist });
        transmittedMoments.push({ barId: c.bar.barId, value: mCarry });
      });

      maxUnbalanced = Math.max(maxUnbalanced, Math.abs(sumMoment));
      nodeResults.push({ nodeId: nodes[n], unbalancedMoment: sumMoment, distributedMoments, transmittedMoments });
    }

    iterations.push({ iteration, nodeResults, maxUnbalanced });
    finalMaxUnbalanced = maxUnbalanced;
    if (maxUnbalanced < tolerance) {
      converged = true;
      break;
    }
  }

  const barResults: BarEndResult[] = bars.map((b) => ({
    barId: b.barId,
    nodeA: nodes[b.aNode],
    nodeB: nodes[b.bNode],
    mepA: b.mep.left,
    mepB: b.mep.right,
    finalA: b.aReleased ? 0 : b.momentA,
    finalB: b.bReleased ? 0 : b.momentB,
  }));

  return {
    input,
    nodes,
    barResults,
    iterations,
    converged,
    finalMaxUnbalanced,
    nodeReactions: solveReactions(input.spans, barResults, nodes),
    diagrams: buildDiagrams(input.spans, barResults, input),
  };
}

function solveReactions(spans: SpanInput[], bars: BarEndResult[], nodes: string[]) {
  const reactions = Array.from({ length: nodes.length }, (_, i) => ({ nodeId: nodes[i], verticalReaction: 0 }));
  bars.forEach((bar, i) => {
    const span = spans[i];
    const L = span.length;

    // Total load and moment of loads about A (for each load)
    let totalLoad = 0;
    let momentAboutA = 0;

    span.loads.forEach(l => {
      if (l.type === 'udl') {
        const q1 = l.value;
        const q2 = l.q_end ?? q1;
        // Resultant = (q1+q2)/2 * L
        totalLoad += ((q1 + q2) / 2) * L;
        // Centroid of trapezoidal load from A:
        // x_c = L * (q1 + 2*q2) / (3*(q1+q2))  when q1+q2 > 0
        const xCentroid = (q1 + q2) > 1e-12
          ? L * (q1 + 2 * q2) / (3 * (q1 + q2))
          : L / 2;
        momentAboutA += ((q1 + q2) / 2) * L * xCentroid;
      } else {
        totalLoad += l.value;
        momentAboutA += l.value * l.position;
      }
    });

    const leftMoment = bar.finalA;
    const rightMoment = -bar.finalB;
    const RA = (rightMoment - leftMoment + momentAboutA) / L;
    const RB = totalLoad - RA;
    reactions[i].verticalReaction += RA;
    reactions[i + 1].verticalReaction += RB;
  });
  return reactions;
}

function buildDiagrams(spans: SpanInput[], bars: BarEndResult[], input: BeamInput): DiagramPoint[] {
  const points: DiagramPoint[] = [];
  let xOffset = 0;
  spans.forEach((span, i) => {
    const L = span.length;
    const leftM = bars[i].finalA;
    const rightM = -bars[i].finalB;

    // Reaction at A for this span (using corrected trapezoidal centroid)
    let totalLoad = 0;
    let momentAboutA = 0;
    span.loads.forEach(l => {
      if (l.type === 'udl') {
        const q1 = l.value;
        const q2 = l.q_end ?? q1;
        totalLoad += ((q1 + q2) / 2) * L;
        const xCentroid = (q1 + q2) > 1e-12 ? L * (q1 + 2 * q2) / (3 * (q1 + q2)) : L / 2;
        momentAboutA += ((q1 + q2) / 2) * L * xCentroid;
      } else {
        totalLoad += l.value;
        momentAboutA += l.value * l.position;
      }
    });
    const RA = (rightM - leftM + momentAboutA) / L;

    // EI (kN.m²)
    const E = input.eGPa || 210;
    const I = span.inertiaCm4 || input.defaultInertiaCm4 || 1000;
    const EI = E * I * 0.01;

    // Integration constant C1 (for zero deflection at both ends)
    let termLoadsL = 0;
    span.loads.forEach(load => {
      if (load.type === 'udl') {
        const q1 = load.value;
        const q2 = load.q_end ?? q1;
        // Uniform part
        termLoadsL += (q1 * Math.pow(L, 4)) / 24;
        // Triangular correction
        const dq = q2 - q1;
        termLoadsL += (dq * Math.pow(L, 5)) / 120;
      } else {
        termLoadsL += (load.value * Math.pow(L - load.position, 3)) / 6;
      }
    });
    const C1 = -((leftM * L * L) / 2 + (RA * L * L * L) / 6 - termLoadsL) / L;

    for (let j = 0; j <= 20; j += 1) {
      const x = (L * j) / 20;
      let V = RA;
      let M = leftM + RA * x;
      let defLoad = 0;

      span.loads.forEach((load) => {
        if (load.type === 'udl') {
          const q1 = load.value;
          const q2 = load.q_end ?? q1;
          const dq = q2 - q1;
          // Intensity at position x: q(x) = q1 + dq*(x/L)
          // Shear contribution: integral of q(x) from 0 to x
          V -= q1 * x + (dq / (2 * L)) * x * x;
          // Moment contribution: integral of q(x)*(x-t) dt from 0 to x
          M -= (q1 * x * x) / 2 + (dq * x * x * x) / (6 * L);
          // Deflection integral (4th order): uniform + triangle
          defLoad += (q1 * Math.pow(x, 4)) / 24 + (dq * Math.pow(x, 5)) / (120 * L);
        } else if (x >= load.position) {
          V -= load.value;
          M -= load.value * (x - load.position);
          defLoad += (load.value * Math.pow(x - load.position, 3)) / 6;
        }
      });

      const yEI = (leftM * x * x) / 2 + (RA * x * x * x) / 6 - defLoad + C1 * x;
      const deflectionMm = (yEI / EI) * 1000;

      points.push({
        xGlobal: xOffset + x,
        spanId: span.id,
        xLocal: x,
        shear: V,
        moment: M,
        deflection: -deflectionMm
      });
    }
    xOffset += L;
  });
  return points;
}
