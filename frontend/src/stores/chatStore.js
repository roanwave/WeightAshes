import { create } from 'zustand'
import { sendChat } from '../services/api'

const useChatStore = create((set, get) => ({
  messages: [],
  selectedContext: [],
  loading: false,
  error: null,
  lastTokens: null,

  sendMessage: async (text) => {
    const { selectedContext, messages } = get()

    // Add user message
    const userMessage = { role: 'user', content: text }
    set({
      messages: [...messages, userMessage],
      loading: true,
      error: null,
    })

    try {
      const response = await sendChat(text, selectedContext)
      const assistantMessage = { role: 'assistant', content: response.response }

      set(state => ({
        messages: [...state.messages, assistantMessage],
        loading: false,
        lastTokens: response.tokens_used,
      }))
    } catch (error) {
      set({ error: error.message, loading: false })
    }
  },

  toggleContextEntry: (id) => {
    set(state => {
      const { selectedContext } = state
      if (selectedContext.includes(id)) {
        return { selectedContext: selectedContext.filter(x => x !== id) }
      } else {
        return { selectedContext: [...selectedContext, id] }
      }
    })
  },

  removeContextEntry: (id) => {
    set(state => ({
      selectedContext: state.selectedContext.filter(x => x !== id)
    }))
  },

  clearChat: () => {
    set({ messages: [], lastTokens: null })
  },

  clearContext: () => {
    set({ selectedContext: [] })
  },
}))

export default useChatStore
