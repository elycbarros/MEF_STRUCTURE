from __future__ import annotations
from fpdf import FPDF
from pathlib import Path
from datetime import datetime
import json

class RadierPDF(FPDF):
    def __init__(self, project_meta: dict):
        super().__init__()
        self.project_meta = project_meta
        self.set_auto_page_break(auto=True, margin=15)
        
    def header(self):
        # Logo placeholder (can be improved if logo file exists)
        self.set_font('Arial', 'B', 15)
        self.set_text_color(29, 23, 31) # Apple-ish dark
        self.cell(0, 10, 'Radier Lab Pro - Memorial Descritivo', 0, 1, 'L')
        
        self.set_font('Arial', '', 9)
        self.set_text_color(100, 100, 100)
        obra = self.project_meta.get('obra', 'N/D')
        data = self.project_meta.get('emissao', datetime.now().strftime('%d/%m/%Y'))
        self.cell(0, 5, f'Obra: {obra} | Data: {data}', 0, 1, 'L')
        self.ln(5)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(128)
        self.cell(0, 10, f'Página {self.page_no()} | Radier Lab Pro Engine | v2026', 0, 0, 'C')

    def chapter_title(self, title):
        self.set_font('Arial', 'B', 12)
        self.set_fill_color(240, 240, 245)
        self.cell(0, 8, title, 0, 1, 'L', fill=True)
        self.ln(4)

    def section_title(self, title):
        self.set_font('Arial', 'B', 10)
        self.cell(0, 6, title, 0, 1, 'L')
        self.ln(2)

    def add_metric(self, label, value, unit=''):
        self.set_font('Arial', '', 9)
        self.set_text_color(80, 80, 80)
        self.write(5, f'{label}: ')
        self.set_font('Arial', 'B', 9)
        self.set_text_color(0, 0, 0)
        self.write(5, f'{value} {unit}\n')

    def add_table(self, header, data, col_widths):
        self.set_font('Arial', 'B', 9)
        self.set_fill_color(230, 230, 230)
        for i, h in enumerate(header):
            self.cell(col_widths[i], 7, h, 1, 0, 'C', fill=True)
        self.ln()
        
        self.set_font('Arial', '', 8)
        for row in data:
            for i, item in enumerate(row):
                self.cell(col_widths[i], 6, str(item), 1, 0, 'C')
            self.ln()
        self.ln(5)

    def add_wind_section(self, wind_results: dict):
        if not wind_results: return
        self.chapter_title('11. Análise de Vento (NBR 6123)')
        
        cfg = wind_results.get('config', {})
        self.add_metric('Velocidade Básica (v0)', f"{cfg.get('v0')} m/s")
        self.add_metric('Fator Topográfico (S1)', f"{cfg.get('s1')}")
        self.add_metric('Fator Estatístico (S3)', f"{cfg.get('s3')}")
        cf_val = wind_results.get('cf') or wind_results.get('geometry', {}).get('cf', 'N/D')
        self.add_metric('Coeficiente de Arrasto (Cf)', f"{cf_val}")
        self.ln(5)

        profile = wind_results.get('profile', [])
        if profile:
            header = ['Altura (m)', 'Pressão Dinâmica (Pa)', 'Força de Arrasto (kN)']
            data = []
            for p in profile:
                force_kN = p.get('f_total_kN') if 'f_total_kN' in p else (p.get('f_drag_N', 0) / 1000.0)
                data.append([
                    f"{p['z']:.1f}",
                    f"{p['q_Pa']:.2f}",
                    f"{force_kN:.2f}"
                ])
            self.add_table(header, data, [60, 60, 60])
        self.ln(5)

    def add_stability_section(self, stability_data: dict):
        if not stability_data: return
        self.chapter_title('12. Estabilidade Global e Conforto (Prédio Alto)')
        
        res = stability_data
        status_color = (0, 128, 0) if res.get('is_stable') else (200, 0, 0)
        self.set_text_color(*status_color)
        self.add_metric('Coeficiente Gama-Z', f"{res.get('gamma_z'):.3f}")
        self.set_text_color(0, 0, 0)
        
        self.add_metric('Fator de Amplificação (P-Delta)', f"{res.get('p_delta_factor'):.3f}")
        self.add_metric('Aceleração de Pico (Topo)', f"{res.get('peak_acceleration_ms2'):.4f} m/s2")
        
        self.add_metric('Iteracoes P-Delta', f"{res.get('p_delta_iterations', 1)}")
        
        if res.get('is_divergent'):
            self.set_text_color(200, 0, 0)
            self.add_metric('ALERTA CRITICO', 'ESTRUTURA DIVERGENTE (INSTAVEL)')
            self.set_text_color(0, 0, 0)

        comfort = res.get('comfort_status', 'N/D')
        comfort_color = (200, 0, 0) if comfort == 'CRITICO' else (0, 128, 0)
        self.set_text_color(*comfort_color)
        self.add_metric('Status de Conforto Humano', comfort)
        self.set_text_color(0, 0, 0)
        self.ln(5)

    def add_piles_section(self, pile_results: list):
        if not pile_results: return
        self.chapter_title('13. Fundação Profunda (Radier Estaqueado)')
        
        header = ['ID', 'X (m)', 'Y (m)', 'Rigidez (kN/m)', 'Reação (kN)']
        data = []
        for p in pile_results:
            data.append([
                p.get('id', 'EST'),
                f"{p.get('x', 0):.2f}",
                f"{p.get('y', 0):.2f}",
                f"{p.get('stiffness_kN_m', 0):.0f}",
                f"{p.get('reaction_kN', 0):.2f}"
            ])
        self.add_table(header, data, [30, 30, 30, 50, 50])
        self.ln(5)

    def add_frame_section(self, frame_results: dict):
        if not frame_results: return
        self.chapter_title('10. Análise de Pórtico 3D (StrucPy)')
        
        design = frame_results.get('design_results', {})
        pillars = design.get('pillars', [])
        beams = design.get('beams', [])

        if pillars:
            self.section_title('Dimensionamento de Pilares')
            header = ['ID', 'Seção (cm)', 'Nd (kN)', 'As (cm2)', 'Taxa (%)']
            data = []
            for i, p in enumerate(pillars):
                pid = p.get('id') or p.get('Column') or p.get('Node1') or f"P{i+1}"
                b_val = p.get('b', 300) / 10.0 # cm
                h_val = p.get('d', 300) / 10.0 # cm
                taxa = (p.get('As', 0) / (b_val * h_val)) * 100 if b_val and h_val else 0
                data.append([
                    pid,
                    f"{b_val:.0f}x{h_val:.0f}",
                    _fmt(p.get('Nd', 'N/D')),
                    _fmt(p.get('As', 'N/D')),
                    f"{taxa:.2f}%" if p.get('As') else "N/D"
                ])
            self.add_table(header, data, [20, 40, 40, 40, 40])

        if beams:
            self.section_title('Dimensionamento de Vigas')
            header = ['ID', 'Seção (cm)', 'Mk (kNm)', 'As Inf (cm2)', 'As Sup (cm2)']
            data = []
            for i, b in enumerate(beams):
                bid = b.get('id') or b.get('Beam') or f"V{i+1}"
                b_val = b.get('b', 200) / 10.0 # cm
                h_val = b.get('d', 500) / 10.0 # cm
                data.append([
                    bid,
                    f"{b_val:.0f}x{h_val:.0f}",
                    _fmt(b.get('max_moment') or b.get('M_max', 'N/D')),
                    _fmt(b.get('As_bottom') or b.get('As1', 'N/D')),
                    _fmt(b.get('As_top') or b.get('As2', 'N/D'))
                ])
            self.add_table(header, data, [20, 40, 40, 40, 40])
        self.ln(5)

    def add_special_elements_section(self, special_elements_results: list):
        if not special_elements_results: return
        self.chapter_title('13. Elementos Especiais (Escadas e Reservatórios)')
        
        for elem in special_elements_results:
            type_label = "ESCADA" if elem.get('type') == 'stair' else "RESERVATÓRIO"
            self.section_title(f"Elemento: {elem.get('id')} ({type_label})")
            
            if elem.get('type') == 'stair':
                self.add_metric('Comprimento (L)', f"{elem.get('L'):.2f} m")
                self.add_metric('Carga (q)', f"{elem.get('q'):.2f} kN/m2")
                self.add_metric('Momento Max (Mk)', f"{elem.get('Mk'):.2f} kNm/m")
                self.add_metric('Armadura (As)', f"{elem.get('As_cm2_m'):.2f} cm2/m")
            else:
                self.add_metric('Altura (H)', f"{elem.get('H'):.2f} m")
                self.add_metric('Empuxo Max', f"{elem.get('p_max_kPa'):.2f} kPa")
                self.add_metric('Momento Engaste', f"{elem.get('M_base'):.2f} kNm/m")
                self.add_metric('Armadura Base', f"{elem.get('As_base'):.2f} cm2/m")
            self.ln(3)
        self.ln(5)

    def add_ssi_section(self, ssi_data: dict):
        if not ssi_data: return
        self.chapter_title('14. Interação Solo-Estrutura (SSI) Iterativa')
        
        self.add_metric('Método', 'Pseudo-Acoplado (Half-space Boussinesq)')
        self.add_metric('Iterações', ssi_data.get('iterations', 'N/D'))
        self.add_metric('Erro de Convergência', f"{ssi_data.get('error', 0)*100:.4f}%")
        
        if ssi_data.get('kv_stats'):
            stats = ssi_data.get('kv_stats')
            self.add_metric('Rigidez Média (kv_avg)', f"{stats.get('avg', 0)/1000:.0f} kN/m3")
            self.add_metric('Variação (Min/Max)', f"{stats.get('min', 0)/1000:.0f} / {stats.get('max', 0)/1000:.0f} kN/m3")
        
        self.ln(5)

    def add_markdown_content(self, markdown_text: str):
        if not markdown_text: return
        self.chapter_title('Memorial Técnico Detalhado (M4)')
        
        lines = markdown_text.split('\n')
        in_table = False
        table_data = []
        table_header = []
        
        for line in lines:
            line = line.strip()
            if not line:
                if in_table:
                    self._render_parsed_table(table_header, table_data)
                    in_table = False
                    table_data = []
                    table_header = []
                self.ln(2)
                continue
            
            # Icons replacement for standard fonts
            line = line.replace('✅', '[OK]').replace('❌', '[FAIL]').replace('⚠️', '[!]').replace('📌', '*')
            
            if line.startswith('# '):
                self.chapter_title(line[2:])
            elif line.startswith('## '):
                self.section_title(line[3:])
            elif line.startswith('- '):
                self.set_font('Arial', '', 9)
                self.set_text_color(60, 60, 60)
                self.multi_cell(0, 5, f'  * {line[2:]}')
            elif line.startswith('|'):
                # Simple table parser
                if '---' in line: continue # skip separator
                parts = [p.strip() for p in line.split('|') if p.strip()]
                if not in_table:
                    table_header = parts
                    in_table = True
                else:
                    table_data.append(parts)
            else:
                self.set_font('Arial', '', 9)
                self.set_text_color(40, 40, 40)
                self.multi_cell(0, 5, line)
        
        if in_table:
            self._render_parsed_table(table_header, table_data)

    def _render_parsed_table(self, header, data):
        if not header: return
        num_cols = len(header)
        col_width = 190 / num_cols
        self.add_table(header, data, [col_width] * num_cols)

