import { useState, useRef, useEffect } from 'react'
import useChatStore from '../../stores/chatStore'
import useCodexStore from '../../stores/codexStore'

export default function ChatPanel() {
  const {
    messages,
    selectedContext,
    loading,
    lastTokens,
    sendMessage,
    removeContextEntry,
  } = useChatStore()
  const { entries } = useCodexStore()
  const [input, setInput] = useState('')
  const messagesEndRef = useRef(null)

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleSubmit = (e) => {
    e.preventDefault()
    if (!input.trim() || loading) return

    sendMessage(input.trim())
    setInput('')
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit(e)
    }
  }

  // Get entry names for context pills
  const getEntryName = (id) => {
    const entry = entries.find(e => e.id === id)
    return entry?.name || id
  }

  return (
    <div className="flex flex-col h-full">
      {/* Context Pills */}
      {selectedContext.length > 0 && (
        <div className="px-4 py-2 border-b border-gray-700 flex flex-wrap gap-2">
          <span className="text-xs text-gray-500 self-center">Context:</span>
          {selectedContext.map(id => (
            <button
              key={id}
              onClick={() => removeContextEntry(id)}
              className="inline-flex items-center gap-1 px-2 py-0.5 bg-blue-900 text-blue-200 text-xs rounded hover:bg-blue-800"
            >
              {getEntryName(id)}
              <span className="text-blue-400">×</span>
            </button>
          ))}
        </div>
      )}

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {messages.length === 0 ? (
          <div className="text-gray-500 text-sm text-center py-4">
            Send a message to start chatting with AI
          </div>
        ) : (
          messages.map((message, i) => (
            <div
              key={i}
              className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-[80%] px-3 py-2 rounded-lg text-sm ${
                  message.role === 'user'
                    ? 'bg-blue-900 text-blue-100'
                    : 'bg-gray-800 text-gray-200'
                }`}
              >
                <div className="whitespace-pre-wrap">{message.content}</div>
              </div>
            </div>
          ))
        )}

        {loading && (
          <div className="flex justify-start">
            <div className="bg-gray-800 text-gray-400 px-3 py-2 rounded-lg text-sm">
              <span className="animate-pulse">Thinking...</span>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Token Count */}
      {lastTokens && (
        <div className="px-4 py-1 text-xs text-gray-500 border-t border-gray-700">
          Last response: {lastTokens.input} input + {lastTokens.output} output tokens
        </div>
      )}

      {/* Input */}
      <form onSubmit={handleSubmit} className="p-3 border-t border-gray-700">
        <div className="flex gap-2">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Describe a scene or ask a question..."
            rows={2}
            className="flex-1 bg-gray-800 text-gray-200 text-sm px-3 py-2 rounded border border-gray-700 resize-none focus:outline-none focus:border-blue-600"
            disabled={loading}
          />
          <button
            type="submit"
            disabled={loading || !input.trim()}
            className="px-4 py-2 bg-blue-600 text-white text-sm rounded hover:bg-blue-700 disabled:bg-gray-700 disabled:text-gray-500 disabled:cursor-not-allowed"
          >
            Send
          </button>
        </div>
      </form>
    </div>
  )
}
