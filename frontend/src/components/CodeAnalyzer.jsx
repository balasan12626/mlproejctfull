import { useState, useRef, useEffect } from 'react'
import axios from 'axios'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism'
import ReactMarkdown from 'react-markdown'

export default function CodeAnalyzer({ darkMode }) {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [sourceLanguage, setSourceLanguage] = useState('python')
  const [numVariations, setNumVariations] = useState(10)
  const [targetLanguages, setTargetLanguages] = useState([])
  const messagesEndRef = useRef(null)

  const programmingLanguages = [
    { value: 'python', label: 'Python' },
    { value: 'javascript', label: 'JavaScript' },
    { value: 'java', label: 'Java' },
    { value: 'cpp', label: 'C++' },
    { value: 'c', label: 'C' },
    { value: 'csharp', label: 'C#' },
    { value: 'go', label: 'Go' },
    { value: 'rust', label: 'Rust' },
    { value: 'kotlin', label: 'Kotlin' },
    { value: 'swift', label: 'Swift' },
    { value: 'ruby', label: 'Ruby' },
    { value: 'php', label: 'PHP' },
    { value: 'typescript', label: 'TypeScript' },
    { value: 'react', label: 'React' },
    { value: 'angular', label: 'Angular' }
  ]

  const availableTargetLanguages = programmingLanguages.filter(lang => lang.value !== sourceLanguage)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  useEffect(() => {
    setTargetLanguages(prev => prev.filter(lang => lang !== sourceLanguage))
  }, [sourceLanguage])

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text)
  }

  const handleTargetLanguageToggle = (langValue) => {
    setTargetLanguages(prev => 
      prev.includes(langValue)
        ? prev.filter(l => l !== langValue)
        : [...prev, langValue]
    )
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!input.trim() || loading) return

    const userMessage = input.trim()
    const userSettings = {
      sourceLanguage,
      numVariations,
      targetLanguages
    }
    
    setInput('')
    setMessages(prev => [...prev, { 
      role: 'user', 
      content: userMessage,
      settings: userSettings
    }])
    setLoading(true)

    try {
      const response = await axios.post('/api/ai/generate', {
        prompt: userMessage,
        source_language: sourceLanguage,
        num_variations: numVariations,
        target_languages: targetLanguages
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
    <div className="flex flex-col h-full max-w-5xl mx-auto px-2 sm:px-4 md:px-6">
      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto py-3 sm:py-6 space-y-4 sm:space-y-6">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center">
            <div className="max-w-2xl space-y-3 sm:space-y-4 px-2">
              <h2 className="text-2xl sm:text-3xl lg:text-4xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                CodeMaster AI
              </h2>
              <p className="text-sm sm:text-base text-gray-600 dark:text-gray-400">
                Analyze, optimize, and translate your code instantly
              </p>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 sm:gap-3 text-xs sm:text-sm text-left">
                <div className="p-2 sm:p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                  ✓ Code execution output
                </div>
                <div className="p-2 sm:p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                  ✓ Quality rating (X/10)
                </div>
                <div className="p-2 sm:p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                  ✓ Percentage score (X%)
                </div>
                <div className="p-2 sm:p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                  ✓ Multiple code variations
                </div>
              </div>
            </div>
          </div>
        ) : (
          messages.map((message, index) => (
            <div key={index} className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'} px-1 sm:px-0`}>
              <div className={`max-w-4xl w-full ${message.role === 'user' ? 'flex justify-end' : ''}`}>
                <div className={`rounded-xl sm:rounded-2xl p-3 sm:p-4 ${
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
                      <div className="prose prose-sm dark:prose-invert max-w-none">
                        <ReactMarkdown
                          components={{
                            code({node, inline, className, children, ...props}) {
                              const match = /language-(\w+)/.exec(className || '')
                              const codeString = String(children).replace(/\n$/, '')
                              
                              return !inline && match ? (
                                <div className="relative group my-4">
                                  <button
                                    onClick={() => copyToClipboard(codeString)}
                                    className="absolute right-2 top-2 p-2 bg-gray-700 hover:bg-gray-600 text-white rounded-lg opacity-0 group-hover:opacity-100 transition-opacity text-xs z-10"
                                  >
                                    Copy
                                  </button>
                                  <SyntaxHighlighter
                                    language={match[1]}
                                    style={vscDarkPlus}
                                    customStyle={{
                                      margin: 0,
                                      borderRadius: '0.5rem',
                                      fontSize: '0.875rem'
                                    }}
                                    {...props}
                                  >
                                    {codeString}
                                  </SyntaxHighlighter>
                                </div>
                              ) : (
                                <code className="bg-gray-200 dark:bg-gray-700 px-1 py-0.5 rounded text-sm" {...props}>
                                  {children}
                                </code>
                              )
                            },
                            h1: ({children}) => <h1 className="text-2xl font-bold mt-6 mb-3">{children}</h1>,
                            h2: ({children}) => <h2 className="text-xl font-bold mt-5 mb-2">{children}</h2>,
                            h3: ({children}) => <h3 className="text-lg font-semibold mt-4 mb-2">{children}</h3>,
                            h4: ({children}) => <h4 className="text-base font-semibold mt-3 mb-2">{children}</h4>,
                            ul: ({children}) => <ul className="list-disc list-inside space-y-1 my-2">{children}</ul>,
                            ol: ({children}) => <ol className="list-decimal list-inside space-y-1 my-2">{children}</ol>,
                            li: ({children}) => <li className="ml-4">{children}</li>,
                            p: ({children}) => <p className="mb-2">{children}</p>,
                            strong: ({children}) => <strong className="font-semibold">{children}</strong>,
                            em: ({children}) => <em className="italic">{children}</em>,
                            hr: () => <hr className="my-4 border-gray-300 dark:border-gray-700" />,
                          }}
                        >
                          {message.content}
                        </ReactMarkdown>
                      </div>
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
      <div className="border-t border-gray-200 dark:border-gray-800 py-2 sm:py-4 space-y-2 sm:space-y-3">
        {/* Configuration Controls */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2 sm:gap-3">
          {/* Source Language */}
          <div>
            <label className="block text-xs sm:text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">
              Source Language
            </label>
            <select
              value={sourceLanguage}
              onChange={(e) => setSourceLanguage(e.target.value)}
              className="w-full rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 px-2 sm:px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              disabled={loading}
            >
              {programmingLanguages.map(lang => (
                <option key={lang.value} value={lang.value}>{lang.label}</option>
              ))}
            </select>
          </div>

          {/* Number of Variations */}
          <div>
            <label className="block text-xs sm:text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">
              Number of Variations
            </label>
            <input
              type="number"
              min="1"
              max="20"
              value={numVariations}
              onChange={(e) => setNumVariations(parseInt(e.target.value) || 10)}
              className="w-full rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 px-2 sm:px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              disabled={loading}
            />
          </div>

          {/* Target Languages */}
          <div className="sm:col-span-2 lg:col-span-1">
            <label className="block text-xs sm:text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">
              Translate To ({targetLanguages.length} selected)
            </label>
            <div className="relative">
              <details className="w-full">
                <summary className="cursor-pointer rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 px-2 sm:px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
                  Select Languages...
                </summary>
                <div className="absolute z-10 mt-1 w-full max-h-48 overflow-auto rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 shadow-lg">
                  {availableTargetLanguages.map(lang => (
                    <label
                      key={lang.value}
                      className="flex items-center px-2 sm:px-3 py-2 hover:bg-gray-100 dark:hover:bg-gray-700 cursor-pointer text-sm"
                    >
                      <input
                        type="checkbox"
                        checked={targetLanguages.includes(lang.value)}
                        onChange={() => handleTargetLanguageToggle(lang.value)}
                        className="mr-2"
                      />
                      {lang.label}
                    </label>
                  ))}
                </div>
              </details>
            </div>
          </div>
        </div>

        {/* Code Input and Submit */}
        <form onSubmit={handleSubmit} className="flex flex-col sm:flex-row gap-2 sm:gap-3">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey && window.innerWidth > 640) {
                e.preventDefault()
                handleSubmit(e)
              }
            }}
            placeholder={`Paste your ${programmingLanguages.find(l => l.value === sourceLanguage)?.label || 'code'} here...`}
            className="flex-1 resize-none rounded-lg sm:rounded-xl border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 px-3 sm:px-4 py-2 sm:py-3 text-sm sm:text-base focus:outline-none focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400"
            rows={3}
            disabled={loading}
          />
          <button
            type="submit"
            disabled={loading || !input.trim()}
            className="px-4 sm:px-6 py-2 sm:py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed text-white rounded-lg sm:rounded-xl font-medium transition-colors text-sm sm:text-base whitespace-nowrap"
          >
            {loading ? 'Analyzing...' : 'Analyze'}
          </button>
        </form>
      </div>
    </div>
  )
}
