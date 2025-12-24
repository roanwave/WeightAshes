import Header from './Header'
import ManuscriptPanel from '../Manuscript/ManuscriptPanel'
import EditorPanel from '../Editor/EditorPanel'
import CodexPanel from '../Codex/CodexPanel'
import ChatPanel from '../Chat/ChatPanel'

export default function MainLayout() {
  return (
    <div className="h-screen w-screen bg-gray-900 text-gray-100 flex flex-col">
      <Header />

      <div className="flex flex-1 overflow-hidden">
        {/* Left Panel - Manuscript */}
        <aside className="w-64 border-r border-gray-700 flex flex-col shrink-0 overflow-hidden">
          <ManuscriptPanel />
        </aside>

        {/* Center Panel - Editor */}
        <main className="flex-1 flex flex-col overflow-hidden">
          <EditorPanel />
        </main>

        {/* Right Panel - Codex */}
        <aside className="w-72 border-l border-gray-700 flex flex-col shrink-0 overflow-hidden">
          <CodexPanel />
        </aside>
      </div>

      {/* Bottom Panel - AI Chat */}
      <footer className="h-64 border-t border-gray-700 shrink-0 overflow-hidden">
        <ChatPanel />
      </footer>
    </div>
  )
}
