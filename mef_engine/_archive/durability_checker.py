"""
durability_checker.py - Verificação de Durabilidade e Conformidade Normativa (NBR 6118).
"""

from dataclasses import dataclass


@dataclass
class DurabilityConfig:
    caa: int = 2  # Classe de Agressividade Ambiental (I a IV)
    trrf: int = 60  # Tempo de Resistência ao Fogo (minutos)


class DurabilityChecker:
    @staticmethod
    def get_min_cover(config: DurabilityConfig, member_type: str = 'beam') -> float:
        """
        Retorna o recobrimento nominal mínimo (mm) conforme Tabela 7.2.
        """
        # Tabela 7.2 simplificada
        covers = {
            1: {'beam': 25, 'column': 25, 'slab': 20},
            2: {'beam': 30, 'column': 30, 'slab': 25},
            3: {'beam': 40, 'column': 40, 'slab': 35},
            4: {'beam': 50, 'column': 50, 'slab': 45},
        }
        return covers.get(config.caa, covers[2]).get(member_type, 30)

    @staticmethod
    def check_fire_resistance(width: float, config: DurabilityConfig) -> bool:
        """
        Verificação simplificada de TRRF (NBR 15200).
        Largura mínima da seção para TRRF 60, 90, 120...
        """
        min_widths = {60: 120, 90: 150, 120: 200}  # mm
        required = min_widths.get(config.trrf, 120)
        return (width * 10) >= required  # width em cm -> mm


if __name__ == '__main__':
    cfg = DurabilityConfig(caa=3)  # Ambiente Marinho
    checker = DurabilityChecker()
    print(f'Recobrimento mínimo para viga (CAA III): {checker.get_min_cover(cfg, "beam")} mm')
    print(f'Atende TRRF 60min com viga de 15cm? {checker.check_fire_resistance(15, cfg)}')
