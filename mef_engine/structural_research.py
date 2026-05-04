from __future__ import annotations


def build_research_insights(config, memorial: dict) -> dict:
    geotech = memorial['verificacoes_geotecnicas']
    structural = memorial['verificacoes_estruturais']
    service = memorial['verificacoes_de_servico']
    mode = memorial['objetivo_profissional']['service_mode']

    current_practice = [
        'O modulo atual modela o radier como placa sobre base elastica de Winkler, adequado para estudos comparativos e rastreio inicial de comportamento.',
        'O fluxo principal ja contempla pressao de contato, flexao, puncao e indicadores de servico, preservando a logica central do memorial de calculo.',
    ]
    opportunities = []
    research_questions = [
        'Como calibrar o coeficiente de recalque com dados de instrumentacao de obras altas para reduzir incerteza de modelo?',
        'Em quais faixas de rigidez de solo o modelo de Winkler deixa de ser suficiente e passa a exigir formulacoes mais refinadas?',
        'Quais tipologias de engrossamento sob pilares centrais e de borda trazem melhor ganho de desempenho para torres altas?',
        'Como transformar os resultados do modulo em base comparativa para futuros modulos de vigas, pilares e interacao solo-estrutura global?',
    ]

    if not geotech['atende_pressao_max_modelo']:
        opportunities.append(
            'A pressao maxima no solo supera a tensao admissivel informada; investigar aumento de area, engrossamentos locais, redistribuicao de cargas ou revisao geotecnica.'
        )
    if not memorial['pre_dimensionamento']['atende_referencia_preliminar']:
        opportunities.append(
            'A espessura adotada esta abaixo da referencia preliminar; estudar ganho de rigidez global, punção e reducao de recalques diferenciais.'
        )
    if structural['puncao']['atende'] is False:
        opportunities.append(
            'A verificacao de punção nao atende; avaliar capiteis, engrossamentos, armadura de cisalhamento ou redistribuicao por vigas/faixas rigidas.'
        )
    if service and service.get('w_diff_mm', 0.0) > 5.0:
        opportunities.append(
            'O recalque diferencial estimado merece aprofundamento; comparar malhas, cenarios de kv e estrategias de rigidez local.'
        )
    if not opportunities:
        opportunities.append(
            'O caso atual esta coerente com as verificacoes principais; o proximo passo recomendado e consolidar benchmarks, casos de obra e comparacoes com software comercial.'
        )

    mode_specific = {
        'dimensionamento': [
            'Investigar tabelas de pre-dimensionamento por tipologia de torre, vao entre pilares e rigidez de solo.',
            'Evoluir a recomendacao de armadura de faixas e reforcos locais de forma mais executiva.',
        ],
        'analise': [
            'Comparar malhas, cenarios de rigidez do solo e estrategias de distribuicao de carga para medir sensibilidade do modelo.',
            'Preparar indicadores comparativos entre casos para leitura rapida do comportamento estrutural.',
        ],
        'pericia': [
            'Organizar trilha de evidencias, hipoteses e limitacoes do modelo para uso em parecer tecnico.',
            'Cruzar medições observadas com o modelo para discutir nexo entre dano, solo e resposta estrutural.',
        ],
        'pesquisa': [
            'Transformar os estudos parametricos em benchmark interno para novas solucoes de fundacao.',
            'Relacionar os achados do radier com futuros modulos de vigas, pilares e interacao solo-estrutura global.',
        ],
    }
    opportunities.extend(mode_specific.get(mode, []))

    return {
        'enquadramento': 'modulo didatico-profissional com orientacao de pesquisa aplicada em estruturas',
        'o_que_esta_sendo_feito': current_practice,
        'oportunidades_de_melhoria': opportunities,
        'questoes_de_pesquisa': research_questions,
    }
