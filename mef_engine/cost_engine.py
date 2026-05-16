"""
cost_engine.py - Inteligência de Custo e Otimização Econômica.
"""
from dataclasses import dataclass

@dataclass
class UnitPrices:
    concrete_m3: float = 450.0  # R$ / m3 (C30 médio)
    steel_kg: float = 8.50      # R$ / kg (CA-50)
    formwork_m2: float = 65.0   # R$ / m2 (Madeirite resinado)

class CostEngine:
    """Motor de análise de viabilidade econômica."""

    def __init__(self, prices: UnitPrices | None = None):
        self.prices = prices or UnitPrices()

    def get_concrete_price(self, fck: float) -> float:
        """Ajusta o preço do concreto baseado na classe de resistência (fck)."""
        # Estimativa: + R$ 15 por cada 5 MPa acima de 30
        base_fck = 30.0
        extra = max(0, (fck - base_fck) / 5.0) * 15.0
        return self.prices.concrete_m3 + extra

    def calculate_beam_cost(self, b: float, h: float, length: float, as_cm2: float, fck: float) -> dict:
        """Calcula o custo total de uma viga."""
        volume_m3 = b * h * length
        area_form_m2 = (b + 2 * h) * length # 3 faces
        weight_steel_kg = (as_cm2 / 1e4) * length * 7850.0 * 1.15 # 15% perdas/estribos
        
        c_price = self.get_concrete_price(fck)
        
        cost_concrete = volume_m3 * c_price
        cost_steel = weight_steel_kg * self.prices.steel_kg
        cost_form = area_form_m2 * self.prices.formwork_m2
        
        total = cost_concrete + cost_steel + cost_form
        
        return {
            'total_cost': round(total, 2),
            'breakdown': {
                'concrete': round(cost_concrete, 2),
                'steel': round(cost_steel, 2),
                'formwork': round(cost_form, 2)
            },
            'ratios': {
                'steel_per_m3': round(weight_steel_kg / volume_m3, 1),
                'cost_per_m': round(total / length, 2)
            }
        }

    def calculate_column_cost(self, b: float, h: float, length: float, as_cm2: float, fck: float) -> dict:
        """Calcula o custo total de um pilar."""
        volume_m3 = b * h * length
        area_form_m2 = 2 * (b + h) * length # 4 faces
        weight_steel_kg = (as_cm2 / 1e4) * length * 7850.0 * 1.20 # 20% transpasse/perdas
        
        c_price = self.get_concrete_price(fck)
        
        cost_concrete = volume_m3 * c_price
        cost_steel = weight_steel_kg * self.prices.steel_kg
        cost_form = area_form_m2 * self.prices.formwork_m2
        
        total = cost_concrete + cost_steel + cost_form
        
        return {
            'total_cost': round(total, 2),
            'breakdown': {
                'concrete': round(cost_concrete, 2),
                'steel': round(cost_steel, 2),
                'formwork': round(cost_form, 2)
            },
            'ratios': {
                'steel_per_m3': round(weight_steel_kg / volume_m3, 1),
                'cost_per_m': round(total / length, 2)
            }
        }

class SteelTableEngine:
    """
    Motor de geração de Tabelas de Ferro (Resumo de Aço).
    """
    # Densidades lineares (kg/m) para CA-50 e CA-60
    STEEL_DENSITY = {
        5.0: 0.154,
        6.3: 0.245,
        8.0: 0.395,
        10.0: 0.617,
        12.5: 0.963,
        16.0: 1.578,
        20.0: 2.466,
        25.0: 3.853,
        32.0: 6.313
    }

    @staticmethod
    def generate_rebar_table(detailing_data: list[dict]) -> list[dict]:
        """
        Gera uma lista de posições (N) com comprimentos e pesos.
        """
        table = []
        for i, item in enumerate(detailing_data):
            phi = item.get('phi_mm', 10.0)
            length = item.get('length_m', 0.0)
            count = item.get('count', 1)
            weight = SteelTableEngine.STEEL_DENSITY.get(phi, 0.617) * length * count
            
            table.append({
                "pos": f"N{i+1}",
                "phi_mm": phi,
                "count": count,
                "length_m": round(length, 2),
                "total_length_m": round(length * count, 2),
                "weight_kg": round(weight, 2),
                "type": "CA-60" if phi <= 6.3 else "CA-50"
            })
        return table

    @staticmethod
    def aggregate_project_steel(elements_tables: list[list[dict]]) -> dict:
        """
        Consolida o peso total por bitola para o projeto inteiro.
        """
        summary = {}
        total_ca50 = 0.0
        total_ca60 = 0.0
        
        for table in elements_tables:
            for row in table:
                phi = row['phi_mm']
                w = row['weight_kg']
                summary[phi] = summary.get(phi, 0.0) + w
                
                if row['type'] == "CA-50": total_ca50 += w
                else: total_ca60 += w
                
        return {
            "by_gauge": {f"phi_{k}": round(v, 2) for k, v in summary.items()},
            "total_ca50_kg": round(total_ca50, 2),
            "total_ca60_kg": round(total_ca60, 2),
            "grand_total_kg": round(total_ca50 + total_ca60, 2)
        }
