"""
load_takedown.py — Motor de Acúmulo de Cargas (Takedown) para Edifícios Altos.
Calcula a carga acumulada nos pilares da cobertura até a fundação.
"""

import pandas as pd


class LoadTakedownEngine:
    @staticmethod
    def run_vertical_takedown(
        n_floors: int, area_influence_m2: float, q_dead_kPa: float = 5.0, q_live_kPa: float = 2.0
    ) -> pd.DataFrame:
        """
        Calcula a carga vertical acumulada por pavimento.
        Inclui redução de carga acidental conforme NBR 6120.
        """
        floors = []
        acc_dead = 0.0
        acc_live = 0.0

        for i in range(n_floors, 0, -1):
            # Carga do pavimento atual
            floor_dead = q_dead_kPa * area_influence_m2
            floor_live = q_live_kPa * area_influence_m2

            # Fator de redução de sobrecarga (simplificado NBR 6120)
            # Redução de até 40% para muitos pavimentos
            reduction_factor = 1.0
            if (n_floors - i) > 3:
                reduction_factor = 0.8
            if (n_floors - i) > 6:
                reduction_factor = 0.6

            acc_dead += floor_dead
            acc_live += floor_live * reduction_factor

            total_service = acc_dead + acc_live
            total_design = acc_dead * 1.4 + acc_live * 1.4  # Simplificado gamma

            floors.append(
                {
                    'floor': i,
                    'dead_kN': round(acc_dead, 1),
                    'live_kN': round(acc_live, 1),
                    'total_service_kN': round(total_service, 1),
                    'total_design_kN': round(total_design, 1),
                    'stress_MPa': round((total_design / 1000.0) / (0.6 * 0.6), 2),  # Exemplo pilar 60x60
                }
            )

        return pd.DataFrame(floors)


if __name__ == '__main__':
    # Teste para prédio de 40 andares
    engine = LoadTakedownEngine()
    df = engine.run_vertical_takedown(n_floors=40, area_influence_m2=25.0)
    print('=== ACÚMULO DE CARGAS (PILAR TIPO - 40 ANDARES) ===')
    print(df.tail(10))  # Base do prédio
