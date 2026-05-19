from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any
import re
import os
import matplotlib
matplotlib.use("Agg")
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
    text = str(value or "").strip().replace("\n", " ")
    if not text.startswith("$"):
        text = f"${text}$"
    return text


def _render_latex(latex_str: str, filename: str, fontsize: int = 16):
    # Configuração robusta para Mathtext
    plt.rcParams.update({
        "mathtext.fontset": "dejavusans",
        "text.usetex": False
    })
    
    # Criar figura com proporção melhor para fórmulas
    fig = plt.figure(figsize=(10, 1.2), dpi=300)
    plt.axis('off')
    
    try:
        fig.text(0.5, 0.5, latex_str, fontsize=fontsize, ha='center', va='center', color='#0f172a')
        plt.savefig(filename, transparent=True, bbox_inches='tight', pad_inches=0.1)
    except Exception as e:
        fig.clear()
        plt.axis('off')
        plain_text = latex_str.replace("$", "").replace("\\mathrm", "").replace("{", "").replace("}", "").replace("\\ ", " ").replace("\\", "")
        fig.text(0.5, 0.5, plain_text, fontsize=fontsize, ha='center', va='center', color='#0f172a')
        plt.savefig(filename, transparent=True, bbox_inches='tight', pad_inches=0.1)
    
    plt.close(fig)


class AcademicPDF(FPDF):
    def __init__(self, meta: dict[str, Any] | None = None):
        super().__init__()
        self.meta = meta or {}
        self.set_auto_page_break(auto=True, margin=16)

    def header(self):
        self.set_font("Helvetica", "B", 12)
        self.set_text_color(20, 24, 32)
        self.cell(0, 8, "Engine MESTRE - Memorial de Calculo Pedagogico", 0, new_x="LMARGIN", new_y="NEXT", align="L")
        self.set_font("Helvetica", "", 8)
        self.set_text_color(95, 105, 120)
        disciplina = _clean_text(self.meta.get("disciplina", "Engenharia Civil"))
        professor = _clean_text(self.meta.get("professor", "Professor"))
        self.cell(0, 5, f"{disciplina} | {professor}", 0, new_x="LMARGIN", new_y="NEXT", align="L")
        self.line(10, self.get_y() + 2, 200, self.get_y() + 2)
        self.ln(6)

    def footer(self):
        self.set_y(-14)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(120, 120, 120)
        self.cell(0, 8, f"Pagina {self.page_no()} | Memorial pedagogico gerado automaticamente", 0, new_x="RIGHT", new_y="TOP", align="C")

    def document_title(self, text: str):
        self.set_font("Helvetica", "B", 15)
        self.set_text_color(0, 0, 0)
        self.multi_cell(0, 8, _clean_text(text))
        self.ln(2)

    def section(self, text: str):
        self.set_font("Helvetica", "B", 10)
        self.set_fill_color(236, 240, 245)
        self.set_text_color(30, 35, 45)
        self.cell(0, 7, f"  {_clean_text(text)}", 0, new_x="LMARGIN", new_y="NEXT", align="L", fill=True)
        self.ln(2)

    def latex_callout(self, label: str, latex_text: str, step_idx: int, part_idx: int):
        if not latex_text: return
        
        self.set_font("Helvetica", "B", 7)
        self.set_text_color(100, 116, 139)
        self.cell(0, 4, _clean_text(label).upper(), 0, new_x="LMARGIN", new_y="NEXT")
        
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
        self.set_font("Helvetica", "B", 8)
        self.set_text_color(45, 55, 72)
        self.cell(0, 5, _clean_text(title), 1, new_x="LMARGIN", new_y="NEXT", align="L", fill=True)
        self.set_font("Helvetica", "", 9)
        self.set_text_color(20, 24, 32)
        self.multi_cell(0, 5, _clean_text(text), 1, "L")
        self.ln(1)

    def label_value(self, label: str, value: Any):
        self.set_font("Helvetica", "B", 8)
        self.set_text_color(70, 75, 85)
        self.cell(0, 5, _clean_text(label), 0, new_x="LMARGIN", new_y="NEXT")
        self.set_font("Helvetica", "", 8)
        self.set_text_color(20, 24, 32)
        self.multi_cell(0, 5, _clean_text(value) or "-")
        self.ln(1)

    def add_step(self, index: int, step: dict[str, Any]):
        status = _clean_text(step.get("status", "OK"))
        title = _clean_text(step.get("title", f"Passo {index}"))
        norm_ref = step.get("norm", step.get("norm_ref", ""))
        
        # Estilo do Título do Passo
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(15, 23, 42) # Slate 900
        self.multi_cell(0, 6, f"PASSO {index:02d}: {title}")
        self.ln(1)

        # Metadados e Norma
        if norm_ref:
            self.set_font("Helvetica", "I", 7)
            self.set_text_color(100, 116, 139) # Slate 500
            self.cell(0, 4, f"Ref: {norm_ref}", 0, new_x="LMARGIN", new_y="NEXT")
            
        # Busca flexível de campos (Novo vs Legado)
        f_latex = step.get("formula", step.get("formula_latex"))
        s_latex = step.get("substitution", step.get("substitution_latex"))
        r_latex = step.get("result", step.get("result_latex"))
            
        if f_latex:
            self.latex_callout("1. Expressao Literale", f_latex, index, 1)
        if s_latex:
            self.latex_callout("2. Substituicao de Valores", s_latex, index, 2)
        if r_latex:
            self.latex_callout("3. Conclusao Numerica", r_latex, index, 3)
            
        # Explicações e Pareceres
        explanation = step.get("explanation")
        opinion = step.get("opinion")
        
        if explanation:
            self.set_font("Helvetica", "", 8)
            self.set_text_color(51, 65, 85) # Slate 700
            self.multi_cell(0, 4, _clean_text(explanation))
            
        if opinion:
            self.set_font("Helvetica", "B", 8)
            self.set_text_color(15, 23, 42)
            self.multi_cell(0, 4, f"Parecer: {_clean_text(opinion)}")
            
        self.ln(4)

    def add_diagram_image(self, title: str, img_path: str):
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(0, 0, 0)
        self.cell(0, 7, f"  {_clean_text(title)}", 0, new_x="LMARGIN", new_y="NEXT", align="L")
        if os.path.exists(img_path):
            # Centered image
            self.image(img_path, x=25, w=160)
            self.ln(5)
        else:
            self.cell(0, 5, "[Erro ao carregar diagrama]", 0, 1)


