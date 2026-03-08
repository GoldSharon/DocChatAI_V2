// ── State ──────────────────────────────────────
const state = {
  activeDocId: null,
  activeDocName: null,
  isLoading: false
}

// ── DOM References ─────────────────────────────
const uploadBox     = document.getElementById('uploadBox')
const fileInput     = document.getElementById('fileInput')
const uploadBtn     = document.getElementById('uploadBtn')
const uploadStatus  = document.getElementById('uploadStatus')
const refreshBtn    = document.getElementById('refreshBtn')
const docsList      = document.getElementById('docsList')
const messages      = document.getElementById('messages')
const questionInput = document.getElementById('questionInput')
const sendBtn       = document.getElementById('sendBtn')
const activeDocLabel= document.getElementById('activeDocLabel')

// ── Markdown renderer (marked.js loaded in HTML) ──
function renderMarkdown(text) {
  if (typeof marked !== 'undefined') {
    return marked.parse(text)
  }
  // Fallback: just escape and newline-break
  return escapeHtml(text)
}

// ── Upload Box: click & drag ───────────────────
uploadBox.addEventListener('click', () => fileInput.click())

fileInput.addEventListener('change', () => {
  if (fileInput.files[0]) {
    uploadBox.classList.add('has-file')
    uploadBox.querySelector('p').textContent = fileInput.files[0].name
    uploadBtn.disabled = false
  }
})

uploadBox.addEventListener('dragover', e => {
  e.preventDefault()
  uploadBox.classList.add('dragover')
})

uploadBox.addEventListener('dragleave', () => {
  uploadBox.classList.remove('dragover')
})

uploadBox.addEventListener('drop', e => {
  e.preventDefault()
  uploadBox.classList.remove('dragover')
  const file = e.dataTransfer.files[0]
  if (file) {
    fileInput.files = e.dataTransfer.files
    uploadBox.classList.add('has-file')
    uploadBox.querySelector('p').textContent = file.name
    uploadBtn.disabled = false
  }
})

// ── Upload Button ──────────────────────────────
uploadBtn.addEventListener('click', async () => {
  const file = fileInput.files[0]
  if (!file) return

  setUploadStatus('Uploading...', 'loading')
  uploadBtn.disabled = true

  const formData = new FormData()
  formData.append('file', file)

  try {
    const res  = await fetch('/api/v1/upload', { method: 'POST', body: formData })
    const data = await res.json()

    if (!res.ok) throw new Error(data.detail || 'Upload failed')

    setUploadStatus(`✓ Uploaded! ${data.chunk_count} chunks indexed`, 'success')
    resetUploadBox()
    loadDocuments()

  } catch (err) {
    setUploadStatus(`✗ ${err.message}`, 'error')
    uploadBtn.disabled = false
  }
})

// ── Load Documents ─────────────────────────────
async function loadDocuments() {
  try {
    const res  = await fetch('/api/v1/documents')
    const data = await res.json()

    if (!data.documents || data.documents.length === 0) {
      docsList.innerHTML = '<p class="empty-msg">No documents yet</p>'
      return
    }

    docsList.innerHTML = data.documents.map(doc => `
      <div class="doc-card ${state.activeDocId === doc.doc_id ? 'active' : ''}"
           onclick="selectDoc('${doc.doc_id}', '${doc.filename}')">
        <div class="doc-name">${doc.filename}</div>
        <div class="doc-meta">${doc.chunk_count} chunks · ID: ${doc.doc_id}</div>
      </div>
    `).join('')

  } catch (err) {
    docsList.innerHTML = '<p class="empty-msg">Error loading documents</p>'
  }
}

// ── Select Document ────────────────────────────
function selectDoc(docId, filename) {
  state.activeDocId   = docId
  state.activeDocName = filename
  activeDocLabel.textContent = `Asking about: ${filename}`
  loadDocuments()
}

// ── Send Question ──────────────────────────────
async function sendQuestion() {
  const question = questionInput.value.trim()
  if (!question || state.isLoading) return

  state.isLoading = true
  sendBtn.disabled = true
  questionInput.value = ''
  autoResize()

  const welcome = document.querySelector('.welcome-msg')
  if (welcome) welcome.remove()

  appendMessage('user', question)
  const typingId = showTyping()

  try {
    const endpoint = '/api/v1/ask'
    const body = { question }
    if (state.activeDocId) body.document_id = state.activeDocId

    const res  = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body)
    })

    const data = await res.json()
    removeTyping(typingId)

    if (!res.ok) throw new Error(data.detail || 'API error')

    appendBotMessage(data)

  } catch (err) {
    removeTyping(typingId)
    appendMessage('bot', `Error: ${err.message}`)
  }

  state.isLoading  = false
  sendBtn.disabled = false
  questionInput.focus()
}

