
import numpy as np
from reporting.pedagogy.base import MemorialEngine

def build_frame_blackboard(result: dict, payload: dict):
    """
    Builder de Memorial Pedagógico para Pórticos e Treliças (Modo Mestre).
    Focado na explicação do Método da Rigidez Direta e formulação de elementos finitos.
    """
    is_truss = payload.get("is_truss", False)
    
    if is_truss:
        engine = MemorialEngine("Análise de Treliça Plana - Método dos Elementos Finitos", "frame")
        
        nodes = payload.get("nodes", [])
        members = payload.get("members", [])
        
        # 1. Introdução Teórica Treliças
        engine.add_step(
            id="truss-intro",
            title="Fundamentos de Treliças Rótuladas",
            formula=r"\mathbf{k}_{loc} = \frac{EA}{L}",
            substitution=r"\text{Elementos articulados com rigidez axial pura}",
            result=r"\text{Graus de Liberdade Rotacionais Desativados}",
            explanation="Os elementos de treliça transmitem exclusivamente forças axiais (tração e compressão). Como não há rigidez rotacional à flexão, todos os nós atuam como articulações perfeitas (rótulas).",
            norm="NBR 6118 / Teoria das Estruturas"
        )
        
        # 2. Graus de Liberdade e Estabilidade
        engine.add_step(
            id="truss-dof",
            title="Graus de Liberdade e Bloqueio Automático",
            formula=r"DOF_{ativo} = 2 \times N_{nós}",
            substitution=rf"N_{{nós}} = {len(nodes)} \implies DOF_{{teoricos}} = {2 * len(nodes)}",
            result=r"\text{Rotações } R_x, R_y, R_z \text{ e Translação } Y \text{ travadas}",
            explanation="Para evitar singularidades de rigidez rotacional sem a necessidade de rotulação individual, o solver Mestre trava automaticamente os graus de liberdade rotacionais e fora do plano em todos os nós do sistema.",
            norm="Condição de Não-Singularidade MEF"
        )
        
        # 3. Matriz de Rigidez Local do Elemento de Treliça 2D
        if members:
            m = members[0]
            E = m.get("section", {}).get("E", 2.5e10) / 1e9 # GPa
            engine.add_step(
                id="truss-k-local",
                title="Matriz de Rigidez do Elemento em Coordenadas Globais",
                formula=r"\mathbf{k}_{glob} = \frac{EA}{L} \begin{bmatrix} c^2 & cs & -c^2 & -cs \\ cs & s^2 & -cs & -s^2 \\ -c^2 & -cs & c^2 & cs \\ -cs & -s^2 & cs & s^2 \end{bmatrix}",
                substitution=rf"E = {E:.0f}\,GPa, \quad c = \cos\theta, \quad s = \sin\theta",
                result=r"\text{Montagem 4x4 por barra para graus de liberdade translacionais}",
                explanation="A matriz de rigidez global de cada membro projeta a rigidez axial pura nos eixos coordenados globais X e Z com base nos cossenos diretores c e s.",
                norm="Método dos Deslocamentos Direto"
            )
            
        # 4. Solução do Sistema Global de Deslocamentos
        engine.add_step(
            id="truss-solution",
            title="Montagem e Solução do Sistema Linear",
            formula=r"\mathbf{U}_{livres} = \mathbf{K}_{L}^{-1} \cdot \mathbf{F}_{L}",
            substitution=r"\text{Condições de Contorno e Restrições aplicadas à matriz global}",
            result=r"\mathbf{U} = \text{Vetor de Deslocamentos Nodais Calculado}",
            explanation="A matriz de rigidez global K é particionada nos graus de liberdade livres e restritos. O sistema é resolvido para determinar os deslocamentos reais de cada nó sob a ação das cargas externas.",
            norm="Análise Matricial Linear"
        )
        
        # 5. Auditoria de Equilíbrio de Nós (Gabarito Exato)
        equilibrium = result.get("equilibrium_audit", {})
        if equilibrium:
            err_vec = equilibrium.get("equilibrium_error_kN_m", [0,0,0,0,0,0])
            max_err_f = max(abs(x) for x in err_vec[0:3])
            
            status = "APROVADO" if equilibrium.get("is_equilibrated") else "REVISÃO"
            
            engine.add_step(
                id="truss-equilibrium",
                title="Auditoria de Equilíbrio Estático e Reações",
                formula=r"\sum \mathbf{F}_{externas} + \sum \mathbf{R}_{apoios} = \mathbf{0}",
                substitution=rf"\text{{Erro de Equilíbrio Nodal: }} {max_err_f:.8e}\,kN",
                result=rf"\text{{Equilíbrio Estático: {status}}}",
                explanation="A auditoria de esforços calcula os resíduos de forças nos nós livres, garantindo precisão infinitesimal. As reações de apoio nas restrições são avaliadas diretamente a partir das forças nodais internas acumuladas.",
                norm="Mecânica dos Sólidos Rígidos"
            )
            
        return engine.build()
        
    else:
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
        
        # 2. Materiais e Propriedades
        if members:
            m = members[0]
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
        
        # 4. Matriz de Transformação
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
    
        # 5. Matriz de Rigidez Local
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
    
        # 6. Equilíbrio de Nós
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
