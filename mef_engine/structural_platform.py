from __future__ import annotations

from platform_core import ModuleDescriptor


RADIER_MODULE = ModuleDescriptor(
    module_name='radier',
    title='Modulo de Radier em Concreto Armado',
    scope='fundacoes superficiais do tipo laje sobre base elastica, com foco em resposta do solo e dimensionamento estrutural',
    current_stage='pesquisa aplicada com uso profissional orientado a dimensionamento preliminar, analise e pericia',
    professional_uses=('dimensionamento', 'analise', 'pericia', 'pesquisa'),
    future_modules=('vigas', 'pilares', 'lajes', 'nucleos', 'ligacoes'),
)

LAJE_MODULE = ModuleDescriptor(
    module_name='lajes',
    title='Modulo de Lajes Suspensas em Concreto Armado',
    scope='elementos estruturais bidimensionais (placas) sobre apoios discretos, com foco em flexao, puncao e controle de flechas (Branson)',
    current_stage='estudo preliminar e analise estrutural avancada para lajes macicas',
    professional_uses=('analise', 'dimensionamento', 'verificacao_servico'),
    future_modules=('nervuradas', 'protendidas', 'alveolares'),
)
