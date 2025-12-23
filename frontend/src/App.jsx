import { useEffect, useState } from 'react'
import { healthCheck } from './services/api'

function App() {
  const [backendStatus, setBackendStatus] = useState('checking...')

  useEffect(() => {
    healthCheck()
      .then((data) => setBackendStatus(data.status))
      .catch(() => setBackendStatus('offline'))
  }, [])

  return (
    <div className="dark h-screen w-screen bg-gray-900 text-gray-100 flex flex-col">
      {/* Header */}
      <header className="h-12 border-b border-gray-700 flex items-center px-4 shrink-0">
        <h1 className="text-lg font-semibold">WeightAshes</h1>
        <span className="ml-auto text-sm text-gray-400">
          Backend: <span className={backendStatus === 'ok' ? 'text-green-400' : 'text-red-400'}>{backendStatus}</span>
        </span>
      </header>

      {/* Main Content */}
      <div className="flex flex-1 overflow-hidden">
        {/* Left Panel - Manuscript */}
        <aside className="w-64 border-r border-gray-700 p-4 shrink-0">
          <h2 className="text-sm font-medium text-gray-400 uppercase tracking-wide mb-4">Manuscript</h2>
          <p className="text-gray-500 text-sm">Book structure will appear here</p>
        </aside>

        {/* Center Panel - Editor */}
        <main className="flex-1 p-4 flex flex-col overflow-hidden">
          <h2 className="text-sm font-medium text-gray-400 uppercase tracking-wide mb-4">Editor</h2>
          <div className="flex-1 border border-gray-700 rounded p-4">
            <p className="text-gray-500 text-sm">Scene editor will appear here</p>
          </div>
        </main>

        {/* Right Panel - Codex */}
        <aside className="w-72 border-l border-gray-700 p-4 shrink-0">
          <h2 className="text-sm font-medium text-gray-400 uppercase tracking-wide mb-4">Codex</h2>
          <p className="text-gray-500 text-sm">Characters, locations, lore will appear here</p>
        </aside>
      </div>

      {/* Bottom Panel - AI Chat */}
      <footer className="h-48 border-t border-gray-700 p-4 shrink-0">
        <h2 className="text-sm font-medium text-gray-400 uppercase tracking-wide mb-2">AI Chat</h2>
        <div className="h-32 border border-gray-700 rounded p-3">
          <p className="text-gray-500 text-sm">AI conversation will appear here</p>
        </div>
      </footer>
    </div>
  )
}

export default App
