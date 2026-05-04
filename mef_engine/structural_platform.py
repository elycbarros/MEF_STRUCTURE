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
