import { createContext, useContext, useState, useEffect } from 'react'
import { missoes as dadosIniciais, alertas as dadosAlertas } from '../data/missoes'

const MissoesContext = createContext()

export function MissoesProvider({ children }) {
  const [missoes, setMissoes] = useState(dadosIniciais)
  const [alertas, setAlertas] = useState(dadosAlertas)
  const [telemetriaAtiva, setTelemetriaAtiva] = useState(null)

  const totalAtivas = missoes.filter(m => m.status === 'ativa').length
  const totalAlertas = alertas.filter(a => !a.lido).length

  function marcarAlertaLido(id) {
    setAlertas(prev => prev.map(a => a.id === id ? { ...a, lido: true } : a))
  }

  function marcarTodosLidos() {
    setAlertas(prev => prev.map(a => ({ ...a, lido: true })))
  }

  return (
    <MissoesContext.Provider value={{
      missoes,
      alertas,
      totalAtivas,
      totalAlertas,
      telemetriaAtiva,
      setTelemetriaAtiva,
      marcarAlertaLido,
      marcarTodosLidos,
    }}>
      {children}
    </MissoesContext.Provider>
  )
}

export function useMissoes() {
  return useContext(MissoesContext)
}
