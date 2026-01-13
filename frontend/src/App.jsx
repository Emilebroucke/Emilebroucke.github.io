import React, { useEffect, useMemo, useState } from 'react'

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'

const emptyMessage = () => ({ role: 'assistant', content: '', sources: [] })

const citationRegex = /\[S(\d+):p(\d+):c(\d+)\]/g

function formatCitations(text, sources) {
  const parts = []
  let lastIndex = 0
  let match
  while ((match = citationRegex.exec(text)) !== null) {
    const [full, sourceId, page, chunkId] = match
    if (match.index > lastIndex) {
      parts.push(text.slice(lastIndex, match.index))
    }
    const source = sources.find((s) => String(s.id) === sourceId)
    const label = `S${sourceId}:p${page}:c${chunkId}`
    parts.push(
      <a
        key={`${sourceId}-${page}-${chunkId}-${match.index}`}
        className="citation"
        href="#"
        title={source ? source.filename : 'Unknown source'}
        onClick={(event) => event.preventDefault()}
      >
        [{label}]
      </a>
    )
    lastIndex = match.index + full.length
  }
  if (lastIndex < text.length) {
    parts.push(text.slice(lastIndex))
  }
  return parts
}

export default function App() {
  const [projects, setProjects] = useState([])
  const [selectedProject, setSelectedProject] = useState('')
  const [newProjectName, setNewProjectName] = useState('')
  const [sources, setSources] = useState([])
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [uploading, setUploading] = useState(false)
  const [streaming, setStreaming] = useState(false)

  useEffect(() => {
    fetch(`${API_BASE}/projects`)
      .then((res) => res.json())
      .then((data) => {
        setProjects(data)
        if (data.length > 0 && !selectedProject) {
          setSelectedProject(data[0].id)
        }
      })
      .catch(() => {})
  }, [])

  useEffect(() => {
    if (!selectedProject) return
    fetch(`${API_BASE}/projects/${selectedProject}/sources`)
      .then((res) => res.json())
      .then((data) => setSources(data))
      .catch(() => setSources([]))
  }, [selectedProject])

  const projectSources = useMemo(() => sources, [sources])

  const createProject = async () => {
    if (!newProjectName.trim()) return
    const response = await fetch(`${API_BASE}/projects`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name: newProjectName })
    })
    const data = await response.json()
    setProjects((prev) => [...prev, data])
    setSelectedProject(data.id)
    setNewProjectName('')
  }

  const handleUpload = async (event) => {
    const files = Array.from(event.target.files)
    if (!files.length || !selectedProject) return
    setUploading(true)
    const form = new FormData()
    files.forEach((file) => form.append('files', file))
    await fetch(`${API_BASE}/projects/${selectedProject}/upload`, {
      method: 'POST',
      body: form
    })
    setUploading(false)
    setTimeout(() => {
      fetch(`${API_BASE}/projects/${selectedProject}/sources`)
        .then((res) => res.json())
        .then((data) => setSources(data))
        .catch(() => {})
    }, 1500)
  }

  const sendMessage = async () => {
    if (!input.trim() || !selectedProject) return
    const userMessage = { role: 'user', content: input }
    setMessages((prev) => [...prev, userMessage, emptyMessage()])
    setInput('')
    setStreaming(true)

    const response = await fetch(`${API_BASE}/projects/${selectedProject}/chat/stream`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: userMessage.content })
    })

    const reader = response.body.getReader()
    const decoder = new TextDecoder('utf-8')
    let buffer = ''
    let collectedSources = []

    while (true) {
      const { value, done } = await reader.read()
      if (done) break
      buffer += decoder.decode(value, { stream: true })
      const parts = buffer.split('\n\n')
      buffer = parts.pop()
      parts.forEach((part) => {
        const lines = part.split('\n')
        const eventLine = lines.find((line) => line.startsWith('event: '))
        const dataLine = lines.find((line) => line.startsWith('data: '))
        if (!eventLine || !dataLine) return
        const eventName = eventLine.replace('event: ', '').trim()
        const data = dataLine.replace('data: ', '')
        if (eventName === 'sources') {
          try {
            collectedSources = JSON.parse(data)
          } catch {
            collectedSources = []
          }
        }
        if (eventName === 'token') {
          setMessages((prev) => {
            const next = [...prev]
            const last = next[next.length - 1]
            next[next.length - 1] = {
              ...last,
              content: `${last.content}${data}`,
              sources: collectedSources
            }
            return next
          })
        }
      })
    }
    setStreaming(false)
  }

  return (
    <div className="app">
      <header>
        <div>
          <h1>NotebookLM Local</h1>
          <p>Grounded chat with your sources, with citations.</p>
        </div>
        <div className="project-controls">
          <select
            value={selectedProject}
            onChange={(event) => setSelectedProject(event.target.value)}
          >
            <option value="">Select a notebook</option>
            {projects.map((project) => (
              <option key={project.id} value={project.id}>
                {project.id}
              </option>
            ))}
          </select>
          <input
            type="text"
            placeholder="New notebook name"
            value={newProjectName}
            onChange={(event) => setNewProjectName(event.target.value)}
          />
          <button onClick={createProject}>Create</button>
        </div>
      </header>

      <main>
        <section className="panel">
          <h2>Upload sources</h2>
          <input type="file" multiple onChange={handleUpload} />
          <p>{uploading ? 'Uploading...' : 'PDF, DOCX, TXT/MD, HTML, VTT/SRT, ZIP supported.'}</p>

          <h3>Sources</h3>
          <ul className="sources">
            {projectSources.map((source) => (
              <li key={source.id}>
                <strong>S{source.id}</strong> {source.filename}
                <span>{source.pages} pages</span>
              </li>
            ))}
          </ul>
        </section>

        <section className="panel chat">
          <h2>Chat</h2>
          <div className="messages">
            {messages.map((message, index) => (
              <div key={index} className={`message ${message.role}`}>
                <div className="role">{message.role}</div>
                <div className="content">
                  {formatCitations(message.content, message.sources || [])}
                </div>
              </div>
            ))}
          </div>
          <div className="input-row">
            <textarea
              placeholder="Ask, summarize, compare, find evidence..."
              value={input}
              onChange={(event) => setInput(event.target.value)}
              rows={3}
            />
            <button disabled={streaming} onClick={sendMessage}>
              {streaming ? 'Answering...' : 'Send'}
            </button>
          </div>
        </section>
      </main>
    </div>
  )
}
