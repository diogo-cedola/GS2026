import styled from 'styled-components'
import { useMissoes } from '../context/MissoesContext'

const Nav = styled.nav`
  background: #0a0e1a;
  border-bottom: 1px solid #1e2d4a;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  height: 60px;
  position: sticky;
  top: 0;
  z-index: 100;
`

const Logo = styled.div`
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 18px;
  font-weight: 700;
  color: #fff;
  span { color: #4fc3f7; }
`

const Links = styled.div`
  display: flex;
  gap: 4px;
`

const Link = styled.button`
  background: ${({ $ativo }) => $ativo ? 'rgba(79,195,247,0.15)' : 'transparent'};
  color: ${({ $ativo }) => $ativo ? '#4fc3f7' : '#8899aa'};
  border: none;
  border-bottom: 2px solid ${({ $ativo }) => $ativo ? '#4fc3f7' : 'transparent'};
  padding: 8px 16px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  &:hover { color: #fff; }
`

const Badge = styled.span`
  background: #ef5350;
  color: #fff;
  border-radius: 10px;
  font-size: 11px;
  font-weight: 700;
  padding: 1px 6px;
  margin-left: 6px;
`

const Status = styled.div`
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #4caf50;
  &::before {
    content: '';
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #4caf50;
    animation: pulse 2s infinite;
  }
  @keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.4; }
  }
`

const telas = [
  { id: 'dashboard', label: '⬡ Dashboard' },
  { id: 'missoes', label: '🚀 Missões' },
  { id: 'alertas', label: '🔔 Alertas' },
  { id: 'assistente', label: '🤖 Assistente IA' },
]

export default function NavBar({ tela, setTela }) {
  const { totalAlertas, totalAtivas } = useMissoes()

  return (
    <Nav>
      <Logo>🛰️ <span>Space</span>Ops
      </Logo>
      <Links>
        {telas.map(t => (
          <Link key={t.id} $ativo={tela === t.id} onClick={() => setTela(t.id)}>
            {t.label}
            {t.id === 'alertas' && totalAlertas > 0 && <Badge>{totalAlertas}</Badge>}
          </Link>
        ))}
      </Links>
      <Status>{totalAtivas} missões ativas</Status>
    </Nav>
  )
}
