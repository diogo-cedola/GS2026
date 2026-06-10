import styled from 'styled-components'
import { useMissoes } from '../context/MissoesContext'

const Page = styled.div`
  padding: 28px 32px;
  max-width: 900px;
  margin: 0 auto;
`

const Header = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
`

const Title = styled.h1`
  color: #e0f0ff;
  font-size: 22px;
  font-weight: 700;
`

const BtnLimpar = styled.button`
  background: transparent;
  color: #4fc3f7;
  border: 1px solid #1e2d4a;
  border-radius: 8px;
  padding: 8px 16px;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
  &:hover { border-color: #4fc3f7; background: rgba(79,195,247,0.08); }
`

const Lista = styled.div`
  display: flex;
  flex-direction: column;
  gap: 12px;
`

const Item = styled.div`
  background: #0f1729;
  border: 1px solid ${({ $lido }) => $lido ? '#1e2d4a' : '#2a3f5f'};
  border-left: 4px solid ${({ severidade }) =>
    severidade === 'critica' ? '#ef5350' :
    severidade === 'alta' ? '#ff7043' :
    severidade === 'media' ? '#ffb74d' : '#66bb6a'};
  border-radius: 10px;
  padding: 16px 20px;
  display: flex;
  align-items: flex-start;
  gap: 14px;
  opacity: ${({ $lido }) => $lido ? 0.55 : 1};
  transition: opacity 0.2s;
`

const Icone = styled.div`
  font-size: 22px;
  flex-shrink: 0;
  margin-top: 2px;
`

const Corpo = styled.div`
  flex: 1;
`

const Topo = styled.div`
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 4px;
`

const MissaoTag = styled.span`
  font-size: 12px;
  font-weight: 700;
  color: #4fc3f7;
`

const SevBadge = styled.span`
  font-size: 11px;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: 10px;
  background: ${({ sev }) =>
    sev === 'critica' ? 'rgba(239,83,80,0.15)' :
    sev === 'alta' ? 'rgba(255,112,67,0.15)' :
    sev === 'media' ? 'rgba(255,183,77,0.15)' : 'rgba(102,187,106,0.15)'};
  color: ${({ sev }) =>
    sev === 'critica' ? '#ef5350' :
    sev === 'alta' ? '#ff7043' :
    sev === 'media' ? '#ffb74d' : '#66bb6a'};
  text-transform: uppercase;
`

const Mensagem = styled.p`
  color: ${({ $lido }) => $lido ? '#445566' : '#c0d8f0'};
  font-size: 14px;
  line-height: 1.5;
`

const Rodape = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 8px;
`

const Hora = styled.span`
  font-size: 12px;
  color: #334455;
`

const BtnMarcar = styled.button`
  background: transparent;
  color: #4fc3f7;
  border: none;
  font-size: 12px;
  cursor: pointer;
  padding: 0;
  &:hover { text-decoration: underline; }
  &:disabled { color: #334455; cursor: default; text-decoration: none; }
`

const Vazio = styled.div`
  text-align: center;
  color: #334455;
  padding: 80px 0;
  font-size: 15px;
`

const iconePorTipo = {
  combustivel: '⛽',
  comunicacao: '📡',
  sensor: '🔧',
  critico: '🚨',
  clima: '🌩️',
}

export default function Alertas() {
  const { alertas, marcarAlertaLido, marcarTodosLidos } = useMissoes()
  const naoLidos = alertas.filter(a => !a.lido).length

  return (
    <Page>
      <Header>
        <Title>
          Alertas do Sistema
          {naoLidos > 0 && <span style={{ color: '#ef5350', fontSize: 15, marginLeft: 10 }}>
            {naoLidos} não lido{naoLidos > 1 ? 's' : ''}
          </span>}
        </Title>
        {naoLidos > 0 && (
          <BtnLimpar onClick={marcarTodosLidos}>Marcar todos como lidos</BtnLimpar>
        )}
      </Header>

      {alertas.length === 0 ? (
        <Vazio>✅ Nenhum alerta registrado.</Vazio>
      ) : (
        <Lista>
          {alertas.map(a => (
            <Item key={a.id} severidade={a.severidade} $lido={a.lido}>
              <Icone>{iconePorTipo[a.tipo] || '⚠️'}</Icone>
              <Corpo>
                <Topo>
                  <MissaoTag>{a.missao}</MissaoTag>
                  <SevBadge sev={a.severidade}>{a.severidade}</SevBadge>
                </Topo>
                <Mensagem $lido={a.lido}>{a.mensagem}</Mensagem>
                <Rodape>
                  <Hora>Hoje às {a.hora}</Hora>
                  <BtnMarcar
                    disabled={a.lido}
                    onClick={() => marcarAlertaLido(a.id)}
                  >
                    {a.lido ? '✓ Lido' : 'Marcar como lido'}
                  </BtnMarcar>
                </Rodape>
              </Corpo>
            </Item>
          ))}
        </Lista>
      )}
    </Page>
  )
}
