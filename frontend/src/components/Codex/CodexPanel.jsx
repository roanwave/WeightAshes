import { useEffect, useState } from 'react'
import useCodexStore from '../../stores/codexStore'
import useChatStore from '../../stores/chatStore'
import { searchCodex } from '../../services/api'

const TYPE_LABELS = {
  character: 'Characters',
  location: 'Locations',
  lore: 'Lore',
  object: 'Objects',
  subplot: 'Subplots',
  other: 'Other',
}

const TYPE_ORDER = ['character', 'location', 'lore', 'object', 'subplot', 'other']

export default function CodexPanel() {
  const { entries, selectedEntry, loading, fetchEntries, selectEntry } = useCodexStore()
  const { selectedContext, toggleContextEntry } = useChatStore()
  const [searchQuery, setSearchQuery] = useState('')
  const [searchResults, setSearchResults] = useState(null)
  const [expandedTypes, setExpandedTypes] = useState({ character: true })
  const [expandedEntry, setExpandedEntry] = useState(null)

  useEffect(() => {
    fetchEntries()
  }, [fetchEntries])

  const handleSearch = async (query) => {
    setSearchQuery(query)
    if (query.trim().length > 0) {
      try {
        const results = await searchCodex(query)
        setSearchResults(results)
      } catch {
        setSearchResults([])
      }
    } else {
      setSearchResults(null)
    }
  }

  const toggleType = (type) => {
    setExpandedTypes(prev => ({ ...prev, [type]: !prev[type] }))
  }

  const toggleEntryExpand = async (entryId) => {
    if (expandedEntry === entryId) {
      setExpandedEntry(null)
    } else {
      await selectEntry(entryId)
      setExpandedEntry(entryId)
    }
  }

  // Group entries by type
  const entriesByType = {}
  const entriesToShow = searchResults ?? entries

  entriesToShow.forEach(entry => {
    if (!entriesByType[entry.type]) {
      entriesByType[entry.type] = []
    }
    entriesByType[entry.type].push(entry)
  })

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="p-3 border-b border-gray-700">
        <h2 className="text-sm font-medium text-gray-400 uppercase tracking-wide mb-2">
          Codex
        </h2>
        <input
          type="text"
          value={searchQuery}
          onChange={(e) => handleSearch(e.target.value)}
          placeholder="Search entries..."
          className="w-full bg-gray-800 text-gray-200 text-sm px-3 py-1.5 rounded border border-gray-700 focus:outline-none focus:border-blue-600"
        />
      </div>

      {/* Entry List */}
      <div className="flex-1 overflow-y-auto p-2">
        {loading && entries.length === 0 ? (
          <div className="text-gray-500 text-sm p-2">Loading codex...</div>
        ) : entriesToShow.length === 0 ? (
          <div className="text-gray-500 text-sm p-2">
            {searchQuery ? 'No results found' : 'No codex entries'}
          </div>
        ) : (
          TYPE_ORDER.map(type => {
            const typeEntries = entriesByType[type]
            if (!typeEntries?.length) return null

            return (
              <div key={type} className="mb-2">
                {/* Type Header */}
                <button
                  onClick={() => toggleType(type)}
                  className="flex items-center gap-1 w-full text-left px-2 py-1 text-sm font-medium text-gray-400 hover:bg-gray-800 rounded"
                >
                  <span className="text-gray-500">
                    {expandedTypes[type] ? '▼' : '▶'}
                  </span>
                  <span>{TYPE_LABELS[type] || type}</span>
                  <span className="text-gray-600 ml-1">({typeEntries.length})</span>
                </button>

                {/* Entries */}
                {expandedTypes[type] && (
                  <div className="ml-3">
                    {typeEntries.map(entry => (
                      <div key={entry.id} className="mb-1">
                        <div className="flex items-center gap-2 px-2 py-1 hover:bg-gray-800 rounded">
                          {/* Context Checkbox */}
                          <input
                            type="checkbox"
                            checked={selectedContext.includes(entry.id)}
                            onChange={() => toggleContextEntry(entry.id)}
                            className="w-4 h-4 rounded border-gray-600 bg-gray-700 text-blue-600 focus:ring-blue-500 focus:ring-offset-gray-900"
                          />

                          {/* Entry Name */}
                          <button
                            onClick={() => toggleEntryExpand(entry.id)}
                            className="flex-1 text-left text-sm text-gray-300 hover:text-gray-100"
                          >
                            {entry.name}
                          </button>
                        </div>

                        {/* Tags */}
                        {entry.tags?.length > 0 && (
                          <div className="flex flex-wrap gap-1 ml-8 mb-1">
                            {entry.tags.slice(0, 3).map(tag => (
                              <span
                                key={tag}
                                className="text-xs px-1.5 py-0.5 bg-gray-800 text-gray-500 rounded"
                              >
                                {tag}
                              </span>
                            ))}
                          </div>
                        )}

                        {/* Expanded Description */}
                        {expandedEntry === entry.id && selectedEntry && (
                          <div className="ml-8 mr-2 mt-1 p-2 bg-gray-800 rounded text-sm text-gray-400 border-l-2 border-blue-600">
                            <div className="prose prose-sm prose-invert max-w-none">
                              {selectedEntry.description?.split('\n').map((line, i) => (
                                <p key={i} className="mb-1">{line}</p>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )
          })
        )}
      </div>
    </div>
  )
}
