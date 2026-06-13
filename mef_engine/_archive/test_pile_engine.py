from piles_engine import PileConfig, PilesEngine, SoilLayer


def test_pile_analysis():
    engine = PilesEngine()

    layers = [
        SoilLayer(depth_m=2.0, thickness_m=2.0, nspt=5, soil_type='areia'),
        SoilLayer(depth_m=10.0, thickness_m=8.0, nspt=15, soil_type='argila'),
        SoilLayer(depth_m=12.0, thickness_m=2.0, nspt=30, soil_type='areia'),
    ]

    config = PileConfig(type='bored', diameter_m=0.40, length_m=12.0, fck=30.0, layers=layers)

    results = engine.run_full_analysis(config, applied_load_kN=500.0)

    print('\n--- Resultados de Análise de Estaca ---')
    print(f'Tipo: {results["config"]["type"]}')
    print(f'Capacidade Geotécnica (Adm): {results["geotechnical"]["q_adm_final_kN"]} kN')
    print(f'Capacidade Estrutural (Concreto): {results["structural"]["nr_concrete_kN"]} kN')
    print(f'Carga Aplicada: {results["structural"]["nd_kN"]} kN')
    print(f'Status Geral: {results["overall_status"]}')

    # Detalhes Aoki-Velloso
    av = results['geotechnical']['aoki_velloso']
    print(f'\nAoki-Velloso: Rp={av["rp_kN"]} kN, Rs={av["rs_kN"]} kN, Qadm={av["q_adm_kN"]} kN')

    # Detalhes Decourt-Quaresma
    dq = results['geotechnical']['decourt_quaresma']
    print(f'Decourt-Quaresma: Rp={dq["rp_kN"]} kN, Rs={dq["rs_kN"]} kN, Qadm={dq["q_adm_kN"]} kN')


if __name__ == '__main__':
    test_pile_analysis()
