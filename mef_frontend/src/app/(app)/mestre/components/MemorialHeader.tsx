'use client';

import { Button } from '@/components/ui/button';
import { Download, FileText, Share2, Settings } from 'lucide-react';
import { useMestreStore } from '@/lib/store-mestre';
import { generateProfessionalMemorial, BASE_URL } from '@/lib/api-mestre';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
  DialogFooter,
} from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";

export function MemorialHeader() {
  const { selectedElementType, calculationTrace, fullResults, projectMeta, setProjectMeta } = useMestreStore();

  const handleExportPDF = async () => {
    if (!fullResults) return;
    try {
      const apiMeta = {
        obra: projectMeta.title,
        local: projectMeta.location,
        responsavel: projectMeta.engineer,
        registro: projectMeta.crea
      };
      const response = await generateProfessionalMemorial(fullResults, apiMeta);
      if (response.pdf_url) {
        window.open(`${BASE_URL}${response.pdf_url}`, '_blank');
      }
    } catch (error) {
      console.error("Erro ao gerar memorial executivo:", error);
      alert("Erro ao gerar PDF. Verifique o servidor.");
    }
  };

  const handleExportHTML = () => {
    const { pedagogicalSteps, selectedElementType } = useMestreStore.getState();
    if (pedagogicalSteps.length === 0) return;

    const stepsHtml = pedagogicalSteps.map((step, index) => `
      <div class="step-card">
        <div class="step-header">
          <span class="step-number">PASSO ${index + 1}</span>
          <h2 class="step-title">${step.title}</h2>
        </div>
        
        <div class="formula-box">
          <div class="latex-content">
            \\[ ${step.formula} \\]
          </div>
        </div>

        <div class="details-grid">
          <div class="detail-item">
            <span class="detail-label">Substituição</span>
            <div class="latex-inline">\\( ${step.substitution} \\)</div>
          </div>
          <div class="detail-item">
            <span class="detail-label">Resultado</span>
            <div class="latex-inline highlight">\\( ${step.result} \\)</div>
          </div>
        </div>

        ${step.diagramData ? `
          <div class="diagram-container">
            <div class="diagram-placeholder">
              <strong>${step.diagramData.title}</strong>
              <span>${step.diagramData.kind}</span>
            </div>
          </div>
        ` : ''}

        <div class="explanation">
          <p>${step.explanation}</p>
          ${step.norm ? `<span class="norm-tag">${step.norm}</span>` : ''}
        </div>
      </div>
    `).join('');

    const htmlContent = `
      <!DOCTYPE html>
      <html lang="pt-br">
      <head>
        <meta charset="UTF-8">
        <title>Memorial Atlas - ${selectedElementType.toUpperCase()}</title>
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css">
        <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.js"></script>
        <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/contrib/auto-render.min.js" onload="renderMathInElement(document.body);"></script>
        <style>
          :root { --primary: #007AFF; --text: #1d1d1f; --bg: #f5f5f7; --card: #ffffff; }
          body { font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", "Helvetica Neue", sans-serif; color: var(--text); background: var(--bg); line-height: 1.5; padding: 40px 20px; margin: 0; }
          .container { max-width: 850px; margin: 0 auto; }
          header { text-align: center; margin-bottom: 60px; border-bottom: 2px solid var(--primary); padding-bottom: 30px; }
          .brand { font-size: 24px; font-weight: 900; letter-spacing: -1px; color: var(--primary); margin: 0; }
          .report-title { font-size: 14px; font-weight: 700; text-transform: uppercase; letter-spacing: 2px; color: #86868b; margin-top: 10px; }
          
          .step-card { background: var(--card); border-radius: 20px; padding: 40px; margin-bottom: 30px; box-shadow: 0 4px 20px rgba(0,0,0,0.05); page-break-inside: avoid; }
          .step-header { margin-bottom: 25px; }
          .step-number { font-size: 10px; font-weight: 900; color: var(--primary); letter-spacing: 2px; display: block; margin-bottom: 5px; }
          .step-title { font-size: 22px; font-weight: 800; margin: 0; letter-spacing: -0.5px; }
          
          .formula-box { background: #f9f9fb; border: 1px solid #e5e5e7; border-radius: 12px; padding: 30px; margin: 25px 0; text-align: center; overflow-x: auto; }
          .details-grid { display: grid; grid-cols: 1fr 1fr; gap: 20px; margin-bottom: 25px; }
          .detail-item { background: #fdfdfd; border: 1px solid #f0f0f2; border-radius: 12px; padding: 20px; }
          .detail-label { font-size: 10px; font-weight: 800; text-transform: uppercase; color: #86868b; display: block; margin-bottom: 8px; }
          .latex-inline { font-size: 16px; }
          .highlight { color: var(--primary); font-weight: 700; }
          
          .diagram-container { margin: 30px 0; text-align: center; background: #fff; padding: 10px; border: 1px solid #eee; border-radius: 12px; }
          .diagram-placeholder { min-height: 160px; display: flex; flex-direction: column; align-items: center; justify-content: center; border: 2px solid #1d1d1f; color: #1d1d1f; text-transform: uppercase; letter-spacing: 1px; }
          .diagram-placeholder span { margin-top: 8px; color: #86868b; font-size: 10px; }
          
          .explanation { border-top: 1px solid #f0f0f2; pt-20; margin-top: 20px; padding-top: 20px; }
          .explanation p { font-size: 14px; color: #424245; font-style: italic; margin-bottom: 15px; }
          .norm-tag { font-size: 10px; font-weight: 700; background: rgba(0,122,255,0.08); color: var(--primary); padding: 4px 10px; rounded: 4px; border: 1px solid rgba(0,122,255,0.1); }
          
          footer { text-align: center; margin-top: 80px; color: #86868b; font-size: 12px; }
          @media print { body { background: white; padding: 0; } .step-card { box-shadow: none; border: 1px solid #eee; } }
        </style>
      </head>
      <body>
        <div class="container">
          <header>
            <h1 class="brand">ATLAS STRUCTURAL ENGINE</h1>
            <div class="report-title">Memorial Descritivo — ${selectedElementType.toUpperCase()}</div>
            <div style="font-size: 12px; color: #86868b; margin-top: 15px;">Data de Emissão: ${new Date().toLocaleDateString('pt-BR')}</div>
          </header>

          ${stepsHtml}

          <footer>
            <p>© ${new Date().getFullYear()} Atlas structural. Desenvolvido para Auditoria e Pedagogia Estrutural de Alta Fidelidade.</p>
          </footer>
        </div>
      </body>
      </html>
    `;

    const blob = new Blob([htmlContent], { type: 'text/html' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `Memorial_Atlas_${selectedElementType}_${new Date().getTime()}.html`;
    link.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="flex items-center justify-between mb-6 print:hidden">
      <div>
        <h2 className="text-2xl font-black tracking-tight text-foreground flex items-center gap-3">
          <FileText className="w-6 h-6 text-primary" />
          Memorial Descritivo
        </h2>
        <p className="text-xs text-muted-foreground font-medium uppercase tracking-widest mt-1">
          Elite Pedagogy — {selectedElementType}
        </p>
        {calculationTrace && (
          <div className="mt-2 flex flex-wrap items-center gap-2 text-[10px] font-bold uppercase tracking-wider">
            <span className="rounded-md border border-primary/20 bg-primary/10 px-2 py-1 text-primary">
              Solver: {calculationTrace.solver_module ?? 'não informado'}
            </span>
            <span className="rounded-md border border-border bg-muted/40 px-2 py-1 text-muted-foreground">
              Clássico: {calculationTrace.classical_check ? 'sim' : 'não'}
            </span>
            <span className="rounded-md border border-border bg-muted/40 px-2 py-1 text-muted-foreground">
              MEF: {calculationTrace.mef_check ? 'sim' : 'não'}
            </span>
          </div>
        )}
      </div>

      <div className="flex items-center gap-2">
        <Button 
          variant="outline" 
          size="sm" 
          className="h-9 gap-2 border-orange-500/20 hover:bg-orange-50 text-orange-600"
          onClick={handleExportPDF}
        >
          <FileText className="w-4 h-4" />
          <span className="hidden sm:inline">Memorial Executivo (PDF)</span>
        </Button>

        <Button 
          variant="default" 
          size="sm" 
          className="h-9 gap-2 bg-primary hover:bg-primary/90 text-primary-foreground shadow-lg shadow-primary/20"
          onClick={handleExportHTML}
        >
          <Download className="w-4 h-4" />
          <span className="hidden sm:inline">Memorial Completo</span>
        </Button>

        <Dialog>
          <DialogTrigger render={
            <Button variant="ghost" size="icon" className="h-9 w-9 rounded-full border border-border/50 hover:bg-muted" />
          }>
            <Settings className="w-4 h-4 text-primary" />
          </DialogTrigger>
          <DialogContent className="sm:max-w-[425px]">
            <DialogHeader>
              <DialogTitle>Configurações do Projeto</DialogTitle>
              <DialogDescription>
                Estes dados serão utilizados no cabeçalho dos Memoriais Executivos.
              </DialogDescription>
            </DialogHeader>
            <div className="grid gap-4 py-4">
              <div className="grid grid-cols-4 items-center gap-4">
                <Label htmlFor="title" className="text-right text-[10px] uppercase font-bold text-muted-foreground">Obra</Label>
                <Input id="title" value={projectMeta.title} onChange={(e) => setProjectMeta({ title: e.target.value })} className="col-span-3 h-9" />
              </div>
              <div className="grid grid-cols-4 items-center gap-4">
                <Label htmlFor="client" className="text-right text-[10px] uppercase font-bold text-muted-foreground">Cliente</Label>
                <Input id="client" value={projectMeta.client} onChange={(e) => setProjectMeta({ client: e.target.value })} className="col-span-3 h-9" />
              </div>
              <div className="grid grid-cols-4 items-center gap-4">
                <Label htmlFor="engineer" className="text-right text-[10px] uppercase font-bold text-muted-foreground">Engenheiro</Label>
                <Input id="engineer" value={projectMeta.engineer} onChange={(e) => setProjectMeta({ engineer: e.target.value })} className="col-span-3 h-9" />
              </div>
              <div className="grid grid-cols-4 items-center gap-4">
                <Label htmlFor="crea" className="text-right text-[10px] uppercase font-bold text-muted-foreground">CREA</Label>
                <Input id="crea" value={projectMeta.crea} onChange={(e) => setProjectMeta({ crea: e.target.value })} className="col-span-3 h-9 font-mono" />
              </div>
              <div className="grid grid-cols-4 items-center gap-4">
                <Label htmlFor="location" className="text-right text-[10px] uppercase font-bold text-muted-foreground">Cidade/UF</Label>
                <Input id="location" value={projectMeta.location} onChange={(e) => setProjectMeta({ location: e.target.value })} className="col-span-3 h-9" />
              </div>
            </div>
            <DialogFooter>
              <p className="text-[9px] text-muted-foreground uppercase tracking-widest font-black italic">
                Atlas Professional Grade
              </p>
            </DialogFooter>
          </DialogContent>
        </Dialog>

        <Button variant="ghost" size="icon" className="h-9 w-9 rounded-full">
          <Share2 className="w-4 h-4 text-muted-foreground" />
        </Button>
      </div>
    </div>
  );
}
