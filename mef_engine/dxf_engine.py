"""
dxf_engine.py - Gerador de Desenhos Técnicos (DXF) para Radiers.
Cria arquivos CAD profissionais com armaduras e geometrias.
"""
import ezdxf
from pathlib import Path
import numpy as np

class RadierDXFEngine:
    def __init__(self, filename: str, Lx: float, Ly: float):
        self.doc = ezdxf.new('R2010')
        self.msp = self.doc.modelspace()
        self.Lx = Lx
        self.Ly = Ly
        self.filename = filename
        self._setup_layers()

    def _setup_layers(self):
        self.doc.layers.add('GEOMETRIA', color=7) # Branco
        self.doc.layers.add('ARM_INF', color=1)   # Vermelho
        self.doc.layers.add('ARM_SUP', color=4)   # Ciano
        self.doc.layers.add('TEXTO', color=2)     # Amarelo
        self.doc.layers.add('PILOTIS', color=3)   # Verde
        self.doc.layers.add('ARM_PUNCAO', color=6) # Magenta

    def draw_outline(self):
        # Contorno do radier
        p = [(0,0), (self.Lx, 0), (self.Lx, self.Ly), (0, self.Ly), (0,0)]
        self.msp.add_lwpolyline(p, dxfattribs={'layer': 'GEOMETRIA'})

    def draw_mesh(self, layer: str, spacing_m: float, label: str):
        """Desenha uma malha de armadura simplificada."""
        # Barras em X
        y_steps = np.arange(0, self.Ly + spacing_m, spacing_m)
        for y in y_steps:
            if y > self.Ly: y = self.Ly
            self.msp.add_line((0, y), (self.Lx, y), dxfattribs={'layer': layer})
        
        # Barras em Y
        x_steps = np.arange(0, self.Lx + spacing_m, spacing_m)
        for x in x_steps:
            if x > self.Lx: x = self.Lx
            self.msp.add_line((x, 0), (x, self.Ly), dxfattribs={'layer': layer})
            
        # Adiciona rótulo no centro
        self.msp.add_text(label, dxfattribs={'layer': 'TEXTO', 'height': 0.25}).set_placement((self.Lx/2, self.Ly/2))

    def draw_columns(self, column_loads: np.ndarray):
        """Desenha os pilares."""
        for col in column_loads:
            x, y = col[0], col[1]
            # Desenha um retângulo de 60x60 (padrão)
            p = [
                (x-0.3, y-0.3), (x+0.3, y-0.3), 
                (x+0.3, y+0.3), (x-0.3, y+0.3), (x-0.3, y-0.3)
            ]
            self.msp.add_lwpolyline(p, dxfattribs={'layer': 'PILOTIS'})
            self.msp.add_text(f"P", dxfattribs={'layer': 'TEXTO', 'height': 0.15}).set_placement((x+0.4, y+0.4))

    def draw_punching_reinforcement(self, punching_results: list[dict], d_m: float):
        """
        Desenha zonas de reforço de punção (estribos/studs) ao redor de pilares críticos.
        punching_results: Lista de dicionários com 'x', 'y', 'bx', 'by' e 'status'.
        """
        for res in punching_results:
            if res.get('status') == 'REFORÇO':
                x, y = res['x'], res['y']
                bx, by = res['bx'], res['by']
                # Desenha o perímetro crítico de reforço (2d de distância)
                offset = 2.0 * d_m
                p = [
                    (x - bx/2 - offset, y - by/2 - offset),
                    (x + bx/2 + offset, y - by/2 - offset),
                    (x + bx/2 + offset, y + by/2 + offset),
                    (x - bx/2 - offset, y + by/2 + offset),
                    (x - bx/2 - offset, y - by/2 - offset)
                ]
                self.msp.add_lwpolyline(p, dxfattribs={'layer': 'ARM_PUNCAO', 'linetype': 'DASHED'})
                self.msp.add_text("REFORÇO PUNÇÃO", dxfattribs={'layer': 'TEXTO', 'height': 0.10}).set_placement((x - bx/2 - offset, y + by/2 + offset + 0.1))

    def draw_title_block(self, project_name: str, client: str, author: str):
        """Desenha um carimbo profissional no canto inferior direito."""
        # Dimensões do carimbo em metros (escala 1:50) -> 175mm x 50mm reais
        # 175mm / 1000 * 50 = 8.75m no desenho
        # 50mm / 1000 * 50 = 2.5m no desenho
        w, h = 8.75, 3.5
        x0, y0 = self.Lx + 1, 0
        
        # Moldura do carimbo
        self.msp.add_lwpolyline([(x0, y0), (x0+w, y0), (x0+w, y0+h), (x0, y0+h), (x0, y0)], dxfattribs={'layer': 'GEOMETRIA', 'color': 7})
        
        # Divisórias
        self.msp.add_line((x0, y0+h*0.7), (x0+w, y0+h*0.7), dxfattribs={'layer': 'GEOMETRIA'})
        self.msp.add_line((x0, y0+h*0.4), (x0+w, y0+h*0.4), dxfattribs={'layer': 'GEOMETRIA'})
        
        # Textos
        self.msp.add_text("PROJETO ESTRUTURAL", dxfattribs={'layer': 'TEXTO', 'height': 0.25}).set_placement((x0+0.2, y0+h-0.4))
        self.msp.add_text(project_name.upper(), dxfattribs={'layer': 'TEXTO', 'height': 0.4}).set_placement((x0+0.2, y0+h-0.9))
        
        self.msp.add_text(f"CLIENTE: {client}", dxfattribs={'layer': 'TEXTO', 'height': 0.2}).set_placement((x0+0.2, y0+h-1.6))
        self.msp.add_text(f"RESPONSÁVEL: {author}", dxfattribs={'layer': 'TEXTO', 'height': 0.2}).set_placement((x0+0.2, y0+h-2.1))
        
        self.msp.add_text("ESCALA: 1:50  |  DATA: 2026", dxfattribs={'layer': 'TEXTO', 'height': 0.15}).set_placement((x0+0.2, y0+0.3))
        self.msp.add_text("MEF STRUCTURAL - V5 PLENO", dxfattribs={'layer': 'TEXTO', 'height': 0.15, 'color': 1}).set_placement((x0+w-3.5, y0+0.3))

    def draw_bar_list(self, steel_data: list[dict]):
        """
        Gera uma TABELA DE AÇO (Listagem de Aço).
        steel_data: [{'phi': 12.5, 'n': 20, 'len': 12.4, 'weight': 150.5}, ...]
        """
        x0, y0 = self.Lx + 1, 5
        self.msp.add_text("TABELA DE AÇO (RESUMO)", dxfattribs={'layer': 'TEXTO', 'height': 0.35}).set_placement((x0, y0 + 4.5))
        
        headers = ["BITOLA", "QTD", "COMP(m)", "PESO(kg)"]
        col_w = [1.5, 1.0, 2.0, 2.0]
        
        # Cabeçalho
        for i, h in enumerate(headers):
            x_pos = x0 + sum(col_w[:i])
            self.msp.add_text(h, dxfattribs={'layer': 'TEXTO', 'height': 0.18}).set_placement((x_pos, y0 + 3.8))
        
        self.msp.add_line((x0, y0+3.6), (x0+sum(col_w), y0+3.6), dxfattribs={'layer': 'GEOMETRIA'})

        total_weight = 0
        for idx, item in enumerate(steel_data):
            y = y0 + 3.0 - idx*0.5
            phi = item.get('phi', 0)
            qtd = item.get('n', 0)
            length = item.get('len', 0)
            weight = item.get('weight', 0)
            total_weight += weight
            
            self.msp.add_text(f"%%c{phi}", dxfattribs={'layer': 'TEXTO', 'height': 0.18}).set_placement((x0, y))
            self.msp.add_text(f"{qtd}", dxfattribs={'layer': 'TEXTO', 'height': 0.18}).set_placement((x0 + col_w[0], y))
            self.msp.add_text(f"{length:.2f}", dxfattribs={'layer': 'TEXTO', 'height': 0.18}).set_placement((x0 + col_w[0] + col_w[1], y))
            self.msp.add_text(f"{weight:.2f}", dxfattribs={'layer': 'TEXTO', 'height': 0.18}).set_placement((x0 + col_w[0] + col_w[1] + col_w[2], y))

        self.msp.add_line((x0, y0-0.2), (x0+sum(col_w), y0-0.2), dxfattribs={'layer': 'GEOMETRIA'})
        self.msp.add_text(f"PESO TOTAL: {total_weight:.2f} kg", dxfattribs={'layer': 'TEXTO', 'height': 0.25}).set_placement((x0, y0 - 0.7))

    def draw_dimensions(self):
        """Adiciona cotas principais."""
        # Cota X
        self.msp.add_aligned_dim(p1=(0, -0.5), p2=(self.Lx, -0.5), distance=0.5, dxfattribs={'layer': 'TEXTO'})
        # Cota Y
        self.msp.add_aligned_dim(p1=(-0.5, 0), p2=(-0.5, self.Ly), distance=0.5, dxfattribs={'layer': 'TEXTO'})

    def save(self):
        self.doc.saveas(self.filename)
        print(f"✅ DXF Executivo salvo: {self.filename}")

