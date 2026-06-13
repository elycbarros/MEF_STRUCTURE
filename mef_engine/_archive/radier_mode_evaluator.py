from __future__ import annotations


def build_mode_specific_assessment(memorial: dict) -> dict:
    mode = memorial['objetivo_profissional']['service_mode']
    geotech = memorial['verificacoes_geotecnicas']
    predim = memorial['pre_dimensionamento']
    structural = memorial['verificacoes_estruturais']
    service = memorial['verificacoes_de_servico']

    if mode == 'dimensionamento':
        combos = memorial['base_normativa']['combinacoes_adotadas']
        return {
            'combination_basis': {
                'service_combination': combos['service_rare'],
                'ultimate_combination': combos['ultimate'],
            },
            'design_checks': {
                'pre_dimensioning_ok': predim['atende_referencia_preliminar'],
                'flexure_governing_Asx_top_cm2_m': structural['flexao'].get('Asx_top_adot_max_cm2_m'),
                'flexure_governing_Asx_bottom_cm2_m': structural['flexao'].get('Asx_bottom_adot_max_cm2_m'),
                'flexure_governing_Asy_top_cm2_m': structural['flexao'].get('Asy_top_adot_max_cm2_m'),
                'flexure_governing_Asy_bottom_cm2_m': structural['flexao'].get('Asy_bottom_adot_max_cm2_m'),
                'punching_ok': structural['puncao']['atende'],
                'punching_critical_local': structural['puncao']['critical_local'],
            },
            'executive_recommendations': [
                'Definir faixas de armadura superior sobre pilares e bordas.',
                'Confirmar espessura final com base em punção, flexão e construtibilidade.',
                'Registrar detalhamento preliminar de reforços locais e malhas mínima/inferior/superior.',
            ],
        }

    if mode == 'analise':
        return {
            'response_interpretation': {
                'average_contact_pressure_kPa': geotech['pressao_media_kPa'],
                'max_contact_pressure_kPa': geotech['pressao_max_modelo_kPa'],
                'max_settlement_mm': service.get('w_max_mm'),
                'differential_settlement_mm': service.get('w_diff_mm'),
                'wk_x_max_mm': service.get('wk_x_max_mm'),
                'wk_y_max_mm': service.get('wk_y_max_mm'),
            },
            'sensitivity_tracks': [
                'Variar kv e espessura para medir rigidez global e redistribuição de pressão.',
                'Comparar refinamentos de malha para estabilização de momentos e recalques.',
                'Confrontar comportamento da fundação com hipóteses de rigidez da superestrutura.',
            ],
            'analysis_recommendations': [
                'Gerar envelopes comparativos entre cenários-base, solo mais rígido e solo mais deformável.',
                'Registrar indicadores comparativos de recalque, pressão e momento para tomada de decisão.',
            ],
        }

    if mode == 'pericia':
        return {
            'evidence_chain': {
                'input_traceability': 'geometria, cargas, solo e parâmetros do modelo devem ser congelados por versão do estudo',
                'model_limitations': 'modelo de placa sobre Winkler adequado para leitura inicial, sujeito a refinamentos conforme evidências e instrumentação',
                'consistency_flags': {
                    'soil_pressure_ok': geotech['atende_pressao_max_modelo'],
                    'global_equilibrium_ok': structural['equilibrio_global']['atende'],
                    'service_compatibility': service.get('w_diff_mm'),
                    'cracking_check_x_ok': service.get('wk_x_ok'),
                    'cracking_check_y_ok': service.get('wk_y_ok'),
                },
            },
            'forensic_hypotheses': [
                'Compatibilidade entre tensão no solo e manifestações patológicas observadas.',
                'Influência de rigidez insuficiente do radier em concentrações locais sob pilares.',
                'Necessidade de confrontar modelo com laudos geotécnicos, monitoramento e histórico executivo.',
            ],
            'forensic_recommendations': [
                'Amarrar o parecer a dados de entrada verificáveis e cronologia executiva.',
                'Comparar comportamento calculado com fissuras, desaprumos, recalques e leituras instrumentadas.',
            ],
        }

    return {
        'benchmark_targets': {
            'core_metrics': [
                'pressao de contato',
                'recalque diferencial',
                'momentos maximos',
                'armadura adotada',
                'punção',
            ],
            'comparison_bases': [
                'cenários paramétricos internos',
                'software comercial',
                'casos instrumentados de obra',
            ],
        },
        'research_vectors': [
            'Evoluir de Winkler para representações mais refinadas quando necessário.',
            'Investigar engrossamentos locais e tipologias de fundação para torres altas.',
            'Transformar o módulo em benchmark de fundações dentro da plataforma estrutural.',
        ],
        'research_recommendations': [
            'Criar base de casos calibrados para confronto entre obras e novas soluções.',
            'Formalizar métricas de comparação para futuros módulos de vigas, pilares e núcleo.',
        ],
    }