def _fmt(val, digits=2, suffix=''):
    if val is None or val == 'N/D':
        return 'N/D'
    try:
        return f"{float(val):.{digits}f}{suffix}"
    except (ValueError, TypeError):
        return str(val)

def _go_no_go_color(go_no_go: str) -> tuple:
    """Retorna RGB para o status go/no-go."""
    mapping = {
        "go_preliminar": (52, 199, 89),      # verde
        "conditional_go": (255, 159, 10),    # amarelo/laranja
        "hold": (255, 69, 58),               # vermelho suave
        "no_go": (255, 45, 85),              # vermelho forte
    }
    return mapping.get(go_no_go, (100, 100, 100))


def _add_executive_cover(pdf: "RadierPDF", results: dict, project_meta: dict) -> None:
    """Página 1: Capa executiva com go/no-go em destaque."""
    exec_decision = results.get("executive_decision", {})
    go_no_go = exec_decision.get("go_no_go", "N/D")
    executive_label = exec_decision.get("executive_label", "N/D")
    main_rec = exec_decision.get("main_recommendation", "N/D")
    next_step = exec_decision.get("next_step", "N/D")
    blocking = exec_decision.get("blocking_count", 0)
    restricao = exec_decision.get("restriction_count", 0)
    alertas = exec_decision.get("alert_count", 0)

    master = results.get("master", {})
    geotech = results.get("memorial", {}).get("verificacoes_geotecnicas", {})
    punching = results.get("memorial", {}).get("verificacoes_estruturais", {}).get("puncao", {})
    service = results.get("memorial", {}).get("verificacoes_de_servico", {})
    kv_conf = exec_decision.get("kv_confidence")

    # -- Topo: identidade do projeto -------------------------------------------
    pdf.set_fill_color(29, 23, 31)
    pdf.rect(0, 0, 210, 42, "F")
    pdf.set_y(10)
    pdf.set_font("Arial", "B", 18)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 10, "RADIER LAB PRO - MEMORIAL DE CÁLCULO", 0, 1, "C")
    pdf.set_font("Arial", "", 9)
    pdf.set_text_color(180, 180, 180)
    pdf.cell(0, 6, f"Obra: {project_meta.get('obra', 'N/D')}  |  Local: {project_meta.get('local', 'N/D')}  |  Emissão: {project_meta.get('emissao', 'N/D')}", 0, 1, "C")
    pdf.set_text_color(0, 0, 0)
    pdf.set_y(50)

    # -- Bloco Go/No-Go --------------------------------------------------------
    r, g, b = _go_no_go_color(go_no_go)
    pdf.set_fill_color(r, g, b)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", "B", 22)
    pdf.cell(0, 18, f"  {executive_label.upper()}", 0, 1, "L", fill=True)
    pdf.set_text_color(0, 0, 0)
    pdf.ln(4)

    # -- Recomendação principal ------------------------------------------------
    pdf.set_font("Arial", "B", 10)
    pdf.cell(0, 7, "Recomendação Principal:", 0, 1)
    pdf.set_font("Arial", "", 9)
    pdf.set_text_color(60, 60, 60)
    pdf.multi_cell(0, 5, main_rec)
    pdf.set_text_color(0, 0, 0)
    pdf.ln(3)

    pdf.set_font("Arial", "B", 10)
    pdf.cell(0, 7, "Próximo Passo:", 0, 1)
    pdf.set_font("Arial", "I", 9)
    pdf.set_text_color(60, 60, 60)
    pdf.multi_cell(0, 5, next_step)
    pdf.set_text_color(0, 0, 0)
    pdf.ln(5)

    # -- Sanity Checks ---------------------------------------------------------
    sanity_checks = results.get("sanity_checks", {})
    if sanity_checks:
        pdf.set_font("Arial", "B", 10)
        pdf.set_fill_color(240, 240, 245)
        pdf.cell(0, 7, "  Sanity Checks Normativos", 0, 1, "L", fill=True)
        pdf.ln(3)

        pdf.set_font("Arial", "B", 8)
        badges = [
            ("Solo", sanity_checks.get("pressao_solo_ok")),
            ("Recalque", sanity_checks.get("recalque_ok")),
            ("Punção", sanity_checks.get("puncao_ok"))
        ]
        
        for label, is_ok in badges:
            if is_ok is None: continue
            if is_ok:
                pdf.set_fill_color(220, 252, 231) # Green-100
                pdf.set_text_color(22, 101, 52)   # Green-800
                status_text = "PASS"
            else:
                pdf.set_fill_color(254, 226, 226) # Red-100
                pdf.set_text_color(153, 27, 27)   # Red-800
                status_text = "FAIL"
            pdf.cell(50, 8, f"{label}: {status_text}", border=0, ln=0, align="C", fill=True)
            pdf.set_x(pdf.get_x() + 4)
            
        pdf.set_text_color(0, 0, 0)
        pdf.ln(12)


    # -- KPIs da capa ---------------------------------------------------------
    pdf.set_font("Arial", "B", 10)
    pdf.set_fill_color(240, 240, 245)
    pdf.cell(0, 7, "  KPIs do Projeto", 0, 1, "L", fill=True)
    pdf.ln(3)

    # Calculate exact minimum reinforcement ratio and contact loss
    as_min = results.get('memorial', {}).get('verificacoes_estruturais', {}).get('flexao', {}).get('As_min_total_cm2_m', 0.0)
    h_m = master.get('h', 1.0)
    rho_min_pct = (as_min / (h_m * 10000.0)) * 100.0 if h_m > 0 else 0.0
    contact_loss_pct = geotech.get('contact_loss_pct', 0.0)

    kpis = [
        ("Dimensões (m)", f"{_fmt(master.get('Lx'))} x {_fmt(master.get('Ly'))}"),
        ("Espessura h (m)", _fmt(master.get("h"), 2)),
        ("Área (m2)", _fmt(master.get("area_m2"), 1)),
        ("fck (MPa)", _fmt(master.get("fck"), 0)),
        ("kv (kN/m3)", _fmt(master.get("kv", 0) / 1000.0 if master.get("kv") else None, 0)),
        ("Confiança kv", f"{_fmt(kv_conf, 2)}" if kv_conf is not None else "N/D"),
        ("Pressão Máx (kPa)", _fmt(geotech.get("pressao_max_modelo_kPa"), 2)),
        ("Sigma_adm (kPa)", _fmt(geotech.get("tensao_admissivel_kPa"), 2)),
        ("Perda de Contato (%)", f"{_fmt(contact_loss_pct, 2)}%"),
        ("Taxa Armadura Mín (%)", f"{_fmt(rho_min_pct, 3)}%"),
        ("Ratio Pressão", _fmt(exec_decision.get("pressure_ratio"), 3)),
        ("Ratio Punção", _fmt(exec_decision.get("punching_ratio"), 3)),
        ("Recalque Máx (mm)", _fmt(service.get("w_max_mm"), 2)),
        ("Bloqueios / Restrições / Alertas", f"{blocking} / {restricao} / {alertas}"),
    ]

    pdf.set_font("Arial", "", 9)
    col_w = [90, 100]
    for label, value in kpis:
        pdf.set_text_color(80, 80, 80)
        pdf.cell(col_w[0], 6, f"  {label}", 1, 0)
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("Arial", "B", 9)
        pdf.cell(col_w[1], 6, f"  {value}", 1, 1)
        pdf.set_font("Arial", "", 9)

    pdf.ln(8)

    # -- Dados do responsável --------------------------------------------------
    pdf.set_font("Arial", "B", 9)
    pdf.cell(0, 6, f"Responsável Técnico: {project_meta.get('responsavel', 'N/D')}  |  Registro: {project_meta.get('registro', 'N/D')}", 0, 1)
    pdf.set_font("Arial", "I", 8)
    pdf.set_text_color(120, 120, 120)
    pdf.cell(0, 5, "Documento gerado automaticamente pelo Radier Lab Pro Engine. Sujeito à revisão do engenheiro responsável.", 0, 1)
    pdf.set_text_color(0, 0, 0)
    pdf.add_page()


