import { useEffect, useState } from 'react'
import useManuscriptStore from '../../stores/manuscriptStore'
import { createScene } from '../../services/api'

export default function ManuscriptPanel() {
  const { structure, currentPath, loading, fetchStructure, loadScene } = useManuscriptStore()
  const [expanded, setExpanded] = useState({})

  useEffect(() => {
    fetchStructure()
  }, [fetchStructure])

  const toggleExpand = (key) => {
    setExpanded(prev => ({ ...prev, [key]: !prev[key] }))
  }

  const handleSceneClick = (book, act, chapter, scene) => {
    loadScene(book, act, chapter, scene)
  }

  const handleAddScene = async (book, act, chapter) => {
    const title = prompt('Enter scene title:')
    if (!title) return

    try {
      await createScene(book, act, chapter, { title, content: `# ${title}\n\n` })
      fetchStructure()
    } catch (error) {
      console.error('Failed to create scene:', error)
    }
  }

  const isSelected = (book, act, chapter, scene) => {
    return currentPath?.book === book &&
           currentPath?.act === act &&
           currentPath?.chapter === chapter &&
           currentPath?.scene === scene
  }

  if (loading && !structure) {
    return (
      <div className="p-4 text-gray-500 text-sm">
        Loading manuscript...
      </div>
    )
  }

  if (!structure?.books?.length) {
    return (
      <div className="p-4 text-gray-500 text-sm">
        No manuscript found
      </div>
    )
  }

  return (
    <div className="flex flex-col h-full">
      <div className="p-3 border-b border-gray-700">
        <h2 className="text-sm font-medium text-gray-400 uppercase tracking-wide">
          Manuscript
        </h2>
      </div>

      <div className="flex-1 overflow-y-auto p-2">
        {structure.books.map(book => (
          <div key={book.id} className="mb-2">
            {/* Book */}
            <button
              onClick={() => toggleExpand(book.id)}
              className="flex items-center gap-1 w-full text-left px-2 py-1 text-sm text-gray-300 hover:bg-gray-800 rounded"
            >
              <span className="text-gray-500">{expanded[book.id] ? '▼' : '▶'}</span>
              <span className="font-medium">{book.title}</span>
            </button>

            {expanded[book.id] && book.acts.map(act => (
              <div key={act.id} className="ml-3">
                {/* Act */}
                <button
                  onClick={() => toggleExpand(`${book.id}/${act.id}`)}
                  className="flex items-center gap-1 w-full text-left px-2 py-1 text-sm text-gray-400 hover:bg-gray-800 rounded"
                >
                  <span className="text-gray-600">{expanded[`${book.id}/${act.id}`] ? '▼' : '▶'}</span>
                  <span>{act.title}</span>
                </button>

                {expanded[`${book.id}/${act.id}`] && act.chapters.map(chapter => (
                  <div key={chapter.id} className="ml-3">
                    {/* Chapter */}
                    <button
                      onClick={() => toggleExpand(`${book.id}/${act.id}/${chapter.id}`)}
                      className="flex items-center gap-1 w-full text-left px-2 py-1 text-sm text-gray-400 hover:bg-gray-800 rounded"
                    >
                      <span className="text-gray-600">
                        {expanded[`${book.id}/${act.id}/${chapter.id}`] ? '▼' : '▶'}
                      </span>
                      <span>{chapter.title}</span>
                    </button>

                    {expanded[`${book.id}/${act.id}/${chapter.id}`] && (
                      <div className="ml-3">
                        {/* Scenes */}
                        {chapter.scenes.map(scene => (
                          <button
                            key={scene.id}
                            onClick={() => handleSceneClick(book.id, act.id, chapter.id, scene.id)}
                            className={`flex items-center gap-1 w-full text-left px-2 py-1 text-sm rounded ${
                              isSelected(book.id, act.id, chapter.id, scene.id)
                                ? 'bg-blue-900 text-blue-200'
                                : 'text-gray-400 hover:bg-gray-800'
                            }`}
                          >
                            <span className="text-gray-600">○</span>
                            <span>{scene.title}</span>
                          </button>
                        ))}

                        {/* Add Scene Button */}
                        <button
                          onClick={() => handleAddScene(book.id, act.id, chapter.id)}
                          className="flex items-center gap-1 w-full text-left px-2 py-1 text-sm text-gray-600 hover:text-gray-400 hover:bg-gray-800 rounded"
                        >
                          <span>+</span>
                          <span>Add scene</span>
                        </button>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            ))}
          </div>
        ))}
      </div>
    </div>
  )
}
