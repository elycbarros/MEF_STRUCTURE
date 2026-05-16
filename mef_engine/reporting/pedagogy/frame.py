
import numpy as np
from reporting.pedagogy.base import MemorialEngine

def build_frame_blackboard(result: dict, payload: dict):
    """
    Builder de Memorial Pedagógico para Pórticos Espaciais (Modo Mestre).
    Focado na explicação do Método da Rigidez Direta.
    """
    engine = MemorialEngine("Análise de Pórtico Espacial - Método da Rigidez Direta", "frame")
    
    nodes = payload.get("nodes", [])
    members = payload.get("members", [])
    
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
    
    # 2. Materiais e Propriedades (Nova Seção Elite)
    if members:
        m = members[0]
        # Tenta extrair E da seção do primeiro membro
        E = m.get("section", {}).get("E", 2.1e11) / 1e9 # GPa
        engine.add_step(
            id="frame-materials",
            title="Materiais e Parâmetros Elásticos",
            formula=r"E = \text{Módulo de Elasticidade}, \quad G = \text{Módulo de Cisalhamento}",
            substitution=rf"E = {E:.0f}\,GPa, \quad \nu = 0,20",
            result=rf"G = \frac{{E}}{{2(1+\nu)}} = {E/2.4:.1f}\,GPa",
            explanation="Os parâmetros elásticos definem a rigidez axial e de flexão do modelo linear.",
            norm="NBR 6118, Item 8.2"
        )

    # 3. Geometria e Conectividade
    engine.add_step(
        id="frame-geometry",
        title="Discretização do Modelo",
        formula=rf"N_{{nós}} = {len(nodes)}, \quad N_{{elementos}} = {len(members)}",
        substitution=rf"\text{{Geometria definida por coordenadas cartesianas X, Y, Z.}}",
        result=rf"\text{{Graus de Liberdade (DOF): }} {6 * len(nodes)}",
        explanation="O sistema global de coordenadas é utilizado para a montagem da matriz de rigidez global da estrutura.",
        norm="Geometria do Modelo"
    )
    
    # 4. Matriz de Transformação (Novo - Mestre)
    pedagogical_data = result.get("pedagogical_proofs", {})
    if "sample_t_matrix" in pedagogical_data:
        m_id = pedagogical_data.get("sample_member_id", "?")
        engine.add_step(
            id="frame-transformation",
            title=f"Transformação de Coordenadas - Barra {m_id}",
            formula=r"\mathbf{k}_{glob} = \mathbf{T}^T \mathbf{k}_{loc} \mathbf{T}",
            substitution=r"\mathbf{T} = \text{Matriz de Rotação 3D (Cossenos Diretores)}",
            result=r"\text{Matriz de Transformação 12x12 calculada.}",
            explanation="A matriz de transformação T rotaciona os esforços e deslocamentos do sistema local da barra para o sistema global da estrutura.",
            norm="Matriz de Rotação 3D"
        )

    # 5. Matriz de Rigidez Local (Amostra)
    if "sample_k_local" in pedagogical_data:
        m_id = pedagogical_data.get("sample_member_id", "?")
        l_val = pedagogical_data.get("sample_l", 1.0)
        engine.add_step(
            id="frame-k-local",
            title=f"Matriz de Rigidez Local - Barra {m_id}",
            formula=r"\mathbf{k}_{loc} = \begin{bmatrix} EA/L & \dots \\ \dots & 12EI/L^3 \end{bmatrix}",
            substitution=rf"L = {l_val:.2f}\,m",
            result=r"\text{Montagem da matriz 12x12 concluída.}",
            explanation="Cada elemento contribui para a rigidez global através de sua matriz local, que considera efeitos axiais, de flexão (biaxial) e torção.",
            norm="Método dos Elementos Finitos",
            diagramData={"kind": "frame", "title": f"Modelo de Barra {m_id}", "values": {"L": l_val}}
        )

    # 6. Equilíbrio de Nós (Auditoria)
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
