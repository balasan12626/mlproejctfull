import { useState } from 'react'
import axios from 'axios'

function AIChat() {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!input.trim()) return

    const userMessage = { role: 'user', content: input }
    setMessages(prev => [...prev, userMessage])
    setInput('')
    setLoading(true)

    try {
      const response = await axios.post('/api/ai/generate', { prompt: input })

      const aiMessage = {
        role: 'assistant',
        content: response.data.response,
        model: response.data.model
      }
      setMessages(prev => [...prev, aiMessage])
    } catch (err) {
      const errorMessage = {
        role: 'error',
        content: err.response?.data?.detail || 'Failed to get AI response'
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="bg-white rounded-2xl shadow-xl overflow-hidden">
      <div className="bg-gradient-to-r from-primary-600 to-indigo-600 p-6">
        <h2 className="text-2xl font-bold text-white">AI Chat Assistant</h2>
        <p className="text-primary-100">Powered by Gemini 2.5 Flash</p>
      </div>

      <div className="p-6">
        <div className="h-96 overflow-y-auto mb-4 space-y-4 bg-gray-50 rounded-lg p-4">
          {messages.length === 0 ? (
            <div className="flex items-center justify-center h-full">
              <p className="text-gray-500 text-center">
                Start a conversation with the AI assistant.
                <br />
                Ask anything and get intelligent responses!
              </p>
            </div>
          ) : (
            messages.map((message, index) => (
              <div
                key={index}
                className={`flex ${
                  message.role === 'user' ? 'justify-end' : 'justify-start'
                }`}
              >
                <div
                  className={`max-w-xs lg:max-w-md xl:max-w-lg px-4 py-3 rounded-2xl ${
                    message.role === 'user'
                      ? 'bg-primary-600 text-white'
                      : message.role === 'error'
                      ? 'bg-red-100 text-red-800 border border-red-300'
                      : 'bg-white text-gray-800 shadow-md'
                  }`}
                >
                  {message.role === 'assistant' && (
                    <p className="text-xs text-gray-500 mb-1">{message.model}</p>
                  )}
                  <p className="whitespace-pre-wrap">{message.content}</p>
                </div>
              </div>
            ))
          )}
          {loading && (
            <div className="flex justify-start">
              <div className="bg-white text-gray-800 shadow-md px-4 py-3 rounded-2xl">
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-primary-600 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-primary-600 rounded-full animate-bounce delay-100"></div>
                  <div className="w-2 h-2 bg-primary-600 rounded-full animate-bounce delay-200"></div>
                </div>
              </div>
            </div>
          )}
        </div>

        <form onSubmit={handleSubmit} className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask me anything..."
            className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none"
            disabled={loading}
          />
          <button
            type="submit"
            disabled={loading || !input.trim()}
            className="bg-primary-600 hover:bg-primary-700 text-white px-6 py-3 rounded-lg font-semibold transition duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Send
          </button>
        </form>
      </div>
    </div>
  )
}

export default AIChat
