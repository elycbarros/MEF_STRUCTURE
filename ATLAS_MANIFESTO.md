# Atlas: O Motor Estrutural que Une a Ciência do MEF com a Velocidade do Rust

> **"O Atlas não esconde suas equações. Ele as acelera."**

O Atlas é uma plataforma de análise estrutural de próxima geração, desenvolvida para equilibrar **rigor científico, performance industrial e transparência total**. O projeto nasceu da constatação de que os softwares comerciais são, em sua maioria, caixas-pretas lentas para inovação, enquanto as ferramentas acadêmicas falham em escalar para problemas reais.

Decidimos construir algo diferente: um **motor híbrido Python + Rust** que orquestra análise de elementos finitos (MEF) com paralelismo massivo, aderência estrita às normas brasileiras (**NBR 6118 / NBR 6123**) e uma arquitetura pronta para o futuro.

---

## ⚙️ O que o Atlas faz (e faz com maestria)

### 1. Núcleo Matemático de Alta Performance
- **Pórtico Espacial 3D**: Análise linear e P-Delta iterativo com aceleração de Aitken para convergência ultrarrápida.
- **Montagem Paralela em Rust**: Utiliza a biblioteca `rayon` para montagem de matrizes de rigidez global, atingindo speedups superiores a 5×.
- **Solver Esparso Nativo (`faer`)**: Implementação 100% Rust do solver esparso, permitindo resolver sistemas massivos com uso mínimo de memória e tempo recorde.

### 2. Rigor Normativo e Pedagógico
- **Verificações NBR 6118**: ELU, ELS (flechas e fissuração) e durabilidade por classe de agressividade ambiental.
- **Transparência e Auditabilidade**: Cada solução gera snapshots completos em JSON e relatórios em Markdown com o passo-a-passo normativo.
- **Paridade Científica**: Validação com paridade numérica de **1e-15** em relação aos métodos analíticos tradicionais.

### 3. Inteligência Híbrida
- **Surrogate Models (ML)**: Modelos treinados para prever comportamentos complexos (como recalques em radier) em milissegundos, ideais para fases de pré-dimensionamento.

---

## 📊 Performance que Muda o Jogo

Em nossos benchmarks de estresse, o Atlas demonstrou uma escalabilidade sem precedentes para motores open-source:

| Complexidade | Nós | Membros | DOFs | **Tempo de Solução (Rust)** |
| :--- | :--- | :--- | :--- | :--- |
| **5 Pavimentos** | 96 | 224 | 576 | **0.041s** |
| **20 Pavimentos** | 336 | 824 | 2.016 | **0.012s** |
| **50 Pavimentos** | 816 | 2.024 | 4.896 | **0.023s** |

*Comparado à versão puramente Python, o motor Rust entrega um speedup total de até **75×** em modelos de alta escala.*

---

## 🚀 Roadmap e Visão

O Atlas está em constante evolução. Nossos próximos marcos incluem:

- [x] **Solver Esparso Nativo**: Concluído e validado (faer-sparse).
- [ ] **Discretização de Lajes**: Integração de elementos de casca (Shells) diretamente no core Rust.
- [ ] **Análise Sísmica**: Espectro de resposta conforme a NBR 15421.
- [ ] **Interface Web 3D**: Visualização interativa e imersiva utilizando Next.js + Three.js.
- [ ] **Expansão de Surrogates**: Modelos de IA para contraventamentos e pilares de seção variável.

---

## 🔬 Um Convite à Colaboração

Se você é engenheiro estrutural, pesquisador em MEF, ou desenvolvedor apaixonado por computação científica: o Atlas é sua plataforma.

> **"Não somos apenas um solver; somos uma infraestrutura para a nova engenharia brasileira."**

**[Acesse o Repositório]** | **[Documentação Técnica]** | **[Benchmarks Públicos]**
