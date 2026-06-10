import { useState, useRef, useEffect } from 'react'
import styled, { keyframes } from 'styled-components'
import { respostasIA } from '../data/missoes'

const Page = styled.div`
  padding: 28px 32px;
  max-width: 800px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  height: calc(100vh - 60px);
`

const Title = styled.h1`
  color: #e0f0ff;
  font-size: 22px;
  font-weight: 700;
  margin-bottom: 4px;
`

const Sub = styled.p`
  color: #5577aa;
  font-size: 13px;
  margin-bottom: 20px;
`

const Chat = styled.div`
  flex: 1;
  background: #0f1729;
  border: 1px solid #1e2d4a;
  border-radius: 14px;
  padding: 20px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-bottom: 16px;
  scroll-behavior: smooth;
`

const Blink = keyframes`
  0%, 100% { opacity: 1; }
  50% { opacity: 0; }
`

const Msg = styled.div`
  display: flex;
  flex-direction: ${({ $user }) => $user ? 'row-reverse' : 'row'};
  align-items: flex-start;
  gap: 10px;
`

const Avatar = styled.div`
  width: 34px;
  height: 34px;
  border-radius: 50%;
  background: ${({ $user }) => $user ? 'rgba(79,195,247,0.2)' : 'rgba(76,175,80,0.2)'};
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  flex-shrink: 0;
`

const Balao = styled.div`
  max-width: 80%;
  background: ${({ $user }) => $user ? 'rgba(79,195,247,0.12)' : '#0a0e1a'};
  border: 1px solid ${({ $user }) => $user ? 'rgba(79,195,247,0.25)' : '#1e2d4a'};
  border-radius: ${({ $user }) => $user ? '14px 4px 14px 14px' : '4px 14px 14px 14px'};
  padding: 12px 16px;
  color: #c0d8f0;
  font-size: 14px;
  line-height: 1.6;
`

const Digitando = styled.div`
  display: flex;
  gap: 4px;
  align-items: center;
  padding: 4px 0;
`

const Ponto = styled.span`
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #4fc3f7;
  animation: ${Blink} 1.2s ease-in-out infinite;
  animation-delay: ${({ delay }) => delay};
`

const Sugestoes = styled.div`
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-bottom: 12px;
`

const Sug = styled.button`
  background: #0a0e1a;
  border: 1px solid #1e2d4a;
  border-radius: 20px;
  color: #5577aa;
  font-size: 12px;
  padding: 5px 12px;
  cursor: pointer;
  transition: all 0.2s;
  &:hover { border-color: #4fc3f7; color: #c0d8f0; }
`

const InputRow = styled.div`
  display: flex;
  gap: 10px;
`

const Input = styled.input`
  flex: 1;
  background: #0f1729;
  border: 1px solid #1e2d4a;
  border-radius: 10px;
  padding: 12px 16px;
  color: #e0f0ff;
  font-size: 14px;
  outline: none;
  transition: border-color 0.2s;
  &::placeholder { color: #334455; }
  &:focus { border-color: #4fc3f7; }
`

const Enviar = styled.button`
  background: #4fc3f7;
  color: #0a0e1a;
  border: none;
  border-radius: 10px;
  padding: 12px 20px;
  font-size: 14px;
  font-weight: 700;
  cursor: pointer;
  transition: opacity 0.2s;
  &:hover { opacity: 0.85; }
  &:disabled { opacity: 0.4; cursor: default; }
`

const sugestoesRapidas = [
  'Status das missões',
  'Nível de combustível',
  'Dados de radiação',
  'Janela para Marte',
  'Variação de temperatura',
]

function buscarResposta(texto) {
  const t = texto.toLowerCase()
  if (t.includes('combustiv') || t.includes('fuel')) return respostasIA.combustivel
  if (t.includes('temperatura') || t.includes('térm')) return respostasIA.temperatura
  if (t.includes('radi')) return respostasIA.radiacao
  if (t.includes('status') || t.includes('missão') || t.includes('missoes')) return respostasIA.status
  if (t.includes('marte') || t.includes('mars')) return respostasIA.marte
  return respostasIA.padrão
}

export default function Assistente() {
  const [mensagens, setMensagens] = useState([
    {
      id: 0,
      texto: 'Olá! Sou o ARIA — Agente de Resposta Inteligente Aeroespacial. Posso ajudar com análise de telemetria, status de missões, planejamento de trajetórias e muito mais. Como posso ajudar?',
      user: false,
    }
  ])
  const [input, setInput] = useState('')
  const [digitando, setDigitando] = useState(false)
  const chatRef = useRef(null)

  useEffect(() => {
    if (chatRef.current) {
      chatRef.current.scrollTop = chatRef.current.scrollHeight
    }
  }, [mensagens, digitando])

  function enviar(texto) {
    const msg = texto || input.trim()
    if (!msg) return
    setInput('')
    setMensagens(prev => [...prev, { id: Date.now(), texto: msg, user: true }])
    setDigitando(true)
    setTimeout(() => {
      setDigitando(false)
      setMensagens(prev => [...prev, {
        id: Date.now() + 1,
        texto: buscarResposta(msg),
        user: false,
      }])
    }, 1200 + Math.random() * 800)
  }

  function handleKey(e) {
    if (e.key === 'Enter') enviar()
  }

  return (
    <Page>
      <Title>🤖 Assistente ARIA</Title>
      <Sub>Agente de Resposta Inteligente Aeroespacial — powered by SpaceOps AI</Sub>

      <Chat ref={chatRef}>
        {mensagens.map(m => (
          <Msg key={m.id} $user={m.user}>
            <Avatar $user={m.user}>{m.user ? '👤' : '🤖'}</Avatar>
            <Balao $user={m.user}>{m.texto}</Balao>
          </Msg>
        ))}
        {digitando && (
          <Msg $user={false}>
            <Avatar>🤖</Avatar>
            <Balao>
              <Digitando>
                <Ponto delay="0s" />
                <Ponto delay="0.2s" />
                <Ponto delay="0.4s" />
              </Digitando>
            </Balao>
          </Msg>
        )}
      </Chat>

      <Sugestoes>
        {sugestoesRapidas.map(s => (
          <Sug key={s} onClick={() => enviar(s)}>{s}</Sug>
        ))}
      </Sugestoes>

      <InputRow>
        <Input
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={handleKey}
          placeholder="Pergunte sobre telemetria, missões, trajetórias..."
          disabled={digitando}
        />
        <Enviar onClick={() => enviar()} disabled={digitando || !input.trim()}>
          Enviar
        </Enviar>
      </InputRow>
    </Page>
  )
}