def generate_academic_blackboard_pdf(
    output_path: str | Path,
    blackboard: dict[str, Any],
    project_meta: dict[str, Any] | None = None,
    diagrams: dict[str, Any] | None = None,
    classical_diagrams: dict[str, Any] | None = None,
) -> str:
    shear_path = moment_path = deflection_path = None
    try:
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
            pdf.section("Visualizacao de Esforços e Deformacoes")
            output_dir = os.path.dirname(output_path)
            shear_path, moment_path, deflection_path = _plot_structural_diagrams(classical_diagrams, diagrams, output_dir)
            pdf.add_diagram_image("Diagrama de Esforços Cortantes V(x) [kN]", shear_path)
            pdf.add_diagram_image("Diagrama de Momentos Fletores M(x) [kNm]", moment_path)
            if deflection_path:
                pdf.add_diagram_image("Diagrama de Deformacoes - Flecha y(x) [mm]", deflection_path)

        pdf.section("Resolucao passo a passo")
        for index, step in enumerate(blackboard.get("steps", []) or [], start=1):
            pdf.add_step(index, step)

        pdf.output(str(path))
        return str(path)
    except Exception as e:
        raise e
    finally:
        for f in [shear_path, moment_path, deflection_path]:
            if f and os.path.exists(f): os.remove(f)


