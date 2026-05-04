# MEF Structural Elite - v1.0.0

Plataforma avançada de engenharia estrutural que integra análise de elementos finitos (MEF), design gerativo e auditoria forense assistida por IA.

## 🚀 Visão Geral

O **MEF Structural Elite** é dividido em duas frentes de trabalho coordenadas:

- **MESTRE (Academic Engine)**: Ambiente didático para análise de vigas contínuas (Hardy Cross), lajes e dimensionamento de elementos isolados.
- **UFO (Professional Engine)**: Motor de alta performance para análise global de edifícios, estabilidade alfa e concreto protendido (**TensionPro**).

## ✨ Principais Funcionalidades

- **M5-PhD Optimization**: Motor de design gerativo que sugere seções transversais otimizadas para redução de peso e custo.
- **BIM Interoperability**: Exportação de modelos em formato IFC 2x3 para integração com softwares de projeto (Revit, TQS, etc).
- **TensionPro**: Módulo de concreto protendido com simulação de perdas imediatas e diferidas (fluência/retração) via Rust Core.
- **Viga Cross**: Simulador didático de convergência de momentos hiperestáticos.
- **Audit Agent**: IA Ph.D. integrada que emite pareceres técnicos e diagnósticos de segurança normativa (NBR 6118:2023).

## 🛠️ Tecnologias

- **Frontend**: Next.js 16 (Turbopack), Tailwind CSS, Framer Motion.
- **Visualização**: Three.js (React Three Fiber) para modelos 3D dinâmicos.
- **Backend**: FastAPI (Python) & Rust (WebAssembly) para motores de cálculo pesado.

## ⚙️ Instalação e Execução

### Pré-requisitos
- Node.js 20+
- Python 3.10+ (para o backend de relatórios)

### Frontend
```bash
cd mef_dashboard
npm install
npm run dev
```
Acesse em: [http://localhost:3000](http://localhost:3000)

### Backend (Motores de Cálculo)
```bash
# Certifique-se de que a porta 8000 está liberada
python3 api.py
```

## 📜 Licença e Versionamento

O projeto segue a regra de versionamento **VibeDoCode**. Consulte o arquivo [atualizaçoes do projeto.md](./atualizaçoes%20do%20projeto.md) para o histórico completo de mudanças.

---
© 2026 Elite Engineering - Scaling Structural Intelligence
