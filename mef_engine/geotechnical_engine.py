"""
geotechnical_engine.py — Motor de interpretação de sondagem SPT (NBR 6484 / 6122).
"""
from dataclasses import dataclass
from typing import List, Dict

@dataclass
class SPTLayer:
    depth_m: float
    nspt: int
    soil_type: str = "Solo Generico"

class GeotechnicalEngine:
    """Motor de analise de solo para fundacoes."""

    @staticmethod
    def estimate_sigma_adm_teixeira(nspt_avg: float) -> float:
        """
        Estimativa de sigma_adm baseada na media de N_SPT (Teixeira, 1996).
        sigma_adm (kPa) = (N_SPT / 5) * 100
        Exemplo: N=10 -> 200 kPa
        """
        sigma_adm_kgcm2 = nspt_avg / 5.0
        return round(sigma_adm_kgcm2 * 100.0, 1) # kPa

    @staticmethod
    def identify_competent_layer(spt_profile: List[SPTLayer], min_nspt: int = 8) -> SPTLayer:
        """Identifica a primeira camada competente para assentamento de sapata."""
        for layer in spt_profile:
            if layer.nspt >= min_nspt:
                return layer
        return spt_profile[-1]

    @classmethod
    def analyze_spt(cls, spt_data: List[Dict]) -> Dict:
        """Analisa um perfil de sondagem e sugere parametros de projeto."""
        profile = [SPTLayer(**d) for d in spt_data]
        
        # Media dos 3 primeiros metros (simplificado)
        competent = cls.identify_competent_layer(profile)
        nspt_design = competent.nspt
        
        sigma_adm = cls.estimate_sigma_adm_teixeira(nspt_design)
        
        return {
            "nspt_design": nspt_design,
            "sigma_adm_kPa": sigma_adm,
            "depth_m": competent.depth_m,
            "soil_type": competent.soil_type,
            "method": "Teixeira (1996)"
        }
