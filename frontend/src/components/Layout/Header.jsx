import { useState, useEffect } from 'react'
import { healthCheck } from '../../services/api'

export default function Header() {
  const [connected, setConnected] = useState(false)

  useEffect(() => {
    const checkConnection = async () => {
      try {
        await healthCheck()
        setConnected(true)
      } catch {
        setConnected(false)
      }
    }

    checkConnection()
    const interval = setInterval(checkConnection, 30000)
    return () => clearInterval(interval)
  }, [])

  return (
    <header className="h-12 bg-gray-800 border-b border-gray-700 flex items-center px-4 shrink-0">
      <h1 className="text-lg font-semibold text-gray-100">WeightAshes</h1>

      <div className="ml-auto flex items-center gap-2">
        <span className="text-sm text-gray-400">Backend:</span>
        <span
          className={`w-2.5 h-2.5 rounded-full ${
            connected ? 'bg-green-500' : 'bg-red-500'
          }`}
          title={connected ? 'Connected' : 'Disconnected'}
        />
      </div>
    </header>
  )
}