class SpecialElementsDXFEngine:
    """Gerador de Desenhos Técnicos para Elementos Especiais."""
    def __init__(self, filename: str):
        self.doc = ezdxf.new('R2010')
        self.msp = self.doc.modelspace()
        self.filename = filename
        self._setup_layers()

    def _setup_layers(self):
        self.doc.layers.add('GEOMETRIA', color=7)
        self.doc.layers.add('ARMADURA', color=1)
        self.doc.layers.add('TEXTO', color=2)

    def draw_retaining_wall(self, h_wall: float, b_base: float, thick_wall: float):
        """Desenha corte transversal de muro de arrimo."""
        # Geometria do Muro (Corte)
        p = [
            (0, 0), (b_base, 0), (b_base, 0.4), # Base
            (thick_wall + 0.2, 0.4), (thick_wall, h_wall), # Parede
            (0, h_wall), (0, 0)
        ]
        self.msp.add_lwpolyline(p, dxfattribs={'layer': 'GEOMETRIA'})
        self.msp.add_text("CORTE MURO DE ARRIMO", dxfattribs={'layer': 'TEXTO', 'height': 0.2}).set_placement((0, h_wall + 0.5))

    def draw_stair_section(self, l_horiz: float, h_vert: float, steps: int):
        """Desenha corte de escada."""
        x, y = 0, 0
        dh = l_horiz / steps
        dv = h_vert / steps
        points = [(0, 0)]
        for _ in range(steps):
            points.append((x, y + dv))
            points.append((x + dh, y + dv))
            x += dh
            y += dv
        # Fundo da laje
        points.append((x, y - 0.15))
        points.append((0, -0.15))
        points.append((0, 0))
        
        self.msp.add_lwpolyline(points, dxfattribs={'layer': 'GEOMETRIA'})
        self.msp.add_text("DETALHE ESCADA", dxfattribs={'layer': 'TEXTO', 'height': 0.2}).set_placement((0, h_vert + 0.5))

    def save(self):
        self.doc.saveas(self.filename)
        print(f"✅ DXF Especial salvo: {self.filename}")

if __name__ == "__main__":
    # Teste Radier
    engine = RadierDXFEngine("output/test_detailing.dxf", 24, 24)
    engine.draw_outline()
    engine.draw_mesh('ARM_INF', 0.15, "phi 12.5 c/ 15 INF")
    engine.save()
    
    # Teste Especiais
    spec_engine = SpecialElementsDXFEngine("output/test_especiais.dxf")
    spec_engine.draw_retaining_wall(4.0, 2.5, 0.25)
    spec_engine.draw_stair_section(4.0, 3.0, 16)
    spec_engine.save()
