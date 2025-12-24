import { create } from 'zustand'
import { getManuscriptStructure, getScene, updateScene } from '../services/api'

const useManuscriptStore = create((set, get) => ({
  structure: null,
  currentScene: null,
  currentPath: null,
  loading: false,
  saving: false,
  error: null,

  fetchStructure: async () => {
    set({ loading: true, error: null })
    try {
      const structure = await getManuscriptStructure()
      set({ structure, loading: false })
    } catch (error) {
      set({ error: error.message, loading: false })
    }
  },

  loadScene: async (book, act, chapter, scene) => {
    set({ loading: true, error: null })
    try {
      const sceneData = await getScene(book, act, chapter, scene)
      set({
        currentScene: sceneData,
        currentPath: { book, act, chapter, scene },
        loading: false,
      })
    } catch (error) {
      set({ error: error.message, loading: false })
    }
  },

  updateCurrentScene: async (content) => {
    const { currentPath, currentScene } = get()
    if (!currentPath || !currentScene) return

    set({ saving: true })
    try {
      const updated = await updateScene(
        currentPath.book,
        currentPath.act,
        currentPath.chapter,
        currentPath.scene,
        { content }
      )
      set({ currentScene: updated, saving: false })
    } catch (error) {
      set({ error: error.message, saving: false })
    }
  },

  clearScene: () => {
    set({ currentScene: null, currentPath: null })
  },
}))

export default useManuscriptStore
