/**
 * MOTOR DE OTIMIZAÇÃO MULTI-OBJETIVO M5-PHD
 * Foco: Minimização de Peso Estrutural e Custo de Materiais.
 */

export interface SectionOptimizationParams {
  currentB: number;
  currentH: number;
  currentFck: number;
  utilization: number; // 0.0 a 1.0+
  type: 'beam' | 'pillar' | 'slab';
  constraints?: {
    minB?: number;
    maxB?: number;
    minH?: number;
    maxH?: number;
    fixedFck?: boolean;
  };
}

export interface OptimizationResult {
  suggestedB: number;
  suggestedH: number;
  suggestedFck: number;
  weightReduction: number; // Porcentagem
  explanation: string;
  isOptimized: boolean;
}

export class OptimizationEngine {
  /**
   * Sugere uma seção otimizada baseada na taxa de utilização atual.
   * Se utilization < 0.5, tenta reduzir a seção.
   * Se utilization > 0.95, tenta aumentar a seção para segurança.
   */
  static suggestSection(params: SectionOptimizationParams): OptimizationResult {
    const { currentB, currentH, currentFck, utilization, type, constraints } = params;
    
    let suggestedB = currentB;
    let suggestedH = currentH;
    let suggestedFck = currentFck;
    let isOptimized = false;
    let explanation = "";

    const minB = constraints?.minB || 12; // Mínimo normativo NBR 6118 para vigas é 12cm (com ressalvas)
    const minH = constraints?.minH || 20;

    // Caso 1: Sub-utilizado (Superdimensionado)
    if (utilization < 0.6) {
      isOptimized = true;
      // Tenta reduzir a altura primeiro (mais impacto no peso e arquitetura)
      if (currentH > minH + 5) {
        suggestedH = currentH - 5;
        explanation = `Seção superdimensionada (Utilização: ${(utilization * 100).toFixed(1)}%). Sugerimos reduzir a altura para ${suggestedH}cm para economia de material.`;
      } else if (currentB > minB + 3) {
        suggestedB = currentB - 2;
        explanation = `Seção superdimensionada. Sugerimos reduzir a largura para ${suggestedB}cm.`;
      } else if (!constraints?.fixedFck && currentFck > 25) {
        suggestedFck = currentFck - 5;
        explanation = `Utilização baixa. Considere reduzir o FCK para ${suggestedFck}MPa para reduzir custos.`;
      } else {
        isOptimized = false;
        explanation = "Seção já está no limite mínimo dimensional.";
      }
    } 
    // Caso 2: Crítico (Próximo ao limite ou falhando)
    else if (utilization > 0.98) {
      isOptimized = true;
      if (!constraints?.fixedFck && currentFck < 50) {
        suggestedFck = currentFck + 5;
        explanation = `Seção no limite crítico. Sugerimos aumentar o FCK para ${suggestedFck}MPa para evitar falhas por compressão.`;
      } else {
        suggestedH = currentH + 5;
        explanation = `Seção insuficiente. Sugerimos aumentar a altura para ${suggestedH}cm para garantir a segurança estrutural.`;
      }
    }
    else {
      explanation = "Seção atual está com aproveitamento ideal (60% - 95%).";
    }

    const currentArea = currentB * currentH;
    const suggestedArea = suggestedB * suggestedH;
    const weightReduction = ((currentArea - suggestedArea) / currentArea) * 100;

    return {
      suggestedB,
      suggestedH,
      suggestedFck,
      weightReduction: weightReduction,
      explanation,
      isOptimized
    };
  }

  /**
   * Simulação de Pareto: Retorna múltiplas opções para o usuário escolher.
   */
  static getTradeOffOptions(params: SectionOptimizationParams): OptimizationResult[] {
    const options: OptimizationResult[] = [];
    
    // Opção 1: Foco em Economia de Concreto
    options.push(this.suggestSection({
      ...params,
      constraints: { ...params.constraints, minH: 20 }
    }));

    // Opção 2: Foco em Segurança Máxima (Aumentar FCK)
    if (params.currentFck < 50) {
      options.push({
        suggestedB: params.currentB,
        suggestedH: params.currentH,
        suggestedFck: params.currentFck + 10,
        weightReduction: 0,
        explanation: "Aumentar apenas o FCK mantém a geometria e aumenta a reserva de segurança significativamente.",
        isOptimized: true
      });
    }

    return options.filter(opt => opt.isOptimized);
  }
}
