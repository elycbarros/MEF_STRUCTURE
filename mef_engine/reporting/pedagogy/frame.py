
import numpy as np
from reporting.pedagogy.base import MemorialEngine

def build_frame_blackboard(result: dict, payload: dict):
    """
    Builder de Memorial Pedagógico para Pórticos Espaciais (Modo Mestre).
    Focado na explicação do Método da Rigidez Direta.
    """
    engine = MemorialEngine("Análise de Pórtico Espacial - Método da Rigidez Direta", "frame")
    
    # 1. Introdução Teórica
    engine.add_step(
        id="frame-intro",
        title="Fundamentos da Análise Matricial",
        formula=r"\mathbf{K} \cdot \mathbf{U} = \mathbf{F}",
        substitution=r"\text{Método dos Deslocamentos (Rigidez Direta)}",
        result=r"\text{Análise de 1ª Ordem Linear}",
        explanation="A análise utiliza elementos de barra 3D com 12 graus de liberdade por elemento (3 translações e 3 rotações em cada extremidade).",
        norm="NBR 6118 / Mecânica das Estruturas"
    )
    
    # 2. Geometria e Conectividade
    nodes = payload.get("nodes", [])
    members = payload.get("members", [])
    engine.add_step(
        id="frame-geometry",
        title="Discretização do Modelo",
        formula=rf"N_{{nós}} = {len(nodes)}, \quad N_{{elementos}} = {len(members)}",
        substitution=rf"\text{{Geometria definida por coordenadas cartesianas X, Y, Z.}}",
        result=rf"\text{{Graus de Liberdade (DOF): }} {6 * len(nodes)}",
        explanation="O sistema global de coordenadas é utilizado para a montagem da matriz de rigidez global da estrutura.",
        norm="Geometria do Modelo"
    )
    
    # 3. Matriz de Rigidez Local (Amostra)
    pedagogical_data = result.get("pedagogical_proofs", {})
    if "sample_k_local" in pedagogical_data:
        m_id = pedagogical_data.get("sample_member_id", "?")
        engine.add_step(
            id="frame-k-local",
            title=f"Matriz de Rigidez Local - Barra {m_id}",
            formula=r"\mathbf{k}_{loc} = \begin{bmatrix} EA/L & \dots \\ \dots & 12EI/L^3 \end{bmatrix}",
            substitution=r"\text{Matriz de Rigidez Local 12x12}",
            result=r"\text{Montagem concluída com sucesso.}",
            explanation="Cada elemento contribui para a rigidez global através de sua matriz local, que considera efeitos axiais, de flexão (biaxial) e torção.",
            norm="Método dos Elementos Finitos",
            diagramData={"kind": "frame", "title": f"Modelo de Barra {m_id}", "values": {"L": 1.0}}
        )

    # 4. Equilíbrio de Nós (Auditoria)
    equilibrium = result.get("equilibrium_audit", {})
    if equilibrium:
        err_vec = equilibrium.get("equilibrium_error_kN_m", [0,0,0,0,0,0])
        max_err_f = max(abs(x) for x in err_vec[0:3])
        max_err_m = max(abs(x) for x in err_vec[3:6])
        
        status = "APROVADO" if equilibrium.get("is_equilibrated") else "REVISÃO"
        
        engine.add_step(
            id="frame-equilibrium",
            title="Auditoria de Equilíbrio Global",
            formula=r"\sum \mathbf{F}_{ext} + \sum \mathbf{R} \approx 0",
            substitution=rf"\text{{Erro Máx Força: }} {max_err_f:.6f}\,kN, \quad \text{{Erro Máx Momento: }} {max_err_m:.6f}\,kNm",
            result=rf"\text{{Status de Convergência: {status}}}",
            explanation="A verificação de resíduos garante que a solução numérica encontrada respeita as leis da estática para toda a estrutura.",
            norm="NBR 6118, Item 11.2"
        )

    return engine.build()
