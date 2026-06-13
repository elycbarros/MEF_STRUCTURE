import requests


def test_skyscraper_40_floors():
    url = 'http://127.0.0.1:8000/calculate_v2_unified'

    # Simulação de 40 andares
    # Lx=30, Ly=20, h=1.5, kv=30e6, q=150kPa (40 * 12kN/m2 + extras)
    payload = {
        'Lx': 30.0,
        'Ly': 20.0,
        'h': 1.5,
        'kv': 30e6,
        'q': 150.0,
        'fck': 40.0,
        'pillars': [
            {'id': 'P01', 'x': 5, 'y': 5, 'p_kN': 15000, 'bx': 0.8, 'by': 0.8},
            {'id': 'P02', 'x': 15, 'y': 5, 'p_kN': 18000, 'bx': 0.8, 'by': 0.8},
            {'id': 'P03', 'x': 25, 'y': 5, 'p_kN': 15000, 'bx': 0.8, 'by': 0.8},
            {'id': 'P04', 'x': 5, 'y': 15, 'p_kN': 15000, 'bx': 0.8, 'by': 0.8},
            {'id': 'P05', 'x': 15, 'y': 15, 'p_kN': 25000, 'bx': 1.0, 'by': 1.0},
            {'id': 'P06', 'x': 25, 'y': 15, 'p_kN': 15000, 'bx': 0.8, 'by': 0.8},
        ],
        'pillar_height': 3.0,
        'ssi_enabled': True,
    }

    print('Enviando simulação de Skyscraper (40 andares) com ISE...')
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        data = response.json()

        print('\n=== RESULTADOS DA VALIDAÇÃO FINAL ===')
        print(f'Sucesso: {data["success"]}')

        if data['success']:
            stab = data.get('stability', {})
            print(f'Gama-Z: {stab.get("gamma_z", 0):.3f}')
            print(f'Aceleração Topo: {stab.get("peak_acceleration_ms2", 0) * 100:.2f} cm/s²')
            print(f'Status Conforto: {stab.get("comfort_status")}')

            radier = data.get('radier', {})
            print(f'Radier gerado em: {radier.get("output_dir")}')

            # Verificar se o memorial existe
            if 'memorial_summary_file' in radier:
                print(f'Memorial técnico disponível: {radier["memorial_summary_file"]}')

            print('\nIntegração de EXCELÊNCIA confirmada.')
        else:
            print(f'Erro no backend: {data.get("error")}')

    except Exception as e:
        print(f'Erro na conexão com API: {e}')


if __name__ == '__main__':
    test_skyscraper_40_floors()
