import { useState } from 'react'
import { createGlobalStyle } from 'styled-components'
import { MissoesProvider } from './context/MissoesContext'
import NavBar from './components/NavBar'
import Dashboard from './screens/Dashboard'
import Missoes from './screens/Missoes'
import Alertas from './screens/Alertas'
import Assistente from './screens/Assistente'

const GlobalStyle = createGlobalStyle`
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    font-family: 'Inter', 'Segoe UI', system-ui, sans-serif;
    background: #060a12;
    color: #c0d8f0;
    min-height: 100vh;
    -webkit-font-smoothing: antialiased;
  }
  ::-webkit-scrollbar { width: 6px; }
  ::-webkit-scrollbar-track { background: #0a0e1a; }
  ::-webkit-scrollbar-thumb { background: #1e2d4a; border-radius: 3px; }
`

export default function App() {
  const [tela, setTela] = useState('dashboard')

  const renderTela = () => {
    if (tela === 'missoes') return <Missoes />
    if (tela === 'alertas') return <Alertas />
    if (tela === 'assistente') return <Assistente />
    return <Dashboard />
  }

  return (
    <MissoesProvider>
      <GlobalStyle />
      <NavBar tela={tela} setTela={setTela} />
      {renderTela()}
    </MissoesProvider>
  )
}
