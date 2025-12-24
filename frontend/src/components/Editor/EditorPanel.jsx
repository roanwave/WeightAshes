import { useState, useEffect, useRef, useCallback } from 'react'
import useManuscriptStore from '../../stores/manuscriptStore'

export default function EditorPanel() {
  const { currentScene, loading, saving, updateCurrentScene } = useManuscriptStore()
  const [content, setContent] = useState('')
  const [isDirty, setIsDirty] = useState(false)
  const saveTimeoutRef = useRef(null)

  // Sync content with current scene
  useEffect(() => {
    if (currentScene) {
      setContent(currentScene.content || '')
      setIsDirty(false)
    }
  }, [currentScene])

  // Debounced save
  const debouncedSave = useCallback((newContent) => {
    if (saveTimeoutRef.current) {
      clearTimeout(saveTimeoutRef.current)
    }

    saveTimeoutRef.current = setTimeout(() => {
      updateCurrentScene(newContent)
      setIsDirty(false)
    }, 2000)
  }, [updateCurrentScene])

  // Cleanup timeout on unmount
  useEffect(() => {
    return () => {
      if (saveTimeoutRef.current) {
        clearTimeout(saveTimeoutRef.current)
      }
    }
  }, [])

  const handleChange = (e) => {
    const newContent = e.target.value
    setContent(newContent)
    setIsDirty(true)
    debouncedSave(newContent)
  }

  const handleBlur = () => {
    if (isDirty && saveTimeoutRef.current) {
      clearTimeout(saveTimeoutRef.current)
      updateCurrentScene(content)
      setIsDirty(false)
    }
  }

  // Calculate word count from content
  const wordCount = content
    .replace(/^#+\s+/gm, '')
    .replace(/[*_]{1,2}([^*_]+)[*_]{1,2}/g, '$1')
    .split(/\s+/)
    .filter(word => word.length > 0).length

  if (loading) {
    return (
      <div className="flex-1 flex items-center justify-center text-gray-500">
        Loading scene...
      </div>
    )
  }

  if (!currentScene) {
    return (
      <div className="flex-1 flex items-center justify-center text-gray-500">
        <div className="text-center">
          <p className="text-lg mb-2">No scene selected</p>
          <p className="text-sm">Select a scene from the manuscript panel</p>
        </div>
      </div>
    )
  }

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="p-3 border-b border-gray-700 flex items-center justify-between">
        <div>
          <h2 className="text-lg font-medium text-gray-200">{currentScene.title}</h2>
          {currentScene.pov && (
            <span className="text-sm text-gray-500">POV: {currentScene.pov}</span>
          )}
        </div>
        <div className="text-sm text-gray-500">
          {saving ? (
            <span className="text-yellow-500">Saving...</span>
          ) : isDirty ? (
            <span className="text-gray-400">Unsaved changes</span>
          ) : (
            <span className="text-green-600">Saved</span>
          )}
        </div>
      </div>

      {/* Editor */}
      <div className="flex-1 p-4 overflow-hidden">
        <textarea
          value={content}
          onChange={handleChange}
          onBlur={handleBlur}
          className="w-full h-full bg-gray-800 text-gray-100 p-4 rounded border border-gray-700 resize-none focus:outline-none focus:border-blue-600 font-mono text-sm leading-relaxed"
          placeholder="Start writing..."
          spellCheck="false"
        />
      </div>

      {/* Footer */}
      <div className="px-4 py-2 border-t border-gray-700 flex items-center justify-between text-sm text-gray-500">
        <span>{wordCount} words</span>
        <span className="capitalize">{currentScene.status}</span>
      </div>
    </div>
  )
}
