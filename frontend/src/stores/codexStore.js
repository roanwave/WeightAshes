import { create } from 'zustand'
import { getCodexEntries, getCodexEntry } from '../services/api'

const useCodexStore = create((set, get) => ({
  entries: [],
  selectedEntry: null,
  loading: false,
  error: null,

  fetchEntries: async (type = null) => {
    set({ loading: true, error: null })
    try {
      const entries = await getCodexEntries(type)
      set({ entries, loading: false })
    } catch (error) {
      set({ error: error.message, loading: false })
    }
  },

  selectEntry: async (id) => {
    if (!id) {
      set({ selectedEntry: null })
      return
    }

    set({ loading: true, error: null })
    try {
      const entry = await getCodexEntry(id)
      set({ selectedEntry: entry, loading: false })
    } catch (error) {
      set({ error: error.message, loading: false })
    }
  },

  clearSelection: () => {
    set({ selectedEntry: null })
  },

  // Get entries grouped by type
  getEntriesByType: () => {
    const { entries } = get()
    const grouped = {}

    entries.forEach(entry => {
      const type = entry.type
      if (!grouped[type]) {
        grouped[type] = []
      }
      grouped[type].push(entry)
    })

    return grouped
  },
}))

export default useCodexStore