def generate_radier_report_pdf(output_path: str | Path, results: dict, project_meta: dict):
    pdf = RadierPDF(project_meta)
    pdf.add_page()
    
    is_laje = results.get('system_type') == 'laje'
    master = results.get('master', {})

    # Capa executiva (Frente F)
    _add_executive_cover(pdf, results, project_meta)

    # 1. Resumo Executivo
    pdf.chapter_title('1. Resumo Executivo')
    exec_decision = results.get('executive_decision', {})
    pdf.add_metric('Decisão', exec_decision.get('executive_label', 'N/D'))
    pdf.add_metric('Status', exec_decision.get('decision_status', 'N/D'))
    pdf.add_metric('Go/No-Go', exec_decision.get('go_no_go', 'N/D'))
    pdf.add_metric('Recomendação Principal', exec_decision.get('main_recommendation', 'N/D'))
    pdf.ln(5)
    
    pdf.add_metric('Concreto fck', _fmt(master.get('fck'), 0, ' MPa'))
    pdf.ln(5)

    # 2.1 Resumo de Materiais
    pdf.chapter_title('2.1 Resumo de Materiais (Estimativo)')
    metrics = results.get('memorial', {}).get('verificacoes_estruturais', {}).get('flexao', {}).get('metrics', {})
    if metrics:
        pdf.add_metric('Volume de Concreto', _fmt(metrics.get('concrete_volume_m3')), ' m3')
        pdf.add_metric('Peso Total de Aço (+10%)', _fmt(metrics.get('total_steel_kg')), ' kg')
        pdf.add_metric('Taxa de Aço (por volume)', _fmt(metrics.get('steel_density_kg_m3')), ' kg/m3')
        pdf.add_metric('Taxa de Aço (por área)', _fmt(metrics.get('steel_density_kg_m2')), ' kg/m2')
    else:
        pdf.set_font('Arial', 'I', 9)
        pdf.cell(0, 5, 'Dados de consumo não disponíveis nesta simulação.', 0, 1)
    pdf.ln(5)
    
    # 3. Verificações Geotécnicas ou Reações de Apoio
    if is_laje:
        pdf.chapter_title('3. Reações de Apoio (Nodal)')
        aco_comb = results.get('memorial', {}).get('acoes_e_combinacoes', {})
        reacoes = aco_comb.get('reacoes_apoio', [])
        if reacoes:
            header = ['Pilar', 'Posição X (m)', 'Posição Y (m)', 'Reação Pz (kN)']
            data = [[r['id'], f"{r['x']:.2f}", f"{r['y']:.2f}", f"{r['reaction_kN']:.2f}"] for r in reacoes]
            pdf.add_table(header, data, [40, 50, 50, 50])
            pdf.add_metric('Somatório das Reações', _fmt(aco_comb.get('carga_pilares_kN')), ' kN')
        else:
            pdf.cell(0, 5, 'Dados de reações não disponíveis.', 0, 1)
    else:
        pdf.chapter_title('3. Verificações Geotécnicas')
        geotech = results.get('memorial', {}).get('verificacoes_geotecnicas', {})
        service = results.get('memorial', {}).get('verificacoes_de_servico', {})
        pdf.add_metric('Pressão Média de Contato', _fmt(geotech.get('pressao_media_kPa')), ' kPa')
        pdf.add_metric('Pressão Máxima de Contato', _fmt(geotech.get('pressao_max_modelo_kPa')), ' kPa')
        pdf.add_metric('Tensão Admissível do Solo', _fmt(geotech.get('tensao_admissivel_kPa')), ' kPa')
        pdf.add_metric('Recalque Máximo Calculado', _fmt(service.get('w_max_mm')), ' mm')
        pdf.add_metric('Status Pressão', 'ATENDE' if geotech.get('atende_pressao_max_modelo') else 'NÃO ATENDE')
    pdf.ln(5)
    
    # 4. Verificações Estruturais (Punção)
    pdf.chapter_title('4. Verificações Estruturais')
    punching = results.get('memorial', {}).get('verificacoes_estruturais', {}).get('puncao', {})
    if punching.get('status') == 'nao_aplicavel_sem_pilares':
        pdf.set_font('Arial', 'I', 9)
        pdf.cell(0, 5, 'Punção não aplicável para carregamento uniforme.', 0, 1)
    else:
        pdf.add_metric('Ratio Máximo Punção', _fmt(punching.get('ratio_max'), 2))
        pdf.add_metric('Pilar Crítico', punching.get('critical_local', 'N/D'))
        pdf.add_metric('Status Punção', 'ATENDE' if punching.get('atende') else 'NÃO ATENDE')
    pdf.ln(5)
    
    # 5. Detalhamento de Armadura
    pdf.chapter_title('5. Detalhamento de Armadura')
    flexure = results.get('memorial', {}).get('verificacoes_estruturais', {}).get('flexao', {})
    
    header = ['Direção', 'Posição', 'As calc (cm2/m)', 'Sugestão']
    data = [
        ['X', 'Superior', _fmt(flexure.get('Asx_top_adot_max_cm2_m')), flexure.get('sugestao_x_sup', 'N/D')],
        ['Y', 'Superior', _fmt(flexure.get('Asy_top_adot_max_cm2_m')), flexure.get('sugestao_y_sup', 'N/D')],
        ['X', 'Inferior', _fmt(flexure.get('Asx_bottom_adot_max_cm2_m')), flexure.get('sugestao_x_inf', 'N/D')],
        ['Y', 'Inferior', _fmt(flexure.get('Asy_bottom_adot_max_cm2_m')), flexure.get('sugestao_y_inf', 'N/D')],
    ]
    pdf.add_table(header, data, [30, 30, 50, 80])

    # 5.1 Verificação de Fissuração (ELS-W)
    pdf.section_title('5.1 Verificação de Fissuração (NBR 6118)')
    service = results.get('memorial', {}).get('verificacoes_de_servico', {})
    if service:
        pdf.add_metric('Abertura Máx X (wk,x)', _fmt(service.get('wk_x_max_mm')), ' mm')
        pdf.add_metric('Abertura Máx Y (wk,y)', _fmt(service.get('wk_y_max_mm')), ' mm')
        pdf.add_metric('Limite Normativo', _fmt(service.get('wk_limit_mm')), ' mm')
        status_wk = "ATENDE" if service.get('wk_x_ok') and service.get('wk_y_ok') else "NÃO ATENDE"
        pdf.add_metric('Status Fissuração', status_wk)
    pdf.ln(5)

    # 6. Comparativo Metodológico
    pdf.chapter_title('6. Comparativo Metodológico')
    comp = results.get('memorial', {}).get('comparativo_metodologias', {})
    analytical = comp.get('analytical', {})
    geotech = results.get('memorial', {}).get('verificacoes_geotecnicas', {})
    if not is_laje:
        pdf.add_metric('Pressão Max MEF', _fmt(geotech.get('pressao_max_modelo_kPa'), 2, ' kPa'))
    pdf.add_metric('Pressão Max Analítico', _fmt(analytical.get('q_max_kPa'), 2, ' kPa'))
    pdf.ln(5)

    # 7. Checklist Normativo
    pdf.chapter_title('7. Checklist de Conformidade Normativa')
    checklist = results.get('memorial', {}).get('base_normativa', {}).get('checklist_detalhado', [])
    
    header = ['Tema', 'Referência', 'Status']
    data = []
    for item in checklist:
        data.append([
            item.get('theme', 'N/D'),
            item.get('reference', 'N/D'),
            item.get('status', 'N/D')
        ])
    pdf.add_table(header, data, [60, 100, 30])
    
    # 8. Trilha de Auditoria Analitica (8 Passos)
    pdf.chapter_title('8. Trilha de Auditoria Analitica (8 Passos)')
    
    # Passo 1: Geometria
    pdf.section_title('Passo 01: Geometria e Matriz do Modelo')
    pdf.set_font('Courier', '', 9)
    pdf.multi_cell(0, 5, f"Lx = {_fmt(master.get('Lx'))} m, Ly = {_fmt(master.get('Ly'))} m, h = {_fmt(master.get('h'))} m\n"
                         f"Area = {_fmt(master.get('area_m2'))} m2\n"
                         f"Metodo: Elementos Finitos (Mindlin-Reissner)")
    pdf.ln(3)

    # Passo 2: Materiais
    pdf.section_title('Passo 02: Parametros dos Materiais e Solo')
    pdf.set_font('Courier', '', 9)
    pdf.multi_cell(0, 5, f"fck = {_fmt(master.get('fck'))} MPa -> fcd = {_fmt(master.get('fck', 0)/1.4 if master.get('fck') else None)} MPa\n"
                         f"Modulo de Elasticidade (E) = {_fmt(master.get('E_cs_GPa'))} GPa\n"
                         f"Coef. Poisson (v) = 0.2\n"
                         f"Mod. Reacao do Solo (kv) = {_fmt(master.get('kv'))} kN/m3")
    pdf.ln(3)

    # Passo 3: Equilibrio
    pdf.section_title('Passo 03: Carregamentos e Equilibrio Global')
    pdf.set_font('Courier', '', 9)
    total_load = master.get('total_load_kN', 0)
    w_avg = geotech.get('recalque_medio_mm', 0)
    pdf.multi_cell(0, 5, f"Somatorio de Forcas Verticais (Fz) = {_fmt(total_load)} kN\n"
                         f"Pressao Media (q_avg) = Fz / Area = {_fmt(geotech.get('pressao_media_kPa'))} kPa\n"
                         f"Recalque Medio (w_avg) = q_avg / kv = {_fmt(w_avg)} mm")
    pdf.ln(3)

    # Passo 4: Geotecnia
    pdf.section_title('Passo 04: Reacoes do Solo e Verificacao Geotecnica')
    pdf.set_font('Courier', '', 9)
    pdf.multi_cell(0, 5, f"Pressao Maxima do Modelo (q_max) = {_fmt(geotech.get('pressao_max_modelo_kPa'))} kPa\n"
                         f"Tensao Admissivel do Solo (Sigma_adm) = {_fmt(geotech.get('tensao_admissivel_kPa'))} kPa\n"
                         f"Fator de Seguranca (FS) = Sigma_adm / q_max = {_fmt(geotech.get('fs_pressao'))}\n"
                         f"Condicao: q_max <= Sigma_adm -> {'ATENDE' if geotech.get('atende_pressao_max_modelo') else 'NAO ATENDE'}")
    pdf.ln(3)

    # Passo 5: Momentos
    pdf.section_title('Passo 05: Esforcos Internos Analiticos (Momentos)')
    pdf.set_font('Courier', '', 9)
    struct = results.get('memorial', {}).get('verificacoes_estruturais', {})
    mx_max = struct.get('mx_abs_max_kNm_m', 0)
    my_max = struct.get('my_abs_max_kNm_m', 0)
    if float(mx_max or 0) == 0 and float(my_max or 0) == 0:
        pdf.multi_cell(0, 5, "Momentos Fletores Nulos (Recalque Rigido)\n"
                             "Explicacao: Para placa submetida a carga uniformemente distribuida\n"
                             "com reacao elastica de Winkler proporcional, a placa recalca como um\n"
                             "corpo rigido (curvatura nula), resultando em momentos internos zerados.")
    else:
        pdf.multi_cell(0, 5, f"Momento Maximo X (Mx) = {_fmt(mx_max)} kNm/m\n"
                             f"Momento Maximo Y (My) = {_fmt(my_max)} kNm/m\n"
                             f"Momento Majorado (Msd) = 1.40 * M_max")
    pdf.ln(3)

    # Passo 6: Flexao
    pdf.section_title('Passo 06: Dimensionamento a Flexao Critico (ELU)')
    pdf.set_font('Courier', '', 9)
    flexure = results.get('memorial', {}).get('verificacoes_estruturais', {}).get('flexao', {})
    if float(mx_max or 0) == 0 and float(my_max or 0) == 0:
        pdf.multi_cell(0, 5, f"As_min = 0.15% * h = {_fmt(flexure.get('As_min_cm2_m'))} cm2/m\n"
                             f"As_calc = 0.00 cm2/m (Momento nulo)\n"
                             f"Armadura Adotada = As_min = {_fmt(flexure.get('Asx_bottom_adot_max_cm2_m'))} cm2/m")
    else:
        pdf.multi_cell(0, 5, f"As_min = 0.15% * h = {_fmt(flexure.get('As_min_cm2_m'))} cm2/m\n"
                             f"As_calc = Msd / (0.8 * d * fyd)\n"
                             f"As_adotado = max(As_calc, As_min)\n"
                             f"As_x_inf = {_fmt(flexure.get('Asx_bottom_adot_max_cm2_m'))} cm2/m\n"
                             f"As_y_inf = {_fmt(flexure.get('Asy_bottom_adot_max_cm2_m'))} cm2/m")
    pdf.ln(3)

    # Passo 7: Puncao
    pdf.section_title('Passo 07: Verificacao de Puncao no Pilar Critico (ELU)')
    pdf.set_font('Courier', '', 9)
    punching = results.get('memorial', {}).get('verificacoes_estruturais', {}).get('puncao', {})
    if punching.get('status') == 'nao_aplicavel_sem_pilares':
        pdf.multi_cell(0, 5, "Status: Nao aplicavel (Modelo de carga uniformemente distribuida sem pilares concentrados)")
    else:
        status_atende = 'ATENDE' if punching.get('atende') else 'NAO ATENDE'
        status_text = status_atende
        if not punching.get('atende_sem_reforco') and punching.get('Asw_req_cm2', 0) > 0:
            status_text = f"{status_atende} (COM REFORCO)"
            
        pdf.multi_cell(0, 5, f"Pilar Critico: {punching.get('critical_local', 'N/D')}\n"
                             f"Tensao Solicitante (tau_sd) = {_fmt(punching.get('tau_sd_MPa', 3))} MPa\n"
                             f"Tensao Resistente (tau_rd1) = {_fmt(punching.get('tau_rd1_MPa', 3))} MPa\n"
                             f"Ratio = tau_sd / tau_rd1 = {_fmt(punching.get('ratio_max', 3))}\n"
                             f"Asw Requerido = {_fmt(punching.get('Asw_req_cm2', 0))} cm2\n"
                             f"Detalhamento: {punching.get('detalhe_reforco', 'Dispensa')}\n"
                             f"Condicao: {status_text}")
    pdf.ln(3)

    # Passo 8: ELS
    pdf.section_title('Passo 08: Estados Limites de Servico (ELS)')
    pdf.set_font('Courier', '', 9)
    service = results.get('memorial', {}).get('verificacoes_de_servico', {})
    pdf.multi_cell(0, 5, f"Recalque Maximo Absoluto (w_max) = {_fmt(service.get('w_max_mm'))} mm\n"
                         f"Recalque Diferencial (w_diff) = {_fmt(service.get('w_diff_mm'))} mm\n"
                         f"Distorcao Angular = w_diff / L\n"
                         f"Limite Normativo (w_lim) = {_fmt(service.get('w_limite_mm'))} mm")
    pdf.ln(5)

    # 9. Análise Global (Vento + Estabilidade)
    pdf.add_stability_section(results.get('stability_data') or results.get('stability'))
    pdf.add_wind_section(results.get('wind_data'))

    # 10. Resultados do Pórtico 3D (StrucPy)
    frame_results = results.get('frame_data') or results.get('frame') or results
    if isinstance(frame_results, dict) and ('design_results' in frame_results or 'design' in frame_results):
        if 'design' in frame_results and 'design_results' not in frame_results:
            frame_results['design_results'] = frame_results['design']
        pdf.add_frame_section(frame_results)

    # 11. Interação Solo-Estrutura (SSI)
    if results.get('ssi_data') or (results.get('radier') and results.get('radier').get('ssi_data')):
        ssi_data = results.get('ssi_data') or results.get('radier', {}).get('ssi_data')
        pdf.add_ssi_section(ssi_data)

    # 12. Elementos Especiais
    pdf.add_special_elements_section(results.get('special_elements'))

    # 13. Estacas
    piles_data = results.get('piles_data') or results.get('radier', {}).get('pile_results')
    if piles_data:
        pdf.add_piles_section(piles_data)
    # 14. Memorial M4 (Standardized Markdown)
    memorial = results.get('memorial', {})
    if memorial.get('standard_markdown'):
        pdf.add_markdown_content(memorial['standard_markdown'])
    elif results.get('memorial_markdown'):
        pdf.add_markdown_content(results['memorial_markdown'])

    pdf.output(str(output_path))
    return str(output_path)
