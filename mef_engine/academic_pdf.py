from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any
import re
import os
import matplotlib.pyplot as plt
import numpy as np

from fpdf import FPDF
# Garantir que estamos usando fpdf2 (que expõe FPDF mas tem mais recursos)
try:
    import fpdf
    if not hasattr(fpdf, "__version__") or int(fpdf.__version__.split('.')[0]) < 2:
        print("WARNING: FPDF version is old. Unicode support may be limited.")
except ImportError:
    pass


def _clean_text(value: Any) -> str:
    """Limpa texto para compatibilidade com FPDF mantendo acentuação básica se possível."""
    text = "" if value is None else str(value)
    # Tentar manter acentuação básica para português
    # FPDF2 lida melhor com latin-1 por padrão
    replacements = {
        "λ": "lambda",
        "γ": "gamma",
        "φ": "phi",
        "²": "2",
        "³": "3",
        "≤": "<=",
        "≥": ">=",
        "≈": "~=",
        "→": "->",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    
    # Se não conseguirmos converter para latin-1, limpamos mais agressivamente
    try:
        text.encode('latin-1')
    except UnicodeEncodeError:
        text = re.sub(r"[^\x00-\xFF]+", "", text) # Remove apenas o que não é latin-1
    return text


def _formula_text(value: Any) -> str:
    """Prepara texto para renderização LaTeX via Matplotlib."""
    text = str(value or "")
    if not text.startswith("$"):
        text = f"${text}$"
    return text


def _render_latex(latex_str: str, filename: str, fontsize: int = 16):
    """Renderiza uma string LaTeX para um arquivo de imagem usando Matplotlib com alta qualidade."""
    plt.rc('text', usetex=False)
    plt.rc('font', family='serif', serif=['Computer Modern Roman', 'DejaVu Serif', 'serif'])
    
    # Criar figura com proporção melhor para fórmulas
    fig = plt.figure(figsize=(10, 1.2), dpi=300)
    plt.axis('off')
    
    try:
        # Centralizado
        print(f"DEBUG: Renderizando LaTeX: {latex_str}", flush=True)
        plt.text(0.5, 0.5, latex_str, fontsize=fontsize, ha='center', va='center', color='#0f172a')
        plt.savefig(filename, transparent=True, bbox_inches='tight', pad_inches=0.1)
    except Exception as e:
        print(f"ERROR: Falha ao renderizar LaTeX: {e}", flush=True)
        plt.text(0.5, 0.5, f"Formula Error", fontsize=10, color='red', ha='center', va='center')
        plt.savefig(filename, transparent=True, bbox_inches='tight', pad_inches=0.1)
    
    plt.close(fig)


class AcademicPDF(FPDF):
    def __init__(self, meta: dict[str, Any] | None = None):
        super().__init__()
        self.meta = meta or {}
        self.set_auto_page_break(auto=True, margin=16)

    def header(self):
        self.set_font("Arial", "B", 12)
        self.set_text_color(20, 24, 32)
        self.cell(0, 8, "Engine MESTRE - Memorial de Calculo Pedagogico", 0, 1, "L")
        self.set_font("Arial", "", 8)
        self.set_text_color(95, 105, 120)
        disciplina = _clean_text(self.meta.get("disciplina", "Engenharia Civil"))
        professor = _clean_text(self.meta.get("professor", "Professor"))
        self.cell(0, 5, f"{disciplina} | {professor}", 0, 1, "L")
        self.line(10, self.get_y() + 2, 200, self.get_y() + 2)
        self.ln(6)

    def footer(self):
        self.set_y(-14)
        self.set_font("Arial", "I", 8)
        self.set_text_color(120, 120, 120)
        self.cell(0, 8, f"Pagina {self.page_no()} | Memorial pedagogico gerado automaticamente", 0, 0, "C")

    def document_title(self, text: str):
        self.set_font("Arial", "B", 15)
        self.set_text_color(0, 0, 0)
        self.multi_cell(0, 8, _clean_text(text))
        self.ln(2)

    def section(self, text: str):
        self.set_font("Arial", "B", 10)
        self.set_fill_color(236, 240, 245)
        self.set_text_color(30, 35, 45)
        self.cell(0, 7, f"  {_clean_text(text)}", 0, 1, "L", fill=True)
        self.ln(2)

    def latex_callout(self, label: str, latex_text: str, step_idx: int, part_idx: int):
        if not latex_text: return
        
        self.set_font("Arial", "B", 7)
        self.set_text_color(100, 116, 139)
        self.cell(0, 4, _clean_text(label).upper(), 0, 1)
        
        # Gerar imagem temporária em local seguro relativo ao script
        temp_dir = Path(__file__).parent / "temp_latex"
        temp_dir.mkdir(parents=True, exist_ok=True)
        filename = temp_dir / f"step_{step_idx}_{part_idx}.png"
        
        if not latex_text.startswith("$"):
            latex_text = f"${latex_text}$"
            
        _render_latex(latex_text, str(filename))
        
        if filename.exists():
            curr_y = self.get_y()
            # Box de fundo estilizado
            self.set_fill_color(248, 250, 252) # Slate 50
            self.rect(10, curr_y, 190, 18, style='F')
            self.set_draw_color(226, 232, 240) # Slate 200
            self.line(10, curr_y, 10, curr_y + 18) # Borda esquerda de destaque
            
            # Centralizar imagem no box
            # fpdf image(x, y, w, h)
            self.image(str(filename), x=20, y=curr_y + 2, h=14)
            self.set_y(curr_y + 20)
        else:
            self.set_font("Courier", "", 8)
            self.multi_cell(0, 5, _clean_text(latex_text))
            self.ln(2)
    def callout(self, title: str, text: str):
        self.set_fill_color(248, 250, 252)
        self.set_draw_color(220, 226, 235)
        self.set_font("Arial", "B", 8)
        self.set_text_color(45, 55, 72)
        self.cell(0, 5, _clean_text(title), 1, 1, "L", fill=True)
        self.set_font("Arial", "", 9)
        self.set_text_color(20, 24, 32)
        self.multi_cell(0, 5, _clean_text(text), 1, "L")
        self.ln(1)

    def label_value(self, label: str, value: Any):
        self.set_font("Arial", "B", 8)
        self.set_text_color(70, 75, 85)
        self.cell(0, 5, _clean_text(label), 0, 1)
        self.set_font("Arial", "", 8)
        self.set_text_color(20, 24, 32)
        self.multi_cell(0, 5, _clean_text(value) or "-")
        self.ln(1)

    def add_step(self, index: int, step: dict[str, Any]):
        status = _clean_text(step.get("status", "INFO"))
        title = _clean_text(step.get("title", f"Passo {index}"))
        norm_ref = step.get("norm_ref", "")
        self.set_font("Arial", "B", 10)
        self.set_text_color(0, 0, 0)
        self.multi_cell(0, 6, f"Passo {index:02d} - {title}")
        self.ln(1)

        self.set_font("Arial", "B", 8)
        self.set_text_color(70, 75, 85)
        self.cell(0, 5, f"Status pedagogico: {status}", 0, 1)
        if norm_ref:
            self.label_value("Referencia normativa / criterio", norm_ref)
            
        if step.get("formula_latex"):
            self.latex_callout("1. Formula utilizada", step.get("formula_latex", ""), index, 1)
        if step.get("substitution_latex"):
            self.latex_callout("2. Substituicao dos valores", step.get("substitution_latex", ""), index, 2)
        if step.get("result_latex"):
            self.latex_callout("3. Conclusao numerica", step.get("result_latex", ""), index, 3)
            
        if step.get("opinion"):
            self.label_value("4. Parecer sobre o resultado final", step.get("opinion", ""))
        if step.get("explanation"):
            self.label_value("Interpretacao didatica", step.get("explanation", ""))
        self.ln(3)

    def add_diagram_image(self, title: str, img_path: str):
        self.set_font("Arial", "B", 10)
        self.set_text_color(30, 35, 45)
        self.cell(0, 7, f"  {_clean_text(title)}", 0, 1, "L")
        if os.path.exists(img_path):
            # Centered image
            self.image(img_path, x=25, w=160)
            self.ln(5)
        else:
            self.set_font("Arial", "I", 8)
            self.cell(0, 5, "[Erro ao carregar diagrama]", 0, 1)


def generate_academic_blackboard_pdf(
    output_path: str | Path,
    blackboard: dict[str, Any],
    project_meta: dict[str, Any] | None = None,
    diagrams: dict[str, Any] | None = None,
    classical_diagrams: dict[str, Any] | None = None,
) -> str:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    pdf = AcademicPDF(project_meta)
    pdf.add_page()

    pdf.document_title(f"Memorial de Calculo Pedagogico - {blackboard.get('title', 'Roteiro didatico')}")
    pdf.section("Objetivo do documento")
    pdf.label_value(
        "Finalidade",
        "Apresentar o passo-a-passo analitico do dimensionamento, com formula, valores substituidos e conclusao de cada verificacao.",
    )
    pdf.label_value("Base", "NBR 6118 e criterios auxiliares indicados em cada passo.")

    pdf.section("Dados do exercicio")
    summary = blackboard.get("summary", {}) or {}
    for key, value in summary.items():
        pdf.label_value(str(key), value)
    pdf.label_value("Data de emissao", datetime.now().strftime("%d/%m/%Y %H:%M"))
    pdf.ln(4)

    # Adicionar Diagramas se existirem
    if classical_diagrams or diagrams:
        pdf.section("Visualizacao de Esforços (Mestre vs MEF)")
        output_dir = os.path.dirname(output_path)
        shear_path, moment_path = _plot_structural_diagrams(classical_diagrams, diagrams, output_dir)
        pdf.add_diagram_image("Diagrama de Esforços Cortantes V(x) [kN]", shear_path)
        pdf.add_diagram_image("Diagrama de Momentos Fletores M(x) [kNm]", moment_path)

    pdf.section("Resolucao passo a passo")
    for index, step in enumerate(blackboard.get("steps", []) or [], start=1):
        pdf.add_step(index, step)

    pdf.output(str(path))
    return str(path)


def _plot_structural_diagrams(classical: dict | None, mef: dict | None, output_dir: str):
    # Shear Plot
    plt.figure(figsize=(10, 4))
    
    if classical:
        xc, Vc = np.array(classical['x_m']), np.array(classical['V_kN'])
        # 90 graus para clássico
        xc_p = np.concatenate([[xc[0]], xc, [xc[-1]]])
        Vc_p = np.concatenate([[0], Vc, [0]])
        plt.plot(xc_p, Vc_p, color='#059669', linewidth=2.5, label='Clássico (Analítico)', alpha=0.9)
        plt.fill_between(xc_p, Vc_p, color='#059669', alpha=0.1)
        
    if mef:
        xm, Vm = np.array(mef['x_m']), np.array(mef['V_kN'])
        plt.plot(xm, Vm, color='#64748b', linewidth=1.5, linestyle='--', label='MEF Premium', alpha=0.7)

    plt.axhline(0, color='black', linewidth=0.8)
    plt.title("Esforço Cortante V(x) [kN]", fontsize=12, fontweight='bold', pad=15)
    plt.grid(True, linestyle='--', alpha=0.4)
    plt.legend(fontsize=9, loc='upper right')
    plt.xlabel("Posição (m)", fontsize=10)
    plt.ylabel("V (kN)", fontsize=10)
    
    shear_img = os.path.join(output_dir, "pdf_diag_shear.png")
    plt.savefig(shear_img, dpi=120, bbox_inches='tight')
    plt.close()

    # Moment Plot
    plt.figure(figsize=(10, 4))
    
    if classical:
        xc, Mc = np.array(classical['x_m']), np.array(classical['M_kNm'])
        xc_p = np.concatenate([[xc[0]], xc, [xc[-1]]])
        Mc_p = np.concatenate([[0], Mc, [0]])
        plt.plot(xc_p, Mc_p, color='#2563eb', linewidth=2.5, label='Clássico (Analítico)', alpha=0.9)
        plt.fill_between(xc_p, Mc_p, color='#2563eb', alpha=0.1)

    if mef:
        xm, Mm = np.array(mef['x_m']), np.array(mef['M_kNm'])
        plt.plot(xm, Mm, color='#64748b', linewidth=1.5, linestyle='--', label='MEF Premium', alpha=0.7)

    plt.axhline(0, color='black', linewidth=0.8)
    plt.gca().invert_yaxis()
    plt.title("Momento Fletor M(x) [kNm]", fontsize=12, fontweight='bold', pad=15)
    plt.grid(True, linestyle='--', alpha=0.4)
    plt.legend(fontsize=9, loc='upper right')
    plt.xlabel("Posição (m)", fontsize=10)
    plt.ylabel("M (kNm)", fontsize=10)
    
    moment_img = os.path.join(output_dir, "pdf_diag_moment.png")
    plt.savefig(moment_img, dpi=120, bbox_inches='tight')
    plt.close()

    return shear_img, moment_img
