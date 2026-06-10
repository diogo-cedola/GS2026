import { useState } from 'react'
import styled from 'styled-components'
import { useMissoes } from '../context/MissoesContext'

const Page = styled.div`
  padding: 28px 32px;
  max-width: 1200px;
  margin: 0 auto;
`

const Header = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
  flex-wrap: wrap;
  gap: 12px;
`

const Title = styled.h1`
  color: #e0f0ff;
  font-size: 22px;
  font-weight: 700;
`

const Filtros = styled.div`
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
`

const FiltroBtn = styled.button`
  background: ${({ $ativo }) => $ativo ? 'rgba(79,195,247,0.2)' : '#0f1729'};
  color: ${({ $ativo }) => $ativo ? '#4fc3f7' : '#5577aa'};
  border: 1px solid ${({ $ativo }) => $ativo ? '#4fc3f7' : '#1e2d4a'};
  border-radius: 20px;
  padding: 6px 14px;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
  &:hover { border-color: #4fc3f7; color: #c0d8f0; }
`

const Grid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
  gap: 20px;
`

const Card = styled.div`
  background: #0f1729;
  border: 1px solid #1e2d4a;
  border-radius: 14px;
  padding: 22px;
  cursor: pointer;
  transition: border-color 0.2s, transform 0.2s;
  &:hover {
    border-color: #4fc3f7;
    transform: translateY(-2px);
  }
`

const CardTop = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
`

const Nome = styled.div`
  font-size: 17px;
  font-weight: 700;
  color: #e0f0ff;
`

const Tipo = styled.div`
  font-size: 12px;
  color: #5577aa;
  margin-top: 2px;
`

const StatusBadge = styled.span`
  font-size: 12px;
  font-weight: 600;
  padding: 4px 10px;
  border-radius: 20px;
  background: ${({ status }) =>
    status === 'ativa' ? 'rgba(76,175,80,0.15)' :
    status === 'concluida' ? 'rgba(79,195,247,0.15)' :
    status === 'planejada' ? 'rgba(255,183,77,0.15)' : 'rgba(239,83,80,0.15)'};
  color: ${({ status }) =>
    status === 'ativa' ? '#4caf50' :
    status === 'concluida' ? '#4fc3f7' :
    status === 'planejada' ? '#ffb74d' : '#ef5350'};
`

const Desc = styled.p`
  color: #5577aa;
  font-size: 13px;
  line-height: 1.5;
  margin-bottom: 16px;
`

const Metricas = styled.div`
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
  margin-bottom: 14px;
`

const Metrica = styled.div`
  background: #0a0e1a;
  border-radius: 8px;
  padding: 8px;
  text-align: center;
`

const MetricaVal = styled.div`
  font-size: 15px;
  font-weight: 700;
  color: #c0d8f0;
`

const MetricaLabel = styled.div`
  font-size: 11px;
  color: #334455;
  margin-top: 2px;
`

const BarWrap = styled.div``

const BarLabel = styled.div`
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: #5577aa;
  margin-bottom: 4px;
`

const Bar = styled.div`
  height: 5px;
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
`

const Vazio = styled.div`
  text-align: center;
  color: #334455;
  padding: 60px 0;
  font-size: 15px;
`

const statusLabels = {
  todos: 'Todos',
  ativa: 'Ativas',
  planejada: 'Planejadas',
  concluida: 'Concluídas',
  falha: 'Falha',
}

export default function Missoes() {
  const { missoes } = useMissoes()
  const [filtro, setFiltro] = useState('todos')

  const filtradas = filtro === 'todos' ? missoes : missoes.filter(m => m.status === filtro)

  return (
    <Page>
      <Header>
        <Title>Missões Espaciais</Title>
        <Filtros>
          {Object.entries(statusLabels).map(([key, label]) => (
            <FiltroBtn key={key} $ativo={filtro === key} onClick={() => setFiltro(key)}>
              {label}
            </FiltroBtn>
          ))}
        </Filtros>
      </Header>

      {filtradas.length === 0 ? (
        <Vazio>Nenhuma missão encontrada com este filtro.</Vazio>
      ) : (
        <Grid>
          {filtradas.map(m => (
            <Card key={m.id}>
              <CardTop>
                <div>
                  <Nome>{m.nome}</Nome>
                  <Tipo>{m.tipo} · Lançamento: {new Date(m.lancamento).toLocaleDateString('pt-BR')}</Tipo>
                </div>
                <StatusBadge status={m.status}>{statusLabels[m.status]}</StatusBadge>
              </CardTop>

              <Desc>{m.descricao}</Desc>

              {m.status === 'ativa' && (
                <Metricas>
                  <Metrica>
                    <MetricaVal>{m.altitude > 1000 ? `${(m.altitude/1000).toFixed(0)}k km` : `${m.altitude} km`}</MetricaVal>
                    <MetricaLabel>Altitude</MetricaLabel>
                  </Metrica>
                  <Metrica>
                    <MetricaVal>{m.velocidade > 0 ? `${m.velocidade} km/h` : '—'}</MetricaVal>
                    <MetricaLabel>Velocidade</MetricaLabel>
                  </Metrica>
                  <Metrica>
                    <MetricaVal style={{ color: m.combustivel < 30 ? '#ef5350' : '#c0d8f0' }}>
                      {m.combustivel}%
                    </MetricaVal>
                    <MetricaLabel>Combustível</MetricaLabel>
                  </Metrica>
                </Metricas>
              )}

              <BarWrap>
                <BarLabel>
                  <span>Progresso da Missão</span>
                  <span>{m.progresso}%</span>
                </BarLabel>
                <Bar><BarFill pct={m.progresso} /></Bar>
              </BarWrap>
            </Card>
          ))}
        </Grid>
      )}
    </Page>
  )
}
