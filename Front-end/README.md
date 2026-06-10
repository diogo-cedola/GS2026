# 🛰️ SpaceOps — Painel de Monitoramento da Nova Economia Espacial

Aplicação web desenvolvida para a Global Solution 2026.1 da FIAP, disciplina de Inteligência Artificial.

## 🚀 Sobre a Solução

O **SpaceOps** é um painel de monitoramento de missões espaciais que representa a Nova Economia Espacial. A plataforma permite acompanhar em tempo real o status de missões lunares, marcianas, satélites de monitoramento ambiental e agrícola, com suporte a um assistente de IA para apoio à tomada de decisão.

### Funcionalidades

- **Dashboard** — estatísticas gerais e gráfico de telemetria animado em tempo real (temperatura, pressão, radiação)
- **Missões** — listagem de 6 missões com filtro por status (ativa, planejada, concluída, falha) e métricas de altitude, velocidade e combustível
- **Alertas** — sistema de alertas com severidades (crítica, alta, média, baixa) e marcação de leitura
- **Assistente ARIA** — agente conversacional de apoio à tomada de decisão com respostas sobre telemetria, combustível, trajetórias e status de missões

## 🛠️ Tecnologias Utilizadas

- [React 19](https://react.dev/) + [Vite](https://vite.dev/)
- [Styled Components](https://styled-components.com/) — estilização com CSS-in-JS
- [Recharts](https://recharts.org/) — gráficos interativos de telemetria
- Context API — gerenciamento de estado global (`MissoesContext`)
- Hooks: `useState`, `useEffect`, `useRef`, `useContext`

## 📋 Conceitos de React Aplicados

- Componentes funcionais com props
- `useState` para controle de estado local (filtros, mensagens, tela ativa)
- `useEffect` para atualização periódica da telemetria em tempo real
- Renderização condicional por status de missão e alertas
- Listas renderizadas com `.map()` e `.filter()`
- Tratamento de eventos de clique e teclado
- Context API para estado compartilhado entre componentes

## 🌐 Aplicação no Ar

> 🔗 **https://gs-frontendfiap.vercel.app**

## 👥 Integrantes

| Nome | RM |
|------|----|
| Diogo Cedola | RM559797 |
| Felipe Sayeg | RM560366 |
| Caio Santiago de Oliveira | RM559788 |

**Curso:** Front End & Mobile Development — FIAP
**Disciplina:** Inteligência Artificial
**Ano:** 2º ano · 2026.1
