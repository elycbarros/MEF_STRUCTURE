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
                # Traduz dofs
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
            pdf.cell(0, 8, "Reações de Apoio nas Restrições:", 0, 1)
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
            pdf.cell(0, 8, "Resumo de Equilíbrio de Forças Globais:", 0, 1)
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
            pdf.cell(0, 10, f"STATUS DA AUDITORIA ESTÁTICA: {is_ok}", 0, 1)
            pdf.set_text_color(0, 0, 0)
            pdf.ln(5)
            
        # 7. Diagramas e Anexos Gráficos
        pdf.add_page()
        pdf.chapter_title('7', 'Anexos Gráficos e Diagramas de Análise')
        
        conversation_dir = "/Users/elycbarros/.gemini/antigravity/brain/79d6f7c6-9836-40b2-b91e-5104cbe67b15"
        
        if is_truss:
            truss_img = Path(conversation_dir) / "diagrama_trelica_esforcos.png"
            if truss_img.exists():
                pdf.section_title("Diagrama de Esforços Axiais nas Barras (kN)")
                # W=170mm (A4 margem esquerda/direita de 20mm deixa ~170mm livres)
                pdf.image(str(truss_img), x=20, w=170)
                pdf.ln(5)
                pdf.set_font('Helvetica', 'I', 8)
                pdf.set_text_color(100, 100, 100)
                pdf.cell(0, 5, "Figura 7.1: Distribuição de carregamento axial nas barras sob a convenção de cores: Azul (Tração) e Vermelho (Compressão).", 0, 1, 'C')
                pdf.set_text_color(0, 0, 0)
        else:
            shear_img = Path(conversation_dir) / "diagrama_viga_cortante.png"
            moment_img = Path(conversation_dir) / "diagrama_viga_momento.png"
            
            if shear_img.exists():
                pdf.section_title("Diagrama de Esforço Cortante V(x) [kN]")
                pdf.image(str(shear_img), x=20, w=170)
                pdf.ln(5)
                pdf.set_font('Helvetica', 'I', 8)
                pdf.set_text_color(100, 100, 100)
                pdf.cell(0, 5, "Figura 7.1: Distribuição de Esforço Cortante ao longo da extensão da viga bi-apoiada com balanço.", 0, 1, 'C')
                pdf.set_text_color(0, 0, 0)
                pdf.ln(5)
                
            if moment_img.exists():
                pdf.add_page()
                pdf.chapter_title('7', 'Anexos Gráficos e Diagramas de Análise (Cont.)')
                pdf.section_title("Diagrama de Momento Fletor M(x) [kNm]")
                pdf.image(str(moment_img), x=20, w=170)
                pdf.ln(5)
                pdf.set_font('Helvetica', 'I', 8)
                pdf.set_text_color(100, 100, 100)
                pdf.cell(0, 5, "Figura 7.2: Distribuição de Momento Fletor. Fibra tracionada desenhada para cima (Convenção NBR 6118-2023).", 0, 1, 'C')
                pdf.set_text_color(0, 0, 0)
            
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
