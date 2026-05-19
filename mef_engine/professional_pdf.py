from __future__ import annotations
from fpdf import FPDF
from fpdf.enums import XPos, YPos
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
            self.cell(0, 10, f'MEMORIAL DE CÁLCULO - {obra.upper()}', 0, align='L', new_x=XPos.RIGHT, new_y=YPos.TOP)
            self.set_font('Helvetica', '', 9)
            self.cell(0, 10, f'Emissão: {datetime.now().strftime("%d/%m/%Y")}', 0, align='R', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            self.line(10, 20, 200, 20)
            self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f'ATLAS Structural Engine | v4.0 | Página {self.page_no()}', 0, align='C', new_x=XPos.RIGHT, new_y=YPos.TOP)

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
        self.cell(0, 10, f"{num}. {title.upper()}", 0, align='L', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.line(10, self.get_y(), 100, self.get_y())
        self.ln(5)

    def section_title(self, title):
        self.set_font('Helvetica', 'B', 11)
        self.set_text_color(40, 40, 40)
        self.cell(0, 8, title, 0, align='L', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(2)

    def add_kpi_grid(self, kpis: list[tuple]):
        self.set_font('Helvetica', '', 10)
        for label, value in kpis:
            self.set_text_color(100, 100, 100)
            self.cell(90, 9, f" {self.ascii_safe(label)}:", 1, align='L', new_x=XPos.RIGHT, new_y=YPos.TOP)
            self.set_text_color(0, 0, 0)
            self.set_font('Helvetica', 'B', 10)
            self.cell(100, 9, f" {self.ascii_safe(str(value))}", 1, align='L', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            self.set_font('Helvetica', '', 10)
        self.ln(6)

    @staticmethod
    def ascii_safe(text: str) -> str:
        """Sanitize text to Latin-1 compatible for Helvetica built-in font."""
        replacements = {
            '\u03a6': 'phi',  # Φ (phi majusculo de diametro)
            '\u03c6': 'phi',  # φ
            '\u00b2': '2',    # ² superscript
            '\u00b3': '3',    # ³ superscript
            '\u2014': '-',    # — em dash
            '\u2013': '-',    # – en dash
            '\u2264': '<=',   # ≤
            '\u2265': '>=',   # ≥
            '\u03b4': 'd',    # δ
            '\u03b3': 'g',    # γ
            '\u2610': '[ ]',  # ☐
            '\u2611': '[x]',  # ☑
        }
        for char, repl in replacements.items():
            text = text.replace(char, repl)
        # Encode to latin-1, replacing any remaining unknowns
        return text.encode('latin-1', errors='replace').decode('latin-1')

    def add_compliance_alert(self, check_name: str, status: str, value_str: str, limit_str: str):
        """Renderiza linha de verificacao normativa com cor de status."""
        is_ok = status.upper() in ('ATENDE', 'OK', 'SATISFAZ', 'PASS')
        self.set_font('Helvetica', 'B', 10)
        if is_ok:
            self.set_fill_color(0, 140, 60)
        else:
            self.set_fill_color(200, 0, 30)
        self.set_text_color(255, 255, 255)
        status_label = 'ATENDE' if is_ok else 'NAO ATENDE'
        self.cell(35, 8, ' ' + status_label, 0, align='L', fill=True,
                  new_x=XPos.RIGHT, new_y=YPos.TOP)
        self.set_fill_color(245, 245, 245)
        self.set_text_color(30, 30, 30)
        self.set_font('Helvetica', '', 9)
        self.cell(75, 9, f" {self.ascii_safe(check_name)}", 1, align='L', fill=True, new_x=XPos.RIGHT, new_y=YPos.TOP)
        self.cell(50, 9, f" Obtido: {self.ascii_safe(value_str)}", 1, align='L', fill=True, new_x=XPos.RIGHT, new_y=YPos.TOP)
        self.cell(30, 9, f" Lim: {self.ascii_safe(limit_str)}", 1, align='L', fill=True,
                  new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        if not is_ok:
            self.set_font('Helvetica', 'B', 9)
            self.set_text_color(200, 0, 30)
            self.cell(0, 6, f"   ATENCAO: {check_name} nao satisfaz a NBR 6118. Revisao do projeto obrigatoria.",
                      0, align='L', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            self.set_text_color(0, 0, 0)
        self.set_font('Helvetica', '', 10)

    def add_executive_table(self, header: list[str], data: list[list], widths: list[float]):
        self.set_font('Helvetica', 'B', 9)
        self.set_fill_color(240, 240, 240)
        for i, h in enumerate(header):
            self.cell(widths[i], 9, self.ascii_safe(str(h)), 1, align='C', fill=True, new_x=XPos.RIGHT, new_y=YPos.TOP)
        self.ln()
        
        self.set_font('Helvetica', '', 9)
        for row in data:
            for i, item in enumerate(row):
                self.cell(widths[i], 8, self.ascii_safe(str(item)), 1, align='C', new_x=XPos.RIGHT, new_y=YPos.TOP)
            self.ln()
        self.ln(6)

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

    def add_exam_audit_section(self, audit: dict):
        self.chapter_title('7', 'Comparação com Gabarito Oficial e Tese Técnica')
        self.section_title(audit.get("title", "Auditoria de Questão"))

        self.set_font('Helvetica', '', 9)
        self.set_text_color(45, 45, 45)
        statement = audit.get("statement", "")
        if statement:
            self.multi_cell(0, 5, f"Enunciado resumido: {statement}")
            self.ln(2)

        correct = audit.get("correct_reactions", {})
        exam = audit.get("exam_reactions", {})
        rows = []
        for key, value in correct.items():
            exam_value = exam.get(key, 0.0)
            rows.append([
                key,
                f"{exam_value:+.2f} kN",
                f"{float(value):+.2f} kN",
                f"{abs(float(value) - float(exam_value)):.2f} kN",
            ])
        if rows:
            self.add_executive_table(
                ['Grandeza', 'Gabarito', 'Solver / Física', 'Divergência'],
                rows,
                [35, 45, 55, 45],
            )

        self.section_title("Conclusão Pericial")
        self.set_font('Helvetica', 'B', 10)
        self.set_text_color(140, 0, 0)
        self.multi_cell(0, 5, audit.get("status", "Status não informado"))
        self.ln(2)
        self.set_font('Helvetica', '', 9)
        self.set_text_color(0, 0, 0)
        self.multi_cell(0, 5, audit.get("recurso_tese", "Tese técnica não informada."))
        self.ln(5)

def plot_wind_tower_diagram(profile: list, height: float, width_x: float, summary: dict, output_dir: str) -> str:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np
    import os
    
    if not profile:
        profile = [{"z": 0.0, "vk": 0.0, "q_Pa": 0.0, "force_kN": 0.0}]
    if height <= 0:
        height = 10.0
        
    # Configurar estilos do matplotlib
    plt.rcParams.update({
        "font.sans-serif": "DejaVu Sans",
        "font.family": "sans-serif"
    })
    
    # Criar figura com duas subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 6), sharey=True)
    
    z_coords = np.array([p['z'] for p in profile])
    q_vals = np.array([p['q_Pa'] for p in profile])
    
    # 1. Subplot de Pressão Dinâmica
    ax1.plot(q_vals, z_coords, color='#3b82f6', linewidth=2.5, label='Pressão q(z)')
    ax1.fill_betweenx(z_coords, q_vals, color='#3b82f6', alpha=0.15)
    
    # Desenhar setas de força de vento
    step_arrows = max(1, len(profile) // 10)
    for i in range(0, len(profile), step_arrows):
        p = profile[i]
        ax1.annotate("", xy=(p['q_Pa'], p['z']), xytext=(0, p['z']),
                     arrowprops=dict(arrowstyle="->", color="#3b82f6", lw=1.5))
        if i % 2 == 0:
            ax1.text(p['q_Pa'] + (max(q_vals) * 0.02), p['z'], f"{p['q_Pa']:.1f} Pa", fontsize=8, color='#1e3a8a', va='center')
            
    ax1.set_xlabel('Pressão Dinâmica (Pa)', fontsize=10, fontweight='bold', color='#1e293b')
    ax1.set_ylabel('Altura z (m)', fontsize=10, fontweight='bold', color='#1e293b')
    ax1.set_title('Perfil de Pressão (NBR 6123)', fontsize=11, fontweight='bold', color='#0f172a', pad=10)
    ax1.grid(True, linestyle='--', alpha=0.3)
    ax1.set_xlim(0, max(q_vals) * 1.2)
    
    # 2. Subplot da Torre Deformada Qualitativa
    tower_w = 4.0
    b_left = 2.0
    b_right = b_left + tower_w
    delta_max = 1.5 # Deflexão máxima visual
    
    # Desenhar terreno
    ax2.axhline(0, color='#64748b', linewidth=3)
    ax2.text(b_left + tower_w/2, -1.5, 'TERRENO', fontsize=8, fontweight='bold', color='#64748b', ha='center')
    
    # Desenhar silhueta original (Ghost/dashed)
    ax2.plot([b_left, b_left], [0, height], color='#cbd5e1', linestyle='--', linewidth=1.2)
    ax2.plot([b_right, b_right], [0, height], color='#cbd5e1', linestyle='--', linewidth=1.2)
    ax2.plot([b_left, b_right], [height, height], color='#cbd5e1', linestyle='--', linewidth=1.2)
    
    # Desenhar silhueta deformada: x(z) = delta_max * (z/H)^3
    z_dense = np.linspace(0, height, 100)
    dx_dense = delta_max * (z_dense / height)**3
    
    left_deformed = b_left + dx_dense
    right_deformed = b_right + dx_dense
    
    ax2.plot(left_deformed, z_dense, color='#1e293b', linewidth=2.5, label='Torre Deformada')
    ax2.plot(right_deformed, z_dense, color='#1e293b', linewidth=2.5)
    ax2.plot([left_deformed[-1], right_deformed[-1]], [height, height], color='#1e293b', linewidth=2.5)
    
    # Desenhar lajes/pisos deformados
    step_floors = max(1, len(profile) // 12)
    for i in range(0, len(profile), step_floors):
        fz = profile[i]['z']
        dx = delta_max * (fz / height)**3
        ax2.plot([b_left + dx, b_right + dx], [fz, fz], color='#64748b', linewidth=1, alpha=0.7)
        ax2.text(b_right + dx + 0.5, fz, f"z={fz:.0f}m", fontsize=8, color='#475569', va='center')
        
    ax2.set_title('Deformada Qualitativa', fontsize=11, fontweight='bold', color='#0f172a', pad=10)
    ax2.set_xlim(0, b_right + delta_max + 2.0)
    ax2.get_xaxis().set_visible(False)
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)
    ax2.spines['bottom'].set_visible(False)
    ax2.spines['left'].set_visible(False)
    
    plt.tight_layout()
    img_path = os.path.join(output_dir, "temp_wind_tower_diagram.png")
    plt.savefig(img_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    return img_path

def generate_professional_memorial(output_path: str, results: dict, project_meta: dict):
    import os
    pdf = ProfessionalMemorialPDF(project_meta)
    pdf.add_cover()
    
    # Verificar se os resultados contêm dados de pórtico ou treliça
    model_3d = results.get("model_3d")
    
    if model_3d:
        is_truss = model_3d.get("is_truss", False)
        elem_name = "Treliça Plana" if is_truss else "Pórtico Espacial"
        
        # 1. Parâmetros de Projeto
        pdf.chapter_title('1', f'Parâmetros e Configuração da {elem_name}')
        kpis = [
            ('Normas Aplicadas', 'NBR 6118, NBR 8800 (Aço)'),
            ('Módulo de Elasticidade (E)', '25.0 GPa' if is_truss else '210.0 GPa'),
            ('Número de Nós', str(len(model_3d.get("nodes", [])))),
            ('Número de Membros', str(len(model_3d.get("members", [])))),
            ('Tipo de Análise', 'Método dos Elementos Finitos (MEF Linear)'),
        ]
        pdf.add_kpi_grid(kpis)
        
        # 2. Nós e Coordenadas
        pdf.chapter_title('2', 'Coordenadas dos Nós e Condições de Apoio')
        header_nodes = ['Nó ID', 'X (m)', 'Y (m)', 'Z (m)', 'Condições de Apoio']
        widths_nodes = [30, 30, 30, 30, 70]
        
        data_nodes = []
        supports = model_3d.get("supports", {})
        for n in model_3d.get("nodes", []):
            nid = n.get("id")
            # Restrições de apoio
            res_list = supports.get(str(nid)) or supports.get(nid) or []
            if res_list:
                dof_labels = ["Ux", "Uy", "Uz", "Rx", "Ry", "Rz"]
                active_res = [dof_labels[i] for i in res_list]
                support_str = f"Apoio ({', '.join(active_res)})"
            else:
                support_str = "Livre"
            data_nodes.append([
                str(nid),
                f"{n.get('x'):.2f}",
                f"{n.get('y'):.2f}",
                f"{n.get('z'):.2f}",
                support_str
            ])
        pdf.add_executive_table(header_nodes, data_nodes, widths_nodes)
        
        # 3. Membros e Conectividade
        pdf.chapter_title('3', 'Tabela de Membros e Propriedades')
        header_mem = ['Membro ID', 'Nó Inicial (i)', 'Nó Final (j)', 'Comprimento (m)', 'Seção b x h (cm)']
        widths_mem = [35, 40, 40, 45, 30]
        
        data_mem = []
        for m in model_3d.get("members", []):
            nid_i = m.get("node_i")
            nid_j = m.get("node_j")
            node_i = next((n for n in model_3d.get("nodes", []) if n.get("id") == nid_i), None)
            node_j = next((n for n in model_3d.get("nodes", []) if n.get("id") == nid_j), None)
            length = 0.0
            if node_i and node_j:
                dx = node_j.get("x", 0) - node_i.get("x", 0)
                dy = node_j.get("y", 0) - node_i.get("y", 0)
                dz = node_j.get("z", 0) - node_i.get("z", 0)
                length = (dx*dx + dy*dy + dz*dz)**0.5
                
            sec = m.get("section", {})
            b = sec.get("b", 0) * 100
            h = sec.get("h", 0) * 100
            data_mem.append([
                str(m.get("id")),
                str(nid_i),
                str(nid_j),
                f"{length:.2f} m",
                f"{b:.0f}x{h:.0f}"
            ])
        pdf.add_executive_table(header_mem, data_mem, widths_mem)
        
        # 4. Deslocamentos Nodais Calculados
        pdf.chapter_title('4', 'Resultados: Deslocamentos Nodais (MEF)')
        header_disp = ['Nó ID', 'dx (mm)', 'dy (mm)', 'dz (mm)', 'Rx (rad)', 'Ry (rad)', 'Rz (rad)']
        widths_disp = [20, 25, 25, 25, 30, 30, 35]
        
        data_disp = []
        displacements = results.get("displacements", {})
        for nid_str, d_vec in displacements.items():
            data_disp.append([
                nid_str,
                f"{d_vec[0]*1000:.4f}",
                f"{d_vec[1]*1000:.4f}",
                f"{d_vec[2]*1000:.4f}",
                f"{d_vec[3]:.5f}",
                f"{d_vec[4]:.5f}",
                f"{d_vec[5]:.5f}"
            ])
        pdf.add_executive_table(header_disp, data_disp, widths_disp)
        
        # 5. Esforços Internos / Axiais
        pdf.chapter_title('5', 'Resultados: Esforços Internos nas Barras')
        efforts = results.get("efforts", {})
        if is_truss:
            header_eff = ['Membro ID', 'Nó i', 'Nó j', 'Força Axial N (kN)', 'Estado Estrutural']
            widths_eff = [35, 35, 35, 45, 40]
            data_eff = []
            for m in model_3d.get("members", []):
                mid = m.get("id")
                eff = efforts.get(str(mid)) or efforts.get(mid) or {"i": {"N": 0.0}}
                force = eff.get("i", {}).get("N", 0.0)
                
                state = "Nulo"
                if force > 0.01:
                    state = "TRAÇÃO"
                elif force < -0.01:
                    state = "COMPRESSÃO"
                    
                data_eff.append([
                    str(mid),
                    str(m.get("node_i")),
                    str(m.get("node_j")),
                    f"{force:.2f} kN",
                    state
                ])
            pdf.add_executive_table(header_eff, data_eff, widths_eff)
        else:
            header_eff = ['Barra ID', 'Nó i (N / Vy / Vz)', 'Nó j (N / Vy / Vz)', 'Momento i (My / Mz)', 'Momento j (My / Mz)']
            widths_eff = [25, 45, 45, 38, 38]
            data_eff = []
            for m in model_3d.get("members", []):
                mid = m.get("id")
                eff = efforts.get(str(mid)) or efforts.get(mid) or {"i": {}, "j": {}}
                ei = eff.get("i", {})
                ej = eff.get("j", {})
                
                str_i = f"N={ei.get('N',0):.1f} | Vy={ei.get('Vy',0):.1f}"
                str_j = f"N={ej.get('N',0):.1f} | Vy={ej.get('Vy',0):.1f}"
                str_mi = f"My={ei.get('My',0):.1f} | Mz={ei.get('Mz',0):.1f}"
                str_mj = f"My={ej.get('My',0):.1f} | Mz={ej.get('Mz',0):.1f}"
                
                data_eff.append([
                    str(mid),
                    str_i,
                    str_j,
                    str_mi,
                    str_mj
                ])
            pdf.add_executive_table(header_eff, data_eff, widths_eff)
            
        # 6. Reações de Apoio e Equilíbrio
        pdf.chapter_title('6', 'Equilíbrio de Nós e Reações de Apoio')
        equilibrium = results.get("equilibrium_audit", {})
        if equilibrium:
            pdf.set_font('Helvetica', 'B', 10)
            pdf.cell(0, 8, "Reações de Apoio nas Restrições:", 0, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.set_font('Helvetica', '', 9)
            
            header_reac = ['Nó ID', 'Rx (kN)', 'Ry (kN)', 'Rz (kN)', 'Mx (kNm)', 'My (kNm)', 'Mz (kNm)']
            widths_reac = [20, 28, 28, 28, 28, 28, 30]
            data_reac = []
            
            reactions = equilibrium.get("reactions", {})
            for nid_str, r_vec in reactions.items():
                data_reac.append([
                    nid_str,
                    f"{r_vec[0]:.2f}",
                    f"{r_vec[1]:.2f}",
                    f"{r_vec[2]:.2f}",
                    f"{r_vec[3]:.2f}",
                    f"{r_vec[4]:.2f}",
                    f"{r_vec[5]:.2f}"
                ])
            pdf.add_executive_table(header_reac, data_reac, widths_reac)
            
            pdf.set_font('Helvetica', 'B', 10)
            pdf.cell(0, 8, "Resumo de Equilíbrio de Forças Globais:", 0, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.set_font('Helvetica', '', 9)
            
            sum_applied = equilibrium.get("sum_applied_kN_m", [0]*6)
            sum_reactions = equilibrium.get("sum_reactions_kN_m", [0]*6)
            err_eq = equilibrium.get("equilibrium_error_kN_m", [0]*6)
            header_eq = ['Componente', 'Cargas Aplicadas', 'Reações Totais', 'Erro Residual']
            widths_eq = [50, 50, 50, 40]
            
            components = ['Força X (kN)', 'Força Y (kN)', 'Força Z (kN)', 'Momento X (kNm)', 'Momento Y (kNm)', 'Momento Z (kNm)']
            data_eq = []
            for idx, comp in enumerate(components):
                data_eq.append([
                    comp,
                    f"{sum_applied[idx]:.4f}",
                    f"{sum_reactions[idx]:.4f}",
                    f"{err_eq[idx]:.2e}"
                ])
            pdf.add_executive_table(header_eq, data_eq, widths_eq)
            
            is_ok = "CONVERGENTE / APROVADO" if equilibrium.get("is_equilibrated", True) else "REVISÃO REQUERIDA"
            pdf.set_font('Helvetica', 'B', 10)
            pdf.set_text_color(0, 122, 255)
            pdf.cell(0, 10, f"STATUS DA AUDITORIA ESTÁTICA: {is_ok}", 0, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.set_text_color(0, 0, 0)
            pdf.ln(5)

        if results.get("exam_audit"):
            pdf.add_exam_audit_section(results["exam_audit"])
            
        # 7. Diagramas e Anexos Gráficos
        annex_chapter = '8' if results.get("exam_audit") else '7'
        pdf.add_page()
        pdf.chapter_title(annex_chapter, 'Anexos Gráficos e Diagramas de Análise')
        
        image_dir = Path(
            results.get("diagram_dir")
            or project_meta.get("diagram_dir")
            or Path(output_path).parent
        )
        
        if is_truss:
            truss_img = image_dir / "diagrama_trelica_esforcos.png"
            if truss_img.exists():
                pdf.section_title("Diagrama de Esforços Axiais nas Barras (kN)")
                pdf.image(str(truss_img), x=20, w=170)
                pdf.ln(5)
                pdf.set_font('Helvetica', 'I', 8)
                pdf.set_text_color(100, 100, 100)
                pdf.cell(0, 5, "Figura 7.1: Distribuição de carregamento axial nas barras sob a convenção de cores: Azul (Tração) e Vermelho (Compressão).", 0, align='C', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                pdf.set_text_color(0, 0, 0)
        else:
            shear_img = image_dir / "diagrama_viga_cortante.png"
            moment_img = image_dir / "diagrama_viga_momento.png"
            
            if shear_img.exists():
                pdf.section_title("Diagrama de Esforço Cortante V(x) [kN]")
                pdf.image(str(shear_img), x=20, w=170)
                pdf.ln(5)
                pdf.set_font('Helvetica', 'I', 8)
                pdf.set_text_color(100, 100, 100)
                pdf.cell(0, 5, "Figura 7.1: Distribuição de Esforço Cortante ao longo da extensão da viga bi-apoiada com balanço.", 0, align='C', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                pdf.set_text_color(0, 0, 0)
                pdf.ln(5)
                
            if moment_img.exists():
                pdf.add_page()
                pdf.chapter_title(annex_chapter, 'Anexos Gráficos e Diagramas de Análise (Cont.)')
                pdf.section_title("Diagrama de Momento Fletor M(x) [kNm]")
                pdf.image(str(moment_img), x=20, w=170)
                pdf.ln(5)
                pdf.set_font('Helvetica', 'I', 8)
                pdf.set_text_color(100, 100, 100)
                pdf.cell(0, 5, "Figura 7.2: Distribuição de Momento Fletor. Fibra tracionada desenhada para cima (Convenção NBR 6118-2023).", 0, align='C', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                pdf.set_text_color(0, 0, 0)
            
    elif "profile" in results: # ANALISE DE VENTO OU ESTABILIDADE GLOBAL
        from wind_engine import WindEngine
        
        # 1. Parâmetros de Vento (NBR 6123)
        pdf.chapter_title('1', 'Parâmetros de Projeto e Ventos (NBR 6123)')
        
        v0 = results.get("v0", 30.0)
        s1 = results.get("s1", 1.0)
        s3 = results.get("s3", 1.0)
        s2_max = results.get("s2_max", 1.0)
        height = results.get("height", results.get("summary", {}).get("height", 30.0))
        width_x = results.get("width_x", 12.0)
        
        cat = results.get("categoria", 2)
        cls = results.get("classe", "B")
        params = WindEngine.get_s2_parameters(cat, cls)
        b = params['b']
        p = params['p']
        fr = params['fr']
        z_min = params['z_min']
        
        summary = results.get("summary", {})
        total_force = summary.get("total_force_kN", 0.0)
        base_moment = summary.get("base_moment_kNm", 0.0)
        max_vk = summary.get("max_vk", 0.0)
        max_q = summary.get("max_q_Pa", 0.0)
        cf_used = summary.get("cf_used", 1.2)
        g_dynamic = summary.get("g_dynamic", 1.0)
        
        kpis = [
            ('Normas Aplicadas', 'NBR 6123 (Vento), NBR 6118 (Estabilidade)'),
            ('Velocidade Básica (V0)', f"{v0:.1f} m/s"),
            ('Fator Topográfico (S1)', f"{s1:.2f}"),
            ('Fator de Rugosidade Máximo (S2)', f"{s2_max:.2f}"),
            ('Fator Estatístico (S3)', f"{s3:.2f}"),
            ('Altura Total da Edificação', f"{height:.1f} m"),
            ('Largura da Fachada (Lx)', f"{width_x:.1f} m"),
            ('Coeficiente de Arrasto (Cf)', f"{cf_used:.2f}"),
            ('Fator de Rajada Dinâmico (G)', f"{g_dynamic:.2f}"),
        ]
        pdf.add_kpi_grid(kpis)
        
        pdf.set_font('Helvetica', 'B', 10)
        pdf.cell(0, 8, "Fundamentação Teórica e Formulação NBR 6123:", 0, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_font('Helvetica', '', 9)
        pdf.multi_cell(0, 5, 
            "A velocidade característica do vento (Vk) em qualquer nível z acima do solo é calculada a partir da velocidade básica (V0) pelas seguintes relações normativas:\n"
            "   Vk(z) = V0 * S1 * S2(z) * S3\n\n"
            "Onde:\n"
            f"   - V0: Velocidade básica do vento correspondente a rajadas de 3 segundos, excedidas uma vez em 50 anos (adotada como {v0:.1f} m/s).\n"
            f"   - S1: Fator topográfico que considera o relevo local (adotado como {s1:.2f}).\n"
            "   - S2(z): Fator de rugosidade e dimensões da estrutura, calculado em função da altura z. A equação de S2(z) é dada por:\n"
            "         S2(z) = b * Fr * (z/10)^p\n"
            f"     Para a Categoria de Rugosidade {cat} e Classe {cls}, os coeficientes normativos são:\n"
            f"         b = {b:.3f},  p = {p:.3f},  Fr = {fr:.3f}  (com cota minima de cálculo z_min = {z_min:.1f} m).\n"
            f"   - S3: Fator estatístico de grau de segurança (adotado como {s3:.2f}).\n\n"
            "A pressão dinâmica (q_k) no nível z é dada por:\n"
            "   q(z) = 0,613 * Vk(z)^2  (em Pa ou N/m2)\n\n"
            "A força estática resultante ou dinâmica em cada pavimento é dada pela integração das pressões na área de projeção exposta lateral (Ae), multiplicada pelo coeficiente de arrasto (Cf) e fator de rajada dinâmico (G):\n"
            f"   F_vento(z) = q(z) * Ae * Cf * G   (com Cf = {cf_used:.2f} e G = {g_dynamic:.2f}).",
            0, align='L'
        )
        pdf.ln(5)
        
        # 2. Resumo de Esforços Globais
        pdf.chapter_title('2', 'Resumo de Esforços Globais e Estabilidade')
        
        gamma_z = results.get("gamma_z")
        has_stability = gamma_z is not None
        
        kpis_esforcos = [
            ('Força Cortante Total na Base (Vd)', f"{total_force:.1f} kN"),
            ('Momento de Tombamento na Base (Md)', f"{base_moment:.1f} kNm"),
            ('Velocidade de Projeto Máxima (Vk)', f"{max_vk:.1f} m/s"),
            ('Pressão Dinâmica Máxima (q0)', f"{max_q:.1f} Pa"),
        ]
        
        if has_stability:
            kpis_esforcos.extend([
                ('Coeficiente Gamma-z', f"{gamma_z:.3f}"),
                ('Classificação da Estrutura', 'Nós Fixos (Estável)' if gamma_z <= 1.1 else 'Nós Móveis (Segunda Ordem requerida)'),
                ('Aceleração de Pico (Conforto)', f"{results.get('peak_acceleration', 0.0):.4f} m/s2"),
                ('Status de Conforto Humano', str(results.get('comfort_status', 'OK'))),
                ('Status de Estabilidade Global', 'APROVADO / ESTÁVEL' if results.get('is_stable', True) else 'REVISAR GEOMETRIA'),
            ])
            
        pdf.add_kpi_grid(kpis_esforcos)
        
        if has_stability:
            pdf.set_font('Helvetica', 'B', 10)
            pdf.cell(0, 8, "Análise de Sensibilidade Global (Gama-z) e Conforto Humano:", 0, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.set_font('Helvetica', '', 9)
            
            # Estimar Delta M
            delta_m = 0.0
            if gamma_z > 1.0 and gamma_z != float('inf'):
                delta_m = base_moment * (gamma_z - 1.0)
                
            pdf.multi_cell(0, 5,
                "A verificação da estabilidade global é conduzida através do coeficiente Gama-z (Gama_z) conforme NBR 6118, item 15.4.2:\n"
                "   Gama_z = 1 / (1 - Delta_M / M1_tot)\n\n"
                "Onde:\n"
                f"   - M1_tot: Momento fletor total de 1ª ordem decorrente das forças de vento na base (Md = {base_moment:.1f} kNm).\n"
                f"   - Delta_M: Momento fletor de 2ª ordem global adicional gerado pelas cargas verticais permanentes e acidentais atuando sobre a estrutura deslocada horizontalmente (estimado em {delta_m:.1f} kNm).\n\n"
                "A NBR 6118 classifica a estrutura em:\n"
                "   - Estrutura de Nós Fixos (Gama_z <= 1,10): Os efeitos globais de 2ª ordem são inferiores a 10% e podem ser desconsiderados na análise de dimensionamento das seções.\n"
                "   - Estrutura de Nós Móveis (Gama_z > 1,10): Os efeitos de 2ª ordem devem ser obrigatoriamente considerados na modelagem estrutural.\n\n"
                "Adicionalmente, a verificação de aceleração de pico (comfort_status) no topo da edificação visa garantir a habitabilidade e o conforto dos ocupantes sob ventos frequentes de serviço, de acordo com a NBR 6123 (Davenport). "
                f"O limite normativo padrão de aceleração de pico de conforto humano é de 0,10 m/s2 a 0,15 m/s2. A aceleração de pico calculada para a torre é de {results.get('peak_acceleration', 0.0):.4f} m/s2.",
                0, align='L'
            )
            pdf.ln(5)
        
        # 3. Tabela de Forças Laterais por Altura
        pdf.chapter_title('3', 'Distribuição de Pressão e Força Lateral por Nível')
        
        header = ['Nível z (m)', 'Velocidade Vk (m/s)', 'Pressão q (Pa)', 'Força Lateral Fk (kN)']
        widths = [45, 45, 45, 45]
        
        profile = results.get("profile", [])
        data_table = []
        
        step_sample = 1
        if len(profile) > 25:
            step_sample = len(profile) // 20
            
        for i in range(0, len(profile), step_sample):
            p = profile[i]
            data_table.append([
                f"{p['z']:.1f} m",
                f"{p['vk']:.1f} m/s",
                f"{p['q_Pa']:.1f} Pa",
                f"{p.get('force_kN', 0.0):.1f} kN"
            ])
            
        if len(profile) > 0 and i < len(profile) - 1:
            p = profile[-1]
            data_table.append([
                f"{p['z']:.1f} m",
                f"{p['vk']:.1f} m/s",
                f"{p['q_Pa']:.1f} Pa",
                f"{p.get('force_kN', 0.0):.1f} kN"
            ])
            
        pdf.add_executive_table(header, data_table, widths)
        
        # 4. Diagrama de Vento e Torre
        pdf.add_page()
        pdf.chapter_title('4', 'Anexos Gráficos: Ação Física e Torre Deformada')
        
        output_dir = os.path.dirname(output_path) or "."
        img_path = None
        try:
            img_path = plot_wind_tower_diagram(profile, height, width_x, summary, output_dir)
            if os.path.exists(img_path):
                pdf.section_title("Diagrama de Ação do Vento e Deformada Qualitativa")
                pdf.image(img_path, x=20, w=170)
                pdf.ln(5)
                pdf.set_font('Helvetica', 'I', 8)
                pdf.set_text_color(100, 100, 100)
                pdf.cell(0, 5, "Figura 4.1: Distribuição de pressões do vento lateral q(z) e linha elástica deformada qualitativa da torre.", 0, align='C', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                pdf.set_text_color(0, 0, 0)
        except Exception as plot_err:
            pdf.set_font('Helvetica', 'I', 9)
            pdf.cell(0, 10, f"Erro ao gerar gráficos: {str(plot_err)}", 0, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        finally:
            if img_path and os.path.exists(img_path):
                try:
                    os.remove(img_path)
                except:
                    pass
    elif "diagrams" in results and "design" in results and "detailing" in results:
        # Memorial de Vigas (Viga Isolada/Contínua)
        pdf.chapter_title('1', 'Parâmetros de Projeto e Geometria')
        
        summary = results.get("summary", {})
        detailing = results.get("detailing", {})
        design = results.get("design", {})
        
        L = summary.get("L_m", 6.0)
        b = summary.get("b_m", 0.20)
        h = summary.get("h_m", 0.50)
        bf = summary.get("bf_m", 0.20)
        hf = summary.get("hf_m", 0.0)
        fck = summary.get("fck_MPa", 30.0)
        caa = summary.get("caa", 2)
        cover = summary.get("cover_mm", 30.0)
        
        # Differentiate rectangular and T-beam
        if bf > b:
            section_desc = f"Seção T: Mesa (bf)={bf*100:.1f} cm, Flange (hf)={hf*100:.1f} cm, Alma (bw)={b*100:.1f} cm, Altura (h)={h*100:.1f} cm"
        else:
            section_desc = f"Retangular: {b*100:.1f} cm x {h*100:.1f} cm"
            
        self_weight_str = "Desativado"
        if summary.get("include_self_weight"):
            material_label = {
                'concreto_armado': 'Concreto Armado',
                'concreto_simples': 'Concreto Simples',
                'aco': 'Aço Estrutural',
                'madeira': 'Madeira'
            }.get(summary.get("self_weight_material"), "Personalizado")
            self_weight_str = f"Ativado ({material_label} - {summary.get('self_weight_density', 25.0):.1f} kN/m³)"

        kpis = [
            ('Normas Aplicadas', 'NBR 6118:2023, NBR 6120'),
            ('Geometria da Seção', section_desc),
            ('Comprimento do Vão', f"{L:.2f} m"),
            ('Concreto (fck)', f"{fck:.1f} MPa"),
            ('Cobrimento Nominal (cnom)', f"{cover:.1f} mm"),
            ('Classe de Agressividade (CAA)', f"Classe {caa}"),
            ('Peso Próprio', self_weight_str),
        ]
        pdf.add_kpi_grid(kpis)
        
        # 2. Esforços de Cálculo e Reações de Apoio
        pdf.chapter_title('2', 'Esforços Solicitantes e Reações de Apoio')
        
        max_moment = summary.get("max_moment_kNm", 0.0)
        max_shear = summary.get("max_shear_kN", 0.0)
        total_load = summary.get("total_load_kN", 0.0)
        total_reaction = summary.get("total_reaction_kN", 0.0)
        
        kpis_esforcos = [
            ('Momento Fletor Máximo (Mk)', f"{max_moment:.2f} kNm"),
            ('Esforço Cortante Máximo (Vk)', f"{max_shear:.2f} kN"),
            ('Carga Total Aplicada', f"{total_load:.2f} kN"),
            ('Reação de Apoio Total', f"{total_reaction:.2f} kN"),
        ]
        pdf.add_kpi_grid(kpis_esforcos)
        
        # Tabela de Reações
        pdf.section_title("Reações de Apoio nos Vínculos")
        header_react = ['Posição x (m)', 'Reação Vertical (kN)']
        widths_react = [95, 95]
        
        data_react = []
        reactions = results.get("reactions", {})
        sorted_reactions = sorted(reactions.items(), key=lambda item: float(item[0]))
        for pos, val in sorted_reactions:
            if isinstance(val, dict):
                r_val = float(val.get('R', 0.0))
            else:
                r_val = float(val)
            data_react.append([f"{float(pos):.2f} m", f"{r_val:.2f} kN"])
            
        pdf.add_executive_table(header_react, data_react, widths_react)
        
        # 3. Verificação Normativa — Painel de Conformidade NBR 6118
        pdf.chapter_title('3', 'Painel de Conformidade Normativa (NBR 6118)')
        pdf.section_title("Verificacoes dos Estados Limites - ELU e ELS")
        
        # Ler dados de verificação do design
        flex    = design.get('flexure_bottom', {})
        shear_d = design.get('shear', {})
        crack_d = design.get('crack_width', {})
        defl_d  = design.get('deflection', {})
        
        max_moment = summary.get('max_moment_kNm', 0.0)
        max_shear  = summary.get('max_shear_kN', 0.0)
        max_defl   = summary.get('max_deflection_mm', 0.0)
        
        # ELU — Flexão
        kx      = float(flex.get('x_d', 0.0))
        kx_lim  = float(flex.get('x_d_lim', 0.45))
        flex_ok = kx <= kx_lim
        flex_status = 'ATENDE' if flex_ok else 'NÃO ATENDE'
        pdf.add_compliance_alert(
            'ELU - Flexao (Linha Neutra)',
            flex_status,
            f"kx = {kx:.3f}",
            f"kx,lim = {kx_lim:.2f}"
        )
        
        # ELU — Cisalhamento
        v_sd    = float(shear_d.get('Vsd_kN', max_shear * 1.4))
        v_rd2   = float(shear_d.get('Vrd2_kN', 0.0))
        shear_ok = v_sd <= v_rd2 if v_rd2 > 0 else True
        shear_status = shear_d.get('biela_status', 'ATENDE' if shear_ok else 'NÃO ATENDE')
        pdf.add_compliance_alert(
            'ELU - Cisalhamento (Biela Comprimida)',
            shear_status,
            f"Vsd = {v_sd:.1f} kN",
            f"Vrd2 = {v_rd2:.1f} kN"
        )
        
        # ELS — Fissuração
        wk       = float(crack_d.get('wk_mm', 0.0))
        wk_lim   = float(crack_d.get('limit_mm', 0.3))
        crack_ok = wk <= wk_lim
        crack_status = 'ATENDE' if crack_ok else 'NÃO ATENDE'
        pdf.add_compliance_alert(
            'ELS - Abertura de Fissuras (wk)',
            crack_status,
            f"wk = {wk:.3f} mm",
            f"wlim = {wk_lim:.2f} mm"
        )
        
        # ELS — Deformação / Flecha
        defl_lim = float(defl_d.get('limit_mm', L * 1000 / 250))
        defl_ok  = max_defl <= defl_lim
        defl_status = 'ATENDE' if defl_ok else 'NÃO ATENDE'
        pdf.add_compliance_alert(
            'ELS - Flecha Maxima (dmax)',
            defl_status,
            f"d = {max_defl:.2f} mm",
            f"dlim = L/250 = {defl_lim:.1f} mm"
        )
        
        # Status global — destaque em caso de reprovação geral
        overall = design.get('overall_status', 'ATENDE')
        any_fail = not all([flex_ok, shear_ok, crack_ok, defl_ok])
        if any_fail:
            pdf.ln(3)
            pdf.set_fill_color(200, 0, 30)
            pdf.set_text_color(255, 255, 255)
            pdf.set_font('Helvetica', 'B', 11)
            pdf.multi_cell(
                0, 9,
                "  PROJETO NAO ATENDE INTEGRALMENTE A NBR 6118:2023.\n"
                "  E IMPRESCINDIVEL REVISAO DAS DIMENSOES OU ARMADURAS ANTES DO DETALHAMENTO EXECUTIVO.",
                align='L', fill=True
            )
            pdf.set_text_color(0, 0, 0)
            pdf.ln(4)
        else:
            pdf.ln(3)
            pdf.set_fill_color(0, 140, 60)
            pdf.set_text_color(255, 255, 255)
            pdf.set_font('Helvetica', 'B', 11)
            pdf.cell(0, 9, "  TODAS AS VERIFICACOES NORMATIVAS ATENDIDAS - NBR 6118:2023",
                     0, align='L', fill=True, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.set_text_color(0, 0, 0)
            pdf.ln(4)
        
        # ── Seção de Detalhamento de Armaduras ───────────────────────────────
        # Exibida SOMENTE quando peso próprio está ativado (dimensionamento completo)
        include_sw = summary.get('include_self_weight', False)
        if include_sw:
            pdf.chapter_title('4', 'Detalhamento das Armaduras (NBR 6118 - Modulo 6/7)')
            
            # 4.1 Armadura longitudinal inferior
            det_inf = detailing.get('inf', {})
            det_sup = detailing.get('sup', {})
            exec_geo = detailing.get('executive', {})
            stirrups_txt = detailing.get('stirrups', 'N/A')
            skin_data = detailing.get('skin', {})
            torsion_data = detailing.get('torsion', {})
            
            # Armaduras longitudinais
            pdf.section_title("4.1 Armadura Longitudinal de Tracao (Inferior - CA-50)")
            def_inf_kpis = [
                ('Area Calculada (As,inf)', f"{det_inf.get('area_calc', 0.0):.2f} cm2"),
                ('Armadura Escolhida',       det_inf.get('spec', 'N/D')),
                ('Diâmetro',                 f"{det_inf.get('phi_mm', 0):.0f} mm"),
                ('Area Efetiva',             f"{det_inf.get('area_efet', 0.0):.2f} cm2"),
                ('Comprimento de Ancoragem Básico (lb)', f"{det_inf.get('lb_basic', 0.0):.1f} cm"),
                ('Comprimento de Ancoragem Necessário (lb,nec)', f"{det_inf.get('lb_nec', 0.0):.1f} cm"),
            ]
            pdf.add_kpi_grid(def_inf_kpis)
            
            pdf.section_title("4.2 Armadura de Compressao (Superior - CA-50)")
            def_sup_kpis = [
                ('Area Calculada (As,sup)', f"{det_sup.get('area_calc', 0.0):.2f} cm2"),
                ('Armadura Escolhida',       det_sup.get('spec', 'N/D')),
                ('Diâmetro',                 f"{det_sup.get('phi_mm', 0):.0f} mm"),
                ('Area Efetiva',             f"{det_sup.get('area_efet', 0.0):.2f} cm2"),
                ('Comprimento de Ancoragem (lb,nec)', f"{det_sup.get('lb_nec', 0.0):.1f} cm"),
            ]
            pdf.add_kpi_grid(def_sup_kpis)
            
            # Armadura transversal
            pdf.section_title("4.3 Armadura Transversal - Estribos (CA-60)")
            asw_cm2_m = detailing.get('Asw_cm2_m', 0.0) or (
                design.get('shear', {}).get('Asw_cm2_m', 0.0)
            )
            pdf.set_font('Helvetica', '', 10)
            estribo_kpis = [
                ('Especificação dos Estribos', stirrups_txt),
                ('Asw necessaria',             f"{asw_cm2_m:.2f} cm2/m"),
                ('Decalagem al',               f"{exec_geo.get('al_cm', 0.0):.1f} cm"),
            ]
            pdf.add_kpi_grid(estribo_kpis)
            
            # Pele (skin reinforcement)
            if skin_data.get('required'):
                pdf.section_title("4.4 Armadura de Pele (Norma NBR 6118, 17.3.5)")
                skin_kpis = [
                    ('Requerida', 'SIM' if skin_data.get('required') else 'NÃO'),
                    ('Area minima por face', f"{skin_data.get('As_skin_cm2', 0.0):.2f} cm2"),
                    ('Espaçamento máximo', f"{skin_data.get('s_max_cm', 0.0):.0f} cm"),
                ]
                pdf.add_kpi_grid(skin_kpis)
            
            # Torcao (se houver)
            if torsion_data.get('Asl_cm2', 0.0) > 0:
                pdf.section_title("4.5 Armadura de Torcao")
                torsion_kpis = [
                    ('Status', torsion_data.get('status', 'N/D')),
                    ('Asl (torcao longitudinal)', f"{torsion_data.get('Asl_cm2', 0.0):.2f} cm2"),
                ]
                pdf.add_kpi_grid(torsion_kpis)
            
            # Tabela-resumo executiva
            pdf.section_title("4.6 Resumo Executivo - Relacao de Ferragens")
            header_steel = ['Posicao', 'Especificacao', 'Area Ef. (cm2)', 'lb,nec (cm)']
            widths_steel = [40, 70, 45, 35]
            data_steel = [
                ['Inf. (Tracao)', det_inf.get('spec', 'N/D'), f"{det_inf.get('area_efet', 0.0):.2f}", f"{det_inf.get('lb_nec', 0.0):.1f}"],
                ['Sup. (Compressao)', det_sup.get('spec', 'N/D'), f"{det_sup.get('area_efet', 0.0):.2f}", f"{det_sup.get('lb_nec', 0.0):.1f}"],
                ['Estribos', stirrups_txt, f"{asw_cm2_m:.2f}/m", '-'],
            ]
            pdf.add_executive_table(header_steel, data_steel, widths_steel)
            
            chapter_diag = '5'
        else:
            # Sem peso próprio: armadura resumida (calculada pela API) 
            pdf.chapter_title('4', 'Resumo de Armaduras (Dimensionamento Parcial)')
            as_calc   = detailing.get('As_calc_cm2', design.get('flexure_bottom', {}).get('As_cm2', 0.0))
            as_min    = detailing.get('As_min_cm2', 0.0)
            asw_cm2_m = detailing.get('Asw_cm2_m', design.get('shear', {}).get('Asw_cm2_m', 0.0))
            steel_txt = detailing.get('steel_text', 'N/D')
            asw_txt   = detailing.get('Asw_text', 'N/D')
            kpis_design = [
                ('Armadura Long. Calculada (As)', f"{as_calc:.2f} cm2"),
                ('Armadura Minima (As,min)', f"{as_min:.2f} cm2"),
                ('Detalhamento Longitudinal', steel_txt),
                ('Armadura Transversal (Asw)', f"{asw_cm2_m:.2f} cm2/m"),
                ('Detalhamento Transversal', asw_txt),
                ('Flecha Máxima (ELS)', f"{max_defl:.2f} mm"),
            ]
            pdf.add_kpi_grid(kpis_design)
            pdf.set_font('Helvetica', 'I', 9)
            pdf.set_text_color(130, 80, 0)
            pdf.multi_cell(0, 5,
                "Nota: O detalhamento completo de armaduras (ancoragens, decalagem, estribos, "
                "pele e torcao) é gerado automaticamente quando o peso próprio da viga está "
                "ativado no modelo. Ative o peso próprio para obter o relatório executivo completo."
            )
            pdf.set_text_color(0, 0, 0)
            pdf.ln(4)
            chapter_diag = '5'
        
        # ── Capítulo de Diagramas ────────────────────────────────────────────
        # 4. Diagramas de Esforços e Deformações
        pdf.add_page()
        pdf.chapter_title(chapter_diag, 'Gráficos e Diagramas Estruturais')
        
        output_dir = os.path.dirname(output_path) or "."
        from academic_pdf import _plot_structural_diagrams
        
        mef_plot_data = {
            'x_m': [pt['x'] for pt in results['diagrams']['shear']],
            'V_kN': [pt['y'] for pt in results['diagrams']['shear']],
            'M_kNm': [pt['y'] for pt in results['diagrams']['moment']],
            'x_nodes_m': [pt['x'] for pt in results['diagrams']['deflection']],
            'delta_mm': [pt['y'] for pt in results['diagrams']['deflection']],
        }
        
        classical_plot_data = None
        if results.get('classical_diagrams'):
            cd = results['classical_diagrams']
            classical_plot_data = {
                'x_m': cd.get('x_m', []),
                'V_kN': cd.get('V_kN', []),
                'M_kNm': cd.get('M_kNm', []),
                'delta_mm': cd.get('delta_mm', [])
            }
            
        shear_img, moment_img, deflection_img = _plot_structural_diagrams(classical_plot_data, mef_plot_data, output_dir)
        
        try:
            if os.path.exists(shear_img):
                pdf.section_title("Diagrama de Esforço Cortante V(x)")
                pdf.image(shear_img, x=20, w=170)
                pdf.ln(3)
            if os.path.exists(moment_img):
                pdf.section_title("Diagrama de Momento Fletor M(x)")
                pdf.image(moment_img, x=20, w=170)
                pdf.ln(3)
            if deflection_img and os.path.exists(deflection_img):
                pdf.section_title("Diagrama de Deformação / Flecha y(x)")
                pdf.image(deflection_img, x=20, w=170)
                pdf.ln(3)
        except Exception as img_err:
            pdf.set_font('Helvetica', 'I', 9)
            pdf.cell(0, 10, f"Erro ao renderizar diagramas no PDF: {str(img_err)}", 0, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        finally:
            for path in [shear_img, moment_img, deflection_img]:
                if path and os.path.exists(path):
                    try:
                        os.remove(path)
                    except:
                        pass
    else:
        # Memorial padrão legado
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