// ── Message Rendering ──────────────────────────
function appendMessage(role, text) {
  const div = document.createElement('div')
  div.className = `message ${role}`
  div.innerHTML = `
    <div class="message-label">${role === 'user' ? 'You' : '🤖 DocChat'}</div>
    <div class="bubble">${escapeHtml(text)}</div>
  `
  messages.appendChild(div)
  scrollToBottom()
}

function appendBotMessage(data) {
  const div = document.createElement('div')
  div.className = 'message bot'

  const sourcesHtml = data.sources && data.sources.length > 0
    ? `<div class="sources">
        <div class="message-label">📎 ${data.sources.length} chunk${data.sources.length !== 1 ? 's' : ''} matched</div>
       </div>`
    : ''

  div.innerHTML = `
    <div class="message-label">🤖 DocChat</div>
    <div class="bubble markdown-body">${renderMarkdown(data.answer)}</div>
    ${sourcesHtml}
  `
  messages.appendChild(div)
  scrollToBottom()
}

// ── Typing Indicator ───────────────────────────
function showTyping() {
  const id  = 'typing-' + Date.now()
  const div = document.createElement('div')
  div.className = 'message bot typing'
  div.id = id
  div.innerHTML = `
    <div class="message-label">🤖 DocChat</div>
    <div class="bubble">
      <div class="typing-dot"></div>
      <div class="typing-dot"></div>
      <div class="typing-dot"></div>
    </div>
  `
  messages.appendChild(div)
  scrollToBottom()
  return id
}

function removeTyping(id) {
  const el = document.getElementById(id)
  if (el) el.remove()
}

// ── Helpers ────────────────────────────────────
function scrollToBottom() {
  messages.scrollTop = messages.scrollHeight
}

function escapeHtml(str) {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/\n/g, '<br>')
}

function setUploadStatus(msg, type) {
  uploadStatus.textContent  = msg
  uploadStatus.className    = `status-msg ${type}`
}

function resetUploadBox() {
  uploadBox.classList.remove('has-file')
  uploadBox.querySelector('p').textContent = 'Click or drag a file here'
  fileInput.value  = ''
  uploadBtn.disabled = true
}

function autoResize() {
  questionInput.style.height = 'auto'
  questionInput.style.height = questionInput.scrollHeight + 'px'
}

// ── Keyboard Shortcuts ─────────────────────────
questionInput.addEventListener('keydown', e => {
  if (e.key === 'Enter' && e.ctrlKey) sendQuestion()
})

questionInput.addEventListener('input', autoResize)
sendBtn.addEventListener('click', sendQuestion)
refreshBtn.addEventListener('click', loadDocuments)

// ── New Session ───────────────────────────────
const newSessionBtn = document.getElementById('newSessionBtn')

if (newSessionBtn) {
  let clearPending = false

  newSessionBtn.addEventListener('click', async function () {
    if (!clearPending) {
      clearPending = true
      newSessionBtn.textContent = '⚠ Confirm Clear?'
      newSessionBtn.classList.add('confirm-mode')
      setTimeout(() => {
        if (clearPending) {
          clearPending = false
          newSessionBtn.textContent = '🗑 Clear Session'
          newSessionBtn.classList.remove('confirm-mode')
        }
      }, 3000)
      return
    }

    clearPending = false
    newSessionBtn.textContent = 'Clearing...'
    newSessionBtn.disabled = true
    newSessionBtn.classList.remove('confirm-mode')

    try {
      const res = await fetch('/api/v1/session', { method: 'DELETE' })
      if (!res.ok) throw new Error('Server error')

      docsList.innerHTML = '<p class="empty-msg">No documents yet</p>'
      messages.innerHTML = '<div class="welcome-msg"><h2>👋 Welcome to DocChat!</h2><p>Upload a document on the left, then ask questions here.</p><p>You can also chat without a document for general questions.</p></div>'
      state.activeDocId   = null
      state.activeDocName = null
      activeDocLabel.textContent = 'No document selected — asking without context'
      setUploadStatus('✓ Session cleared', 'success')
      setTimeout(() => setUploadStatus('', ''), 3000)

    } catch (err) {
      setUploadStatus('✗ ' + err.message, 'error')
    }

    newSessionBtn.textContent = '🗑 Clear Session'
    newSessionBtn.disabled = false
  })
}

// ── Init ───────────────────────────────────────
loadDocuments()