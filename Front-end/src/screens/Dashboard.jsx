import { useEffect, useState } from 'react'
import styled from 'styled-components'
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend
} from 'recharts'
import { useMissoes } from '../context/MissoesContext'
import { telemetria } from '../data/missoes'

const Page = styled.div`
  padding: 28px 32px;
  max-width: 1200px;
  margin: 0 auto;
`

const Title = styled.h1`
  color: #e0f0ff;
  font-size: 22px;
  font-weight: 700;
  margin-bottom: 6px;
`

const Sub = styled.p`
  color: #5577aa;
  font-size: 14px;
  margin-bottom: 28px;
`

const Cards = styled.div`
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 28px;
  @media (max-width: 900px) { grid-template-columns: repeat(2, 1fr); }
`

const Card = styled.div`
  background: #0f1729;
  border: 1px solid #1e2d4a;
  border-radius: 12px;
  padding: 20px;
`

const CardLabel = styled.div`
  color: #5577aa;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.8px;
  margin-bottom: 8px;
`

const CardValue = styled.div`
  font-size: 32px;
  font-weight: 700;
  color: ${({ color }) => color || '#e0f0ff'};
`

const CardSub = styled.div`
  font-size: 12px;
  color: #445566;
  margin-top: 4px;
`

const Row = styled.div`
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  @media (max-width: 900px) { grid-template-columns: 1fr; }
`

const ChartBox = styled.div`
  background: #0f1729;
  border: 1px solid #1e2d4a;
  border-radius: 12px;
  padding: 20px;
`

const ChartTitle = styled.div`
  color: #c0d8f0;
  font-size: 15px;
  font-weight: 600;
  margin-bottom: 16px;
`

const MissaoItem = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 0;
  border-bottom: 1px solid #111e30;
  &:last-child { border-bottom: none; }
`

const MissaoNome = styled.span`
  color: #c0d8f0;
  font-size: 14px;
`

const BarWrap = styled.div`
  display: flex;
  align-items: center;
  gap: 10px;
  width: 200px;
`

const Bar = styled.div`
  flex: 1;
  height: 6px;
  background: #1a2840;
  border-radius: 3px;
  overflow: hidden;
`

const BarFill = styled.div`
  height: 100%;
  width: ${({ pct }) => pct}%;
  background: ${({ pct }) =>
    pct >= 70 ? '#4fc3f7' : pct >= 40 ? '#ffb74d' : '#ef5350'};
  border-radius: 3px;
  transition: width 0.8s ease;
`

const Pct = styled.span`
  color: #5577aa;
  font-size: 12px;
  min-width: 36px;
  text-align: right;
`

const StatusDot = styled.span`
  display: inline-block;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: ${({ status }) =>
    status === 'ativa' ? '#4caf50' :
    status === 'concluida' ? '#4fc3f7' :
    status === 'planejada' ? '#ffb74d' : '#ef5350'};
  margin-right: 8px;
`

export default function Dashboard() {
  const { missoes, alertas } = useMissoes()
  const [dados, setDados] = useState([])

  useEffect(() => {
    let i = 0
    setDados(telemetria.slice(0, 5))
    const intervalo = setInterval(() => {
      i++
      if (i + 5 <= telemetria.length) {
        setDados(telemetria.slice(i, i + 10))
      } else {
        i = 0
      }
    }, 2000)
    return () => clearInterval(intervalo)
  }, [])

  const ativas = missoes.filter(m => m.status === 'ativa').length
  const concluidas = missoes.filter(m => m.status === 'concluida').length
  const alertasAbertos = alertas.filter(a => !a.lido).length
  const ativasComDados = missoes.filter(m => m.status === 'ativa')

  return (
    <Page>
      <Title>Painel de Controle</Title>
      <Sub>Monitoramento em tempo real — Nova Economia Espacial · {new Date().toLocaleDateString('pt-BR', { weekday: 'long', day: '2-digit', month: 'long', year: 'numeric' })}</Sub>

      <Cards>
        <Card>
          <CardLabel>Missões Ativas</CardLabel>
          <CardValue color="#4caf50">{ativas}</CardValue>
          <CardSub>em operação agora</CardSub>
        </Card>
        <Card>
          <CardLabel>Concluídas</CardLabel>
          <CardValue color="#4fc3f7">{concluidas}</CardValue>
          <CardSub>missões finalizadas</CardSub>
        </Card>
        <Card>
          <CardLabel>Total de Missões</CardLabel>
          <CardValue>{missoes.length}</CardValue>
          <CardSub>no sistema</CardSub>
        </Card>
        <Card>
          <CardLabel>Alertas Abertos</CardLabel>
          <CardValue color={alertasAbertos > 0 ? '#ef5350' : '#4caf50'}>{alertasAbertos}</CardValue>
          <CardSub>{alertasAbertos > 0 ? 'requerem atenção' : 'tudo em ordem'}</CardSub>
        </Card>
      </Cards>

      <Row>
        <ChartBox>
          <ChartTitle>Telemetria em Tempo Real</ChartTitle>
          <ResponsiveContainer width="100%" height={220}>
            <LineChart data={dados}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1a2840" />
              <XAxis dataKey="tempo" stroke="#334455" tick={{ fill: '#5577aa', fontSize: 11 }} />
              <YAxis stroke="#334455" tick={{ fill: '#5577aa', fontSize: 11 }} />
              <Tooltip
                contentStyle={{ background: '#0a0e1a', border: '1px solid #1e2d4a', borderRadius: 8 }}
                labelStyle={{ color: '#c0d8f0' }}
              />
              <Legend wrapperStyle={{ fontSize: 12, color: '#5577aa' }} />
              <Line type="monotone" dataKey="temperatura" stroke="#4fc3f7" strokeWidth={2} dot={false} name="Temp (°C)" />
              <Line type="monotone" dataKey="pressao" stroke="#ffb74d" strokeWidth={2} dot={false} name="Pressão (kPa)" />
              <Line type="monotone" dataKey="radiacao" stroke="#ef5350" strokeWidth={2} dot={false} name="Radiação (mSv/h)" />
            </LineChart>
          </ResponsiveContainer>
        </ChartBox>

        <ChartBox>
          <ChartTitle>Progresso das Missões Ativas</ChartTitle>
          {ativasComDados.map(m => (
            <MissaoItem key={m.id}>
              <MissaoNome>
                <StatusDot status={m.status} />
                {m.nome}
              </MissaoNome>
              <BarWrap>
                <Bar><BarFill pct={m.progresso} /></Bar>
                <Pct>{m.progresso}%</Pct>
              </BarWrap>
            </MissaoItem>
          ))}
        </ChartBox>
      </Row>
    </Page>
  )
}
