from __future__ import annotations
from fpdf import FPDF
from pathlib import Path
from datetime import datetime
import json

class ProfessionalMemorialPDF(FPDF):
    """
    Motor de Memorial Descritivo Profissional (Executive Grade).
    Layout otimizado para entrega formal de projetos estruturais.
    """
    def __init__(self, project_meta: dict):
        super().__init__()
        self.project_meta = project_meta
        self.set_auto_page_break(auto=True, margin=20)
        
    def header(self):
        if self.page_no() > 1:
            self.set_font('Helvetica', 'B', 10)
            self.set_text_color(50, 50, 50)
            obra = self.project_meta.get('obra', 'PROJETO ESTRUTURAL')
            self.cell(0, 10, f'MEMORIAL DE CÁLCULO - {obra.upper()}', 0, 0, 'L')
            self.set_font('Helvetica', '', 9)
            self.cell(0, 10, f'Emissão: {datetime.now().strftime("%d/%m/%Y")}', 0, 1, 'R')
            self.line(10, 20, 200, 20)
            self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f'ATLAS Structural Engine | v4.0 | Página {self.page_no()}', 0, 0, 'C')

    def add_cover(self):
        self.add_page()
        self.set_fill_color(33, 37, 41) # Dark Slate
        self.rect(0, 0, 210, 297, 'F')
        
        self.set_y(60)
        self.set_font('Helvetica', 'B', 32)
        self.set_text_color(255, 255, 255)
        self.multi_cell(0, 15, "MEMORIAL DE\nCÁLCULO ESTRUTURAL", 0, 'C')
        
        self.set_y(120)
        self.set_font('Helvetica', '', 14)
        self.set_text_color(200, 200, 200)
        obra = self.project_meta.get('obra', 'N/D')
        local = self.project_meta.get('local', 'N/D')
        self.multi_cell(0, 10, f"OBRA: {obra.upper()}\nLOCAL: {local.upper()}", 0, 'C')
        
        self.set_y(220)
        self.set_font('Helvetica', 'B', 12)
        self.set_text_color(255, 255, 255)
        responsavel = self.project_meta.get('responsavel', 'Eng. Civil')
        registro = self.project_meta.get('registro', 'CREA-XX')
        self.multi_cell(0, 8, f"{responsavel.upper()}\n{registro}", 0, 'C')
        
        self.add_page()

    def chapter_title(self, num, title):
        self.set_font('Helvetica', 'B', 14)
        self.set_text_color(0, 51, 102) # Navy Blue
        self.cell(0, 10, f"{num}. {title.upper()}", 0, 1, 'L')
        self.line(10, self.get_y(), 100, self.get_y())
        self.ln(5)

    def section_title(self, title):
        self.set_font('Helvetica', 'B', 11)
        self.set_text_color(40, 40, 40)
        self.cell(0, 8, title, 0, 1, 'L')
        self.ln(2)

    def add_kpi_grid(self, kpis: list[tuple]):
        self.set_font('Helvetica', '', 10)
        for label, value in kpis:
            self.set_text_color(100, 100, 100)
            self.cell(60, 7, f" {label}:", 1, 0, 'L')
            self.set_text_color(0, 0, 0)
            self.set_font('Helvetica', 'B', 10)
            self.cell(130, 7, f" {value}", 1, 1, 'L')
            self.set_font('Helvetica', '', 10)
        self.ln(5)

    def add_executive_table(self, header: list[str], data: list[list], widths: list[float]):
        self.set_font('Helvetica', 'B', 9)
        self.set_fill_color(240, 240, 240)
        for i, h in enumerate(header):
            self.cell(widths[i], 8, h, 1, 0, 'C', fill=True)
        self.ln()
        
        self.set_font('Helvetica', '', 9)
        for row in data:
            for i, item in enumerate(row):
                self.cell(widths[i], 7, str(item), 1, 0, 'C')
            self.ln()
        self.ln(5)

    def add_steel_table(self, table_data: list[dict]):
        self.chapter_title('X', 'Tabela de Ferro (Resumo de Aço)')
        header = ['Pos', 'phi (mm)', 'Qtd', 'Comp (cm)', 'Total (m)', 'Peso (kg)']
        widths = [20, 30, 20, 40, 40, 40]
        
        formatted_data = []
        for row in table_data:
            formatted_data.append([
                row['pos'],
                f"{row['phi_mm']:.1f}",
                row['count'],
                f"{row['length_m']*100:.0f}",
                f"{row['total_length_m']:.2f}",
                f"{row['weight_kg']:.2f}"
            ])
        self.add_executive_table(header, formatted_data, widths)

def generate_professional_memorial(output_path: str, results: dict, project_meta: dict):
    pdf = ProfessionalMemorialPDF(project_meta)
    pdf.add_cover()
    
    # 1. Parâmetros de Projeto
    pdf.chapter_title('1', 'Parâmetros de Projeto')
    kpis = [
        ('Normas Aplicadas', 'NBR 6118, NBR 6123, NBR 6120'),
        ('Concreto (fck)', f"{results.get('fck', 30)} MPa"),
        ('Aço Principal', 'CA-50'),
        ('Aço Estribos', 'CA-60 / CA-50'),
        ('Cobrimento Nominal', '3.0 cm (Classe II)'),
    ]
    pdf.add_kpi_grid(kpis)

    # 2. Análise Solo-Estrutura (Winkler Não-Linear)
    if 'ssi' in results:
        pdf.chapter_title('2', 'Interação Solo-Estrutura (SSI)')
        ssi = results['ssi']
        kpis_ssi = [
            ('Modelo Geotécnico', 'Winkler Não-Linear (Plastificação)'),
            ('Tensão Admissível', f"{ssi.get('q_adm', 0)} kPa"),
            ('Recalque Máximo', f"{ssi.get('w_max', 0):.2f} mm"),
            ('Ratio de Plastificação', f"{ssi.get('plastification_ratio', 0)*100:.1f}%"),
        ]
        pdf.add_kpi_grid(kpis_ssi)

    # 3. Detalhamento e Quantitativos
    if 'steel_table' in results:
        pdf.add_steel_table(results['steel_table'])

    pdf.output(output_path)
    return output_path
