'use client';

import { useState, useEffect, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { isTokenValid } from '@/lib/auth';
import { chatAPI } from '@/lib/api';
import { formatDateTime } from '@/lib/utils';
import AppShell from '@/components/layout/AppShell';

import LoadingSpinner from '@/components/common/LoadingSpinner';
import { FaPaperPlane, FaRobot, FaUser, FaTrash } from 'react-icons/fa';
import toast from 'react-hot-toast';

export default function Chat() {
  const router = useRouter();
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [initialLoading, setInitialLoading] = useState(true);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    if (!isTokenValid()) {
      router.push('/login');
      return;
    }
    fetchHistory();
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const fetchHistory = async () => {
    try {
      const response = await chatAPI.getHistory();
      const history = response.data.map((msg) => [
        { role: 'user', content: msg.message, timestamp: msg.created_at },
        { role: 'assistant', content: msg.response, timestamp: msg.created_at },
      ]).flat();
      setMessages(history);
    } catch (error) {
      console.error('Failed to fetch chat history:', error);
    } finally {
      setInitialLoading(false);
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMessage = { role: 'user', content: input, timestamp: new Date().toISOString() };
    setMessages([...messages, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await chatAPI.sendMessage({ message: input });
      const assistantMessage = {
        role: 'assistant',
        content: response.data.response,
        timestamp: response.data.created_at,
      };
      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      toast.error('Failed to send message');
      setMessages((prev) => prev.slice(0, -1)); // Remove user message on error
    } finally {
      setLoading(false);
    }
  };

  const handleClearHistory = async () => {
    if (!confirm('Are you sure you want to clear chat history?')) return;

    try {
      await chatAPI.clearHistory();
      setMessages([]);
      toast.success('Chat history cleared');
    } catch (error) {
      toast.error('Failed to clear history');
    }
  };

  const suggestedQuestions = [
    'Analyze my portfolio performance',
    'What are the risks in my portfolio?',
    'Should I rebalance my portfolio?',
    'What stocks are trending today?',
    'Give me investment recommendations',
  ];

  if (initialLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <LoadingSpinner text="Loading chat..." />
      </div>
    );
  }

  return (
    <AppShell>
      <main className="flex flex-col min-h-[calc(100vh-120px)]">
        {/* Header */}
        <div className="p-6 border-b border-dark-700">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold mb-2">AI Financial Assistant</h1>
              <p className="text-gray-400">Ask me anything about your portfolio or the market</p>
            </div>
            <button
              onClick={handleClearHistory}
              className="flex items-center gap-2 px-4 py-2 bg-red-500/10 text-red-500 hover:bg-red-500/20 rounded-lg transition"
            >
              <FaTrash /> Clear History
            </button>
          </div>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          {messages.length === 0 && (
            <div className="text-center py-12">
              <FaRobot className="text-6xl text-primary-500 mx-auto mb-4" />
              <h2 className="text-2xl font-bold mb-4">Welcome to AI Assistant</h2>
              <p className="text-gray-400 mb-6">
                I'm your AI-powered financial advisor. Ask me questions about your portfolio,
                market trends, or investment strategies.
              </p>
              <div className="max-w-2xl mx-auto">
                <p className="text-sm text-gray-500 mb-3">Try asking:</p>
                <div className="grid gap-2">
                  {suggestedQuestions.map((question, index) => (
                    <button
                      key={index}
                      onClick={() => setInput(question)}
                      className="px-4 py-3 bg-dark-800 hover:bg-dark-700 border border-dark-600 rounded-lg text-left transition"
                    >
                      {question}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          )}

          {messages.map((message, index) => (
            <MessageBubble key={index} message={message} />
          ))}

          {loading && (
            <div className="flex items-start gap-3">
              <div className="w-10 h-10 bg-primary-600 rounded-full flex items-center justify-center flex-shrink-0">
                <FaRobot />
              </div>
              <div className="flex-1 bg-dark-800 rounded-lg p-4 border border-dark-700">
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-primary-500 rounded-full animate-pulse"></div>
                  <div className="w-2 h-2 bg-primary-500 rounded-full animate-pulse delay-75"></div>
                  <div className="w-2 h-2 bg-primary-500 rounded-full animate-pulse delay-150"></div>
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <div className="p-6 border-t border-dark-700">
          <form onSubmit={handleSubmit} className="flex gap-3">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask a question..."
              className="flex-1 px-4 py-3 bg-dark-800 border border-dark-600 rounded-lg focus:outline-none focus:border-primary-500"
              disabled={loading}
            />
            <button
              type="submit"
              disabled={loading || !input.trim()}
              className="px-6 py-3 bg-primary-600 hover:bg-primary-700 disabled:bg-dark-600 rounded-lg font-semibold transition flex items-center gap-2"
            >
              <FaPaperPlane /> Send
            </button>
          </form>
        </div>
      </main>
    </AppShell>
  );
}

function MessageBubble({ message }) {
  const isUser = message.role === 'user';

  return (
    <div className={`flex items-start gap-3 ${isUser ? 'flex-row-reverse' : ''}`}>
      <div
        className={`w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0 ${
          isUser ? 'bg-green-600' : 'bg-primary-600'
        }`}
      >
        {isUser ? <FaUser /> : <FaRobot />}
      </div>
      <div className={`flex-1 max-w-3xl ${isUser ? 'flex flex-col items-end' : ''}`}>
        <div
          className={`rounded-lg p-4 ${
            isUser
              ? 'bg-green-600/20 border border-green-600/30'
              : 'bg-dark-800 border border-dark-700'
          }`}
        >
          <p className="whitespace-pre-wrap">{message.content}</p>
        </div>
        {message.timestamp && (
          <p className="text-xs text-gray-500 mt-1">{formatDateTime(message.timestamp)}</p>
        )}
      </div>
    </div>
  );
}