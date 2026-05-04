"""
radier_detailing.py - Motor de Detalhamento Estrutural Comercial.
Converte áreas de aço (cm2/m) em bitolas e espaçamentos reais.
"""
import math

class DetailingEngine:
    # Bitolas comerciais disponíveis no Brasil (mm)
    COMMERCIAL_BARS = [6.3, 8.0, 10.0, 12.5, 16.0, 20.0, 25.0, 32.0]
    
    @staticmethod
    def get_bar_area(diameter_mm: float) -> float:
        """Retorna a área da seção transversal da barra em cm2."""
        return (math.pi * (diameter_mm / 10)**2) / 4

    @staticmethod
    def suggest_reinforcement(as_required_cm2_m: float, preferred_diameter: float = 12.5) -> dict:
        """
        Sugere bitola e espaçamento para cobrir a área de aço necessária.
        as_required_cm2_m: Área de aço calculada (cm2 por metro)
        """
        if as_required_cm2_m <= 0:
            return {"diameter": 0, "spacing": 0, "as_provided": 0, "text": "Sem armadura"}
            
        # Tenta a bitola preferida primeiro
        as_bar = DetailingEngine.get_bar_area(preferred_diameter)
        n_bars = as_required_cm2_m / as_bar
        spacing = 100.0 / n_bars # em cm
        
        # Arredonda o espaçamento para baixo (múltiplo de 2.5cm ou 5cm por praticidade)
        spacing = math.floor(spacing / 2.5) * 2.5
        
        # Limites práticos (máximo 20cm, mínimo 7.5cm)
        if spacing > 20: spacing = 20.0
        if spacing < 7.5:
            # Se o espaçamento for muito pequeno, tenta a próxima bitola
            idx = DetailingEngine.COMMERCIAL_BARS.index(preferred_diameter)
            if idx < len(DetailingEngine.COMMERCIAL_BARS) - 1:
                return DetailingEngine.suggest_reinforcement(as_required_cm2_m, DetailingEngine.COMMERCIAL_BARS[idx+1])
        
        as_provided = (100.0 / spacing) * as_bar
        
        return {
            "diameter": preferred_diameter,
            "spacing": spacing,
            "as_provided": as_provided,
            "text": f"phi {preferred_diameter} c/ {spacing:.1f} cm"
        }

    @staticmethod
    def detail_mesh(as_x_inf: float, as_y_inf: float, as_x_sup: float, as_y_sup: float) -> dict:
        """Gera o detalhamento completo para as 4 faces/direções."""
        return {
            "bottom_x": DetailingEngine.suggest_reinforcement(as_x_inf, 12.5),
            "bottom_y": DetailingEngine.suggest_reinforcement(as_y_inf, 12.5),
            "top_x": DetailingEngine.suggest_reinforcement(as_x_sup, 10.0),
            "top_y": DetailingEngine.suggest_reinforcement(as_y_sup, 10.0)
        }