def _plot_structural_diagrams(classical: dict | None, mef: dict | None, output_dir: str):
    # Extract classical data
    class_shear_x, class_shear_y = [], []
    class_moment_x, class_moment_y = [], []
    class_defl_x, class_defl_y = [], []

    if classical:
        if 'shear' in classical and isinstance(classical['shear'], list):
            class_shear_x = [pt['x'] for pt in classical['shear'] if isinstance(pt, dict) and 'x' in pt]
            class_shear_y = [pt['y'] for pt in classical['shear'] if isinstance(pt, dict) and 'y' in pt]
        elif 'V_kN' in classical:
            class_shear_x = classical.get('x_shear_m', classical.get('x_m', []))
            class_shear_y = classical['V_kN']

        if 'moment' in classical and isinstance(classical['moment'], list):
            class_moment_x = [pt['x'] for pt in classical['moment'] if isinstance(pt, dict) and 'x' in pt]
            class_moment_y = [pt['y'] for pt in classical['moment'] if isinstance(pt, dict) and 'y' in pt]
        elif 'M_kNm' in classical:
            class_moment_x = classical.get('x_moment_m', classical.get('x_m', []))
            class_moment_y = classical['M_kNm']

        if 'deflection' in classical and isinstance(classical['deflection'], list):
            class_defl_x = [pt['x'] for pt in classical['deflection'] if isinstance(pt, dict) and 'x' in pt]
            class_defl_y = [pt['y'] for pt in classical['deflection'] if isinstance(pt, dict) and 'y' in pt]
        elif 'delta_mm' in classical or 'w_mm' in classical:
            class_defl_x = classical.get('x_nodes_m', classical.get('x_m', []))
            class_defl_y = classical.get('delta_mm', classical.get('w_mm', []))

    # Extract MEF data
    mef_shear_x, mef_shear_y = [], []
    mef_moment_x, mef_moment_y = [], []
    mef_defl_x, mef_defl_y = [], []

    if mef:
        if 'shear' in mef and isinstance(mef['shear'], list):
            mef_shear_x = [pt['x'] for pt in mef['shear'] if isinstance(pt, dict) and 'x' in pt]
            mef_shear_y = [pt['y'] for pt in mef['shear'] if isinstance(pt, dict) and 'y' in pt]
        elif 'V_kN' in mef:
            mef_shear_x = mef.get('x_shear_m', mef.get('x_m', []))
            mef_shear_y = mef['V_kN']

        if 'moment' in mef and isinstance(mef['moment'], list):
            mef_moment_x = [pt['x'] for pt in mef['moment'] if isinstance(pt, dict) and 'x' in pt]
            mef_moment_y = [pt['y'] for pt in mef['moment'] if isinstance(pt, dict) and 'y' in pt]
        elif 'M_kNm' in mef:
            mef_moment_x = mef.get('x_moment_m', mef.get('x_m', []))
            mef_moment_y = mef['M_kNm']

        if 'deflection' in mef and isinstance(mef['deflection'], list):
            mef_defl_x = [pt['x'] for pt in mef['deflection'] if isinstance(pt, dict) and 'x' in pt]
            mef_defl_y = [pt['y'] for pt in mef['deflection'] if isinstance(pt, dict) and 'y' in pt]
        elif 'delta_mm' in mef or 'w_mm' in mef:
            mef_defl_x = mef.get('x_nodes_m', mef.get('x_m', []))
            mef_defl_y = mef.get('delta_mm', mef.get('w_mm', []))

    # 1. Shear Plot
    plt.figure(figsize=(10, 3))
    has_shear = False
    if len(class_shear_x) > 0 and len(class_shear_y) > 0:
        xc = np.array(class_shear_x)
        Vc = np.array(class_shear_y)
        min_len = min(len(xc), len(Vc))
        if min_len > 0:
            xc = xc[:min_len]
            Vc = Vc[:min_len]
            xc_p = np.concatenate([[xc[0]], xc, [xc[-1]]])
            Vc_p = np.concatenate([[0], Vc, [0]])
            plt.plot(xc_p, Vc_p, color='#059669', linewidth=2, label='Clássico (Analítico)', alpha=0.9)
            plt.fill_between(xc_p, Vc_p, color='#059669', alpha=0.1)
            has_shear = True

    if len(mef_shear_x) > 0 and len(mef_shear_y) > 0:
        xm = np.array(mef_shear_x)
        Vm = np.array(mef_shear_y)
        min_len = min(len(xm), len(Vm))
        if min_len > 0:
            plt.plot(xm[:min_len], Vm[:min_len], color='#64748b', linewidth=1, linestyle='--', label='Engine Premium', alpha=0.7)
            has_shear = True

    plt.axhline(0, color='black', linewidth=0.8)
    plt.title("Esforço Cortante V(x) [kN]", fontsize=10, fontweight='bold')
    plt.grid(True, linestyle='--', alpha=0.3)
    if has_shear:
        plt.legend(fontsize=8, loc='upper right')
    
    shear_img = os.path.join(output_dir, "pdf_diag_shear.png")
    plt.savefig(shear_img, dpi=150, bbox_inches='tight')
    plt.close()

    # 2. Moment Plot
    plt.figure(figsize=(10, 3))
    has_moment = False
    if len(class_moment_x) > 0 and len(class_moment_y) > 0:
        xc = np.array(class_moment_x)
        Mc = np.array(class_moment_y)
        min_len = min(len(xc), len(Mc))
        if min_len > 0:
            xc = xc[:min_len]
            Mc = Mc[:min_len]
            xc_p = np.concatenate([[xc[0]], xc, [xc[-1]]])
            Mc_p = np.concatenate([[0], Mc, [0]])
            plt.plot(xc_p, Mc_p, color='#c2410c', linewidth=2, label='Clássico (Analítico)', alpha=0.9)
            plt.fill_between(xc_p, Mc_p, color='#c2410c', alpha=0.1)
            has_moment = True

    if len(mef_moment_x) > 0 and len(mef_moment_y) > 0:
        xm = np.array(mef_moment_x)
        Mm = np.array(mef_moment_y)
        min_len = min(len(xm), len(Mm))
        if min_len > 0:
            plt.plot(xm[:min_len], Mm[:min_len], color='#64748b', linewidth=1, linestyle='--', label='Engine Premium', alpha=0.7)
            has_moment = True

    plt.axhline(0, color='black', linewidth=0.8)
    plt.gca().invert_yaxis()
    plt.title("Momento Fletor M(x) [kNm]", fontsize=10, fontweight='bold')
    plt.grid(True, linestyle='--', alpha=0.3)
    if has_moment:
        plt.legend(fontsize=8, loc='upper right')
    
    moment_img = os.path.join(output_dir, "pdf_diag_moment.png")
    plt.savefig(moment_img, dpi=150, bbox_inches='tight')
    plt.close()

    # 3. Deflection Plot
    deflection_img = None
    has_defl = False
    has_class_defl = len(class_defl_x) > 0 and len(class_defl_y) > 0
    has_mef_defl = len(mef_defl_x) > 0 and len(mef_defl_y) > 0

    if has_class_defl or has_mef_defl:
        plt.figure(figsize=(10, 3))
        if has_class_defl:
            xc = np.array(class_defl_x)
            Dc = np.array(class_defl_y)
            min_len = min(len(xc), len(Dc))
            if min_len > 0:
                plt.plot(xc[:min_len], Dc[:min_len], color='#059669', linewidth=2, label='Clássico (Analítico)', alpha=0.9)
                plt.fill_between(xc[:min_len], Dc[:min_len], color='#059669', alpha=0.1)
                has_defl = True
        
        if has_mef_defl:
            xm = np.array(mef_defl_x)
            Dm = np.array(mef_defl_y)
            min_len = min(len(xm), len(Dm))
            if min_len > 0:
                plt.plot(xm[:min_len], Dm[:min_len], color='#2563eb', linewidth=2, label='Flecha (mm)', alpha=0.9)
                plt.fill_between(xm[:min_len], Dm[:min_len], color='#2563eb', alpha=0.1)
                has_defl = True

        plt.axhline(0, color='black', linewidth=0.8)
        plt.gca().invert_yaxis() # Deformação para baixo positiva
        plt.title("Deformação - Flecha y(x) [mm]", fontsize=10, fontweight='bold')
        plt.grid(True, linestyle='--', alpha=0.3)
        if has_defl:
            plt.legend(fontsize=8, loc='upper right')
        
        deflection_img = os.path.join(output_dir, "pdf_diag_deflection.png")
        plt.savefig(deflection_img, dpi=150, bbox_inches='tight')
        plt.close()

    return shear_img, moment_img, deflection_img
