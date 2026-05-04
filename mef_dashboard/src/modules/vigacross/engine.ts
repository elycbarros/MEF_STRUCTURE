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
    const m = (load.value * L * L) / 12;
    return { left: -m, right: m };
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

function isReleased(support: SupportType): boolean {
  return support === 'pin' || support === 'free';
}

function nodeActive(support: SupportType): boolean {
  return support !== 'free';
}

function endMoment(bar: BarState, end: 'A' | 'B'): number {
  return end === 'A' ? bar.momentA : bar.momentB;
}

export function solveCross(input: BeamInput): CrossSolveResult {
  validateInput(input);
  const tolerance = input.tolerance ?? 0.001;
  const maxIterations = input.maxIterations ?? 50;
  const nodes = Array.from({ length: input.spans.length + 1 }, (_, i) => `N${i + 1}`);

  const bars: BarState[] = input.spans.map((span, i) => {
    const mep = fixedEndMoments(span);
    const aReleased = isReleased(input.supports[i]);
    const bReleased = isReleased(input.supports[i + 1]);
    return {
      barId: span.id || `B${i + 1}`,
      span,
      aNode: i,
      bNode: i + 1,
      kRel: (span.inertiaCm4 || input.defaultInertiaCm4) / span.length,
      mep,
      momentA: aReleased ? 0 : mep.left,
      momentB: bReleased ? 0 : mep.right,
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
      if (!nodeActive(input.supports[n])) continue;

      const connected = bars.flatMap((bar) => {
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
    const totalLoad = span.loads.reduce((s, l) => s + (l.type === 'udl' ? l.value * L : l.value), 0);
    const mLoadL = span.loads.reduce((s, l) => s + (l.type === 'udl' ? l.value * L * (L / 2) : l.value * l.position), 0);
    const RB = (mLoadL + bar.finalA - bar.finalB) / L;
    reactions[i + 1].verticalReaction += RB;
    reactions[i].verticalReaction += totalLoad - RB;
  });
  return reactions;
}

function buildDiagrams(spans: SpanInput[], bars: BarEndResult[], input: BeamInput): DiagramPoint[] {
  const points: DiagramPoint[] = [];
  let xOffset = 0;
  spans.forEach((span, i) => {
    const L = span.length;
    const leftM = bars[i].finalA;
    const rightM = bars[i].finalB;
    const totalLoad = span.loads.reduce((s, l) => s + (l.type === 'udl' ? l.value * L : l.value), 0);
    const mLoadL = span.loads.reduce((s, l) => s + (l.type === 'udl' ? l.value * L * (L / 2) : l.value * l.position), 0);
    const RB = (mLoadL + leftM - rightM) / L;
    const RA = totalLoad - RB;

    // EI (kN.m2)
    const E = input.eGPa || 210;
    const I = span.inertiaCm4 || input.defaultInertiaCm4 || 1000;
    const EI = E * I * 0.01;

    // C1 constant for y(0)=0 and y(L)=0
    let termLoadsL = 0;
    span.loads.forEach(load => {
      if (load.type === 'udl') {
        termLoadsL += (load.value * Math.pow(L, 4)) / 24;
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
          V -= load.value * x;
          M -= (load.value * x * x) / 2;
          defLoad += (load.value * Math.pow(x, 4)) / 24;
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
        deflection: -deflectionMm // Positive downwards
      });
    }
    xOffset += L;
  });
  return points;
}
