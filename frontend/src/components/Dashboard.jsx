import { useState, useEffect } from 'react'
import axios from 'axios'
import AIChat from './AIChat'

function Dashboard() {
  const [backendMessage, setBackendMessage] = useState('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchHello = async () => {
      try {
        const response = await axios.get('/api/hello')
        setBackendMessage(response.data.message)
      } catch (err) {
        console.error('Error fetching hello message:', err)
        setBackendMessage('Error connecting to backend')
      } finally {
        setLoading(false)
      }
    }

    fetchHello()
  }, [])

  return (
    <div className="min-h-screen">
      <nav className="bg-white shadow-md">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <h1 className="text-2xl font-bold text-primary-600">AI Dashboard</h1>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-white rounded-2xl shadow-xl p-8 mb-8">
          <h2 className="text-3xl font-bold text-gray-800 mb-4">
            Welcome to Your AI-Powered Dashboard
          </h2>
          <div className="bg-primary-50 border border-primary-200 rounded-lg p-4">
            <p className="text-primary-800 font-semibold">
              {loading ? 'Connecting...' : backendMessage}
            </p>
            <p className="text-gray-600 mt-2">
              Backend: FastAPI | Frontend: React + Vite | AI: Code Analyzer + Multi-Language Expert
            </p>
          </div>
        </div>

        <AIChat />
      </main>
    </div>
  )
}

export default Dashboard
