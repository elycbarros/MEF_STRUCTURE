'use client';

import { useCallback, useState } from 'react';
import { Award, ShieldAlert, FileText, CheckCircle, AlertTriangle, ArrowRight, Download, Activity, HelpCircle } from 'lucide-react';
import { BASE_URL, calculateSpecialElement, generateExamAuditorMemorial } from '@/lib/api-mestre';
import { useMestreStore } from '@/lib/store-mestre';
import { Button } from '@/components/ui/button';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui/card';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';

type QuestionId = 'q47_fcc_2018' | 'q31_vunesp_2021';

interface QuestionDetails {
  id: QuestionId;
  title: string;
  banca: string;
  ano: number;
  orgao: string;
  statement: string;
  official_key: string;
  real_solution: string;
  issue_description: string;
}

const QUESTIONS: QuestionDetails[] = [
  {
    id: 'q47_fcc_2018',
    title: 'Questão 47 - Engenheiro Civil',
    banca: 'FCC',
    ano: 2018,
    orgao: 'Metrô-SP',
    statement: 'Uma viga conjugada (com balanço) de 8,0 metros de comprimento total possui dois apoios: o apoio fixo A está localizado na extremidade esquerda (x = 0,0 m), e o apoio móvel B está a 6,0 metros de A (x = 6,0 m). A extremidade direita (a 2,0 metros de B) está livre (balanço) e submetida a uma carga concentrada de 30 kN dirigida verticalmente para baixo. Determine as reações verticais de apoio (Ra e Rb).',
    official_key: 'Ra = +10 kN (para cima) e Rb = +20 kN (para cima)',
    real_solution: 'Ra = -10 kN (para baixo, ancorando) e Rb = +40 kN (para cima)',
    issue_description: 'A banca violou grosseiramente a 1ª e a 2ª Lei do Equilíbrio Estático (Newton). Para anular o torque de tombamento de 60 kNm gerado pela carga de 30 kN no balanço, o apoio A DEVE tracionar a viga para baixo (-10 kN). Consequentemente, por equilíbrio de forças verticais, o apoio B deve resistir a 40 kN para cima.'
  },
  {
    id: 'q31_vunesp_2021',
    title: 'Questão 31 - Engenheiro Civil',
    banca: 'VUNESP',
    ano: 2021,
    orgao: 'AL-SP (Assembleia Legislativa)',
    statement: 'Considere uma treliça vertical em balanço (tipo cantilever) de 6,0 m de altura e 3,0 m de largura, dividida em dois painéis verticais de 3,0 m cada. O nó inferior esquerdo A (apoio fixo) e o nó inferior direito B (apoio móvel) sustentam a torre. Uma força horizontal Fx = 20 kN para a direita é aplicada no nó superior esquerdo E, e uma força vertical Fz = 20 kN para baixo é aplicada no nó superior direito F. Calcule os esforços axiais nos membros-chave.',
    official_key: 'Esforços axiais calculados com premissas ambíguas de sinais na reação horizontal.',
    real_solution: 'N_EF = -20 kN (compressão pura), reações de apoio exatas: Va = -40 kN, Vb = 60 kN, Ha = -20 kN.',
    issue_description: 'A formulação das alternativas da VUNESP apresentou contradições formais sobre os vetores de reação horizontal e convenções de esforços axiais, gerando ambiguidade intransponível para a resposta correta.'
  }
];

