"""
bim_engine.py - Módulo de Interoperabilidade BIM e Integração TQS/Revit.
Exporta dados estruturais para coordenação 3D e importa cargas de superestrutura.
"""
import json
import pandas as pd
from pathlib import Path

class BIMCoordinator:
    def __init__(self, output_dir: str):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def export_structural_manifest(self, config: any, results: dict):
        """
        Gera um manifesto BIM (JSON/CSV) com a geometria e materiais para importação no Revit/Archicad.
        """
        manifest = {
            "project_info": {
                "name": config.base_name,
                "module": config.module_name,
                "standards": config.code_profile
            },
            "geometry": {
                "type": "IfcSlab" if config.module_name == 'radier' else "IfcFloor",
                "Lx_m": config.Lx,
                "Ly_m": config.Ly,
                "thickness_m": config.h,
                "material": "Concrete_C" + str(config.fck)
            },
            "reinforcement_summary": results.get('reinforcement_metrics', {}),
            "coordination_points": [
                {"id": "ORIGIN", "x": 0, "y": 0, "z": 0},
                {"id": "END", "x": config.Lx, "y": config.Ly, "z": 0}
            ]
        }
        
        path = self.output_dir / f"{config.base_name}_bim_manifest.json"
        with open(path, 'w') as f:
            json.dump(manifest, f, indent=4)
        print(f"✅ Manifesto BIM exportado: {path}")
        return str(path)

class TQSIntegration:
    @staticmethod
    def import_loads_from_csv(csv_path: str):
        """
        Importa cargas de pilares formatadas pelo TQS ou Revit.
        Formato esperado: id, x, y, p_kN, mx_kNm, my_kNm, bx_m, by_m
        """
        try:
            df = pd.read_csv(csv_path)
            # Normalização de nomes de colunas
            mapping = {
                'P(kN)': 'p', 'Mdx(kNm)': 'mx', 'Mdy(kNm)': 'my',
                'X(m)': 'x', 'Y(m)': 'y', 'B(m)': 'bx', 'H(m)': 'by'
            }
            df = df.rename(columns=mapping)
            print(f"✅ {len(df)} cargas importadas com sucesso via TQS/BIM CSV.")
            return df
        except Exception as e:
            print(f"❌ Erro ao importar cargas BIM: {e}")
            return None

def generate_bim_ready_report(config, results, output_dir):
    coord = BIMCoordinator(output_dir)
    return coord.export_structural_manifest(config, results)
