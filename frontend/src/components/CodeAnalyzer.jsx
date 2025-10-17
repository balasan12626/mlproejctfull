import { useState, useRef, useEffect } from 'react'
import axios from 'axios'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism'

export default function CodeAnalyzer({ darkMode }) {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const messagesEndRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text)
  }

  const parseCodeBlocks = (text) => {
    const codeBlockRegex = /```(\w+)?\n([\s\S]*?)```/g
    const parts = []
    let lastIndex = 0
    let match

    while ((match = codeBlockRegex.exec(text)) !== null) {
      if (match.index > lastIndex) {
        parts.push({
          type: 'text',
          content: text.substring(lastIndex, match.index)
        })
      }
      
      parts.push({
        type: 'code',
        language: match[1] || 'python',
        content: match[2].trim()
      })
      
      lastIndex = match.index + match[0].length
    }

    if (lastIndex < text.length) {
      parts.push({
        type: 'text',
        content: text.substring(lastIndex)
      })
    }

    return parts.length > 0 ? parts : [{ type: 'text', content: text }]
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!input.trim() || loading) return

    const userMessage = input.trim()
    setInput('')
    setMessages(prev => [...prev, { role: 'user', content: userMessage }])
    setLoading(true)

    try {
      const response = await axios.post('/api/ai/generate', {
        prompt: userMessage
      })
      
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: response.data.response,
        model: response.data.model
      }])
    } catch (error) {
      setMessages(prev => [...prev, {
        role: 'error',
        content: error.response?.data?.detail || 'Failed to get response'
      }])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex flex-col h-full max-w-5xl mx-auto px-4">
      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto py-6 space-y-6">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center">
            <div className="max-w-2xl space-y-4">
              <h2 className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                AI Code Analyzer
              </h2>
              <p className="text-gray-600 dark:text-gray-400">
                Paste your Python code to get:
              </p>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm text-left">
                <div className="p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                  ✓ Code execution output
                </div>
                <div className="p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                  ✓ Quality rating (X/10)
                </div>
                <div className="p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                  ✓ Percentage score (X%)
                </div>
                <div className="p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                  ✓ 10 logic variations
                </div>
              </div>
            </div>
          </div>
        ) : (
          messages.map((message, index) => (
            <div key={index} className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-4xl w-full ${message.role === 'user' ? 'flex justify-end' : ''}`}>
                <div className={`rounded-2xl p-4 ${
                  message.role === 'user'
                    ? 'bg-blue-600 text-white'
                    : message.role === 'error'
                    ? 'bg-red-100 dark:bg-red-900/20 text-red-800 dark:text-red-200'
                    : 'bg-gray-50 dark:bg-gray-800'
                }`}>
                  {message.role === 'assistant' ? (
                    <div className="space-y-3">
                      {message.model && (
                        <div className="text-xs text-gray-500 dark:text-gray-400 mb-2">
                          {message.model}
                        </div>
                      )}
                      {parseCodeBlocks(message.content).map((part, i) => (
                        part.type === 'code' ? (
                          <div key={i} className="relative group">
                            <button
                              onClick={() => copyToClipboard(part.content)}
                              className="absolute right-2 top-2 p-2 bg-gray-700 hover:bg-gray-600 text-white rounded-lg opacity-0 group-hover:opacity-100 transition-opacity text-xs"
                            >
                              Copy
                            </button>
                            <SyntaxHighlighter
                              language={part.language}
                              style={vscDarkPlus}
                              customStyle={{
                                margin: 0,
                                borderRadius: '0.5rem',
                                fontSize: '0.875rem'
                              }}
                            >
                              {part.content}
                            </SyntaxHighlighter>
                          </div>
                        ) : (
                          <div key={i} className="whitespace-pre-wrap">
                            {part.content}
                          </div>
                        )
                      ))}
                    </div>
                  ) : (
                    <div className="whitespace-pre-wrap">{message.content}</div>
                  )}
                </div>
              </div>
            </div>
          ))
        )}
        
        {loading && (
          <div className="flex justify-start">
            <div className="bg-gray-50 dark:bg-gray-800 rounded-2xl p-4">
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="border-t border-gray-200 dark:border-gray-800 py-4">
        <form onSubmit={handleSubmit} className="flex space-x-3">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault()
                handleSubmit(e)
              }
            }}
            placeholder="Paste your Python code here..."
            className="flex-1 resize-none rounded-xl border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400"
            rows={3}
            disabled={loading}
          />
          <button
            type="submit"
            disabled={loading || !input.trim()}
            className="px-6 py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed text-white rounded-xl font-medium transition-colors"
          >
            {loading ? 'Analyzing...' : 'Send'}
          </button>
        </form>
      </div>
    </div>
  )
}