export function ExamAuditorPlayground() {
  const {
    updateParams,
    setIsLoading,
    setError,
    setCalculationTrace,
    setFullResults,
    applyMestreResponse,
    fullResults,
    isLoading,
    error
  } = useMestreStore();

  const [selectedQuestionId, setSelectedQuestionId] = useState<QuestionId>('q47_fcc_2018');
  const [isGeneratingPdf, setIsGeneratingPdf] = useState(false);
  const activeQuestion = QUESTIONS.find(q => q.id === selectedQuestionId) || QUESTIONS[0];

  const handleAudit = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      // 1. Configurar parâmetros no store para o HUD 2D/3D no frontend
      if (selectedQuestionId === 'q47_fcc_2018') {
        updateParams({
          L: 8.0,
          b: 0.20,
          h: 0.50,
          q: 0.0,
          fck: 30,
          supports: [
            { x: 0.0, type: 'pinned' },
            { x: 6.0, type: 'roller' }
          ],
          distributed_loads: [],
          point_loads: [
            { x: 8.0, P: 30.0 }
          ]
        });
      } else {
        // Questão 31 Vunesp
        updateParams({
          truss_type: 'q31',
          L: 3.0,
          h: 6.0,
          q: 20.0
        });
      }

      // 2. Chamar o solver de auditoria no backend
      const res = await calculateSpecialElement('exam_auditor', {
        question_id: selectedQuestionId
      });

      if (res.success) {
        applyMestreResponse(res);
      } else {
        setError('O motor estrutural falhou em auditar a questão.');
      }
    } catch (err: any) {
      setError(err.message || 'Falha de conexão com o servidor.');
    } finally {
      setIsLoading(false);
    }
  }, [selectedQuestionId, updateParams, setIsLoading, setError, applyMestreResponse]);

  const handleDownloadPDF = async () => {
    if (!fullResults || (fullResults as any).question_id !== selectedQuestionId) {
      setError('Por favor, execute a análise MEF primeiro para consolidar o Laudo.');
      return;
    }
    setIsGeneratingPdf(true);
    setError(null);
    try {
      const generated = await generateExamAuditorMemorial(selectedQuestionId);
      window.open(`${BASE_URL}${generated.pdf_url}`, '_blank');
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Erro ao gerar PDF da auditoria.');
    } finally {
      setIsGeneratingPdf(false);
    }
  };

  return (
    <div className="flex flex-col gap-6 p-4">
      {/* Cabeçalho macOS Premium */}
      <div className="flex flex-col gap-1 border-b border-white/5 pb-4">
        <div className="flex items-center gap-2">
          <Award className="h-6 w-6 text-sky-400" />
          <h2 className="text-xl font-bold tracking-tight text-white">Auditoria de Concursos</h2>
        </div>
        <p className="text-xs text-zinc-400">
          Laudos periciais e auditorias analíticas de questões de engenharia civil com erros estruturais ou físicos.
        </p>
      </div>

      {/* Seleção de Questões */}
      <div className="flex flex-col gap-2">
        <label className="text-xs font-semibold text-zinc-300">Selecione a Questão do Exame:</label>
        <Select
          value={selectedQuestionId}
          onValueChange={(val) => {
            setSelectedQuestionId(val as QuestionId);
            setFullResults(null);
            setCalculationTrace(null);
          }}
        >
          <SelectTrigger className="w-full border-white/10 bg-zinc-900/50 text-sm text-white">
            <SelectValue placeholder="Selecione..." />
          </SelectTrigger>
          <SelectContent className="border-white/10 bg-zinc-950 text-white">
            <SelectItem value="q47_fcc_2018">Questão 47 - FCC 2018 (Metrô-SP)</SelectItem>
            <SelectItem value="q31_vunesp_2021">Questão 31 - VUNESP 2021 (AL-SP)</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Card da Questão */}
      <Card className="border-white/5 bg-zinc-900/20 backdrop-blur-md">
        <CardHeader className="border-b border-white/5 pb-3">
          <div className="flex items-center justify-between">
            <span className="rounded-full bg-red-500/10 px-2 py-0.5 text-[10px] font-bold uppercase tracking-wider text-red-400">
              Inconsistência Detectada
            </span>
            <span className="text-[10px] text-zinc-500 font-mono">
              {activeQuestion.banca} / {activeQuestion.orgao} ({activeQuestion.ano})
            </span>
          </div>
          <CardTitle className="text-md font-bold text-white">{activeQuestion.title}</CardTitle>
          <CardDescription className="text-xs text-zinc-400 leading-relaxed">
            {activeQuestion.statement}
          </CardDescription>
        </CardHeader>
        <CardContent className="flex flex-col gap-4 pt-4">
          {/* Gabarito da Banca */}
          <div className="rounded-lg bg-amber-500/5 border border-amber-500/10 p-3 flex gap-3">
            <ShieldAlert className="h-5 w-5 text-amber-500 shrink-0 mt-0.5" />
            <div className="flex flex-col gap-1">
              <span className="text-xs font-bold text-amber-400">Gabarito Oficial Contestado:</span>
              <p className="text-xs text-zinc-300 font-mono leading-relaxed">{activeQuestion.official_key}</p>
            </div>
          </div>

          {/* Solução Física Real */}
          <div className="rounded-lg bg-emerald-500/5 border border-emerald-500/10 p-3 flex gap-3">
            <CheckCircle className="h-5 w-5 text-emerald-500 shrink-0 mt-0.5" />
            <div className="flex flex-col gap-1">
              <span className="text-xs font-bold text-emerald-400">Solução Física Real (MEF):</span>
              <p className="text-xs text-zinc-300 font-mono leading-relaxed">{activeQuestion.real_solution}</p>
            </div>
          </div>

          {/* Tese Técnico-Jurídica */}
          <div className="rounded-lg bg-zinc-950/60 p-3 border border-white/5">
            <div className="flex items-center gap-1.5 mb-1.5">
              <HelpCircle className="h-4 w-4 text-sky-400" />
              <span className="text-xs font-bold text-sky-400">Tese do Recurso:</span>
            </div>
            <p className="text-xs text-zinc-400 leading-relaxed">
              {activeQuestion.issue_description}
            </p>
          </div>
        </CardContent>

        <CardFooter className="flex gap-3 border-t border-white/5 pt-3">
          <Button
            className="flex-1 bg-sky-600 hover:bg-sky-500 text-xs font-semibold py-1.5 h-auto text-white flex items-center justify-center gap-2"
            onClick={handleAudit}
            disabled={isLoading}
          >
            <Activity className={`h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
            Auditar via MEF
          </Button>

          <Button
            variant="outline"
            className="flex-1 border-white/10 hover:bg-zinc-800 text-xs font-semibold py-1.5 h-auto text-zinc-300 flex items-center justify-center gap-2"
            onClick={handleDownloadPDF}
            disabled={isGeneratingPdf || !fullResults || (fullResults as any).question_id !== selectedQuestionId}
          >
            <Download className={`h-4 w-4 ${isGeneratingPdf ? 'animate-pulse' : ''}`} />
            {isGeneratingPdf ? 'Gerando PDF...' : 'Minuta de Recurso (PDF)'}
          </Button>
        </CardFooter>
      </Card>

      {error && (
        <div className="rounded-lg bg-red-500/10 border border-red-500/20 p-3 flex gap-2">
          <AlertTriangle className="h-4 w-4 text-red-500 shrink-0 mt-0.5" />
          <p className="text-xs text-red-400 font-medium">{error}</p>
        </div>
      )}
    </div>
  );
}
