'use client'

import React, { useState, useRef, useEffect } from 'react'
import { Message } from './types'
import ChatMessage from './components/CharMessage'

export default function App() {
    const [input, setInput] = useState('')
    const [messages, setMessages] = useState<Message[]>([])
    const [isLoading, setIsLoading] = useState(false)

    const bottomRef = useRef<HTMLDivElement>(null)

    useEffect(() => {
        bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
    }, [messages, isLoading])

    const handleSend = async (e: React.FormEvent) => {
        e.preventDefault()
        if (!input.trim() || isLoading) return

        const userMsg: Message = { role: 'user', content: input }
        setMessages(prev => [...prev, userMsg])
        setInput('')
        setIsLoading(true)

        try {
            // 创建 AI 占位符
            const aiMsgPlaceholder: Message = {
                role: 'assistant',
                content: '',
                thoughts: '',
                traceLogs: [],
                tableData: undefined,
                chartData: undefined,
            }
            setMessages(prev => [...prev, aiMsgPlaceholder])

            const historyToSend = [...messages, userMsg].map(m => ({
                role: m.role,
                content: m.content,
            }))

            const response = await fetch(
                'http://10.192.128.153:927/api/rag/chat',
                {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ messages: historyToSend }),
                }
            )

            if (!response.ok) throw new Error(response.statusText)
            if (!response.body) throw new Error('No response body')

            const reader = response.body.getReader()
            const decoder = new TextDecoder()
            let done = false
            let buffer = ''

            while (!done) {
                const { value, done: doneReading } = await reader.read()
                done = doneReading
                const chunk = decoder.decode(value, { stream: true })
                buffer += chunk
                const parts = buffer.split('\n\n')
                buffer = parts.pop() || ''

                for (const part of parts) {
                    const line = part.trim()
                    if (!line.startsWith('data: ')) continue
                    const jsonStr = line.replace('data: ', '').trim()
                    if (jsonStr === '[DONE]') break

                    try {
                        const data = JSON.parse(jsonStr)

                        setMessages(prev => {
                            const newMsgs = [...prev]
                            const lastMsg = {...newMsgs[newMsgs.length - 1]}

                            // A. 文本追加 (保持不变)
                            if (data.type === 'text') {
                                lastMsg.content += data.content
                            }
                            // B. 思考过程 (保持不变)
                            else if (data.type === 'thought') {
                                lastMsg.thoughts =
                                    (lastMsg.thoughts || '') + data.content
                            }
                            // C. 表格数据 (🔥 修复：覆盖而不是追加)
                            else if (data.type === 'table') {
                                lastMsg.tableData = data.data
                            }
                            // D. 图表数据 (🔥 修复：覆盖)
                            else if (data.type === 'chart') {
                                lastMsg.chartData = data.data
                                lastMsg.chartConfig = data.config
                            }
                            // E. Trace 日志 (🔥 修复：严格去重)
                            else if (data.type === 'trace') {
                                if (!lastMsg.traceLogs) lastMsg.traceLogs = []
                                const logData = data.data

                                // 查找是否已经存在同一个 tool 的 pending 状态日志
                                const existingIndex =
                                    lastMsg.traceLogs.findIndex(
                                        l =>
                                            l.tool === logData.tool &&
                                            l.status === 'pending'
                                    )

                                if (existingIndex !== -1) {
                                    // 如果存在，更新它 (比如从 pending -> success/error)
                                    // 使用解构更新，确保 React 感知到变化
                                    const updatedLogs = [...lastMsg.traceLogs]
                                    updatedLogs[existingIndex] = {
                                        ...updatedLogs[existingIndex],
                                        ...logData,
                                    }
                                    lastMsg.traceLogs = updatedLogs
                                } else {
                                    // 如果是新的 pending，或者之前已经结束了，才添加新的
                                    // 这里加一个防抖判断：如果最后一条日志完全一样，就不加了
                                    const lastLog =
                                        lastMsg.traceLogs[
                                            lastMsg.traceLogs.length - 1
                                        ]
                                    const isDuplicate =
                                        lastLog &&
                                        lastLog.tool === logData.tool &&
                                        lastLog.status === logData.status &&
                                        lastLog.message === logData.message

                                    if (!isDuplicate) {
                                        lastMsg.traceLogs.push(logData)
                                    }
                                }
                            }

                            return [...newMsgs.slice(0, -1), lastMsg]
                        })
                    } catch (e) {
                        console.error(e)
                    }
                }
            }
        } catch (err) {
            console.error(err)
            setMessages(prev => {
                const newMsgs = [...prev]
                const lastMsg = newMsgs[newMsgs.length - 1]
                lastMsg.content += `\n\n❌ Error: ${
                    err instanceof Error ? err.message : 'Unknown error'
                }`
                return newMsgs
            })
        } finally {
            setIsLoading(false)
        }
    }

    return (
        <div className='flex flex-col h-screen bg-gray-50 font-sans'>
            {/* Header */}
            <header className='bg-white border-b border-gray-200 px-6 py-4 shadow-sm flex items-center justify-between z-10'>
                <div className='flex items-center gap-3'>
                    <div className='bg-indigo-600 p-2 rounded-lg'>
                        <svg
                            className='w-6 h-6 text-white'
                            fill='none'
                            stroke='currentColor'
                            viewBox='0 0 24 24'
                        >
                            <path
                                strokeLinecap='round'
                                strokeLinejoin='round'
                                strokeWidth={2}
                                d='M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z'
                            />
                        </svg>
                    </div>
                    <h1 className='text-xl font-bold text-gray-800'>
                        何意味
                        <span className='ml-2 text-xs font-normal text-gray-500 bg-gray-100 px-2 py-1 rounded-full'>
                            你想RAG出怎样的意味
                        </span>
                    </h1>
                </div>
            </header>

            {/* Chat Area */}
            <div className='flex-1 overflow-y-auto px-4 py-6 sm:px-6 lg:px-8 custom-scrollbar'>
                <div className='max-w-4xl mx-auto'>
                    {messages.length === 0 ? (
                        <div className='text-center mt-20 opacity-50'>
                            <p className='text-6xl mb-4'>📊</p>
                            <p className='text-xl text-gray-600'>
                                想分析点什么？
                            </p>
                            <p className='text-sm text-gray-400 mt-2'>
                                试试问："根据车辆基本信息的车型，画个饼图"或"番茄炒蛋怎么做？"
                            </p>
                        </div>
                    ) : (
                        messages.map((msg, i) => (
                            <ChatMessage key={i} msg={msg} />
                        ))
                    )}

                    {isLoading &&
                        messages.length > 0 &&
                        messages[messages.length - 1].role === 'user' && (
                            <div className='flex justify-start w-full mb-8'>
                                <div className='bg-white p-4 rounded-2xl rounded-tl-none border border-gray-100 shadow-sm flex items-center gap-2'>
                                    <span className='text-sm text-gray-400'>
                                        Agent 正在思考...
                                    </span>
                                </div>
                            </div>
                        )}

                    <div ref={bottomRef} className='h-4' />
                </div>
            </div>

            {/* Input Area */}
            <div className='bg-white border-t border-gray-200 p-4 sm:p-6'>
                <div className='max-w-4xl mx-auto'>
                    <form
                        onSubmit={handleSend}
                        className='relative flex items-center gap-2'
                    >
                        <input
                            type='text'
                            className='w-full pl-5 pr-14 py-4 bg-gray-50 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:bg-white transition-all shadow-sm text-gray-800 placeholder-gray-400'
                            placeholder='请输入问题'
                            value={input}
                            onChange={e => setInput(e.target.value)}
                            disabled={isLoading}
                        />
                        <button
                            type='submit'
                            disabled={isLoading || !input.trim()}
                            className='absolute right-2 p-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors shadow-sm'
                        >
                            <svg
                                xmlns='http://www.w3.org/2000/svg'
                                viewBox='0 0 24 24'
                                fill='currentColor'
                                className='w-6 h-6'
                            >
                                <path d='M3.478 2.405a.75.75 0 00-.926.94l2.432 7.905H13.5a.75.75 0 010 1.5H4.984l-2.432 7.905a.75.75 0 00.926.94 60.519 60.519 0 0018.445-8.986.75.75 0 000-1.218A60.517 60.517 0 003.478 2.405z' />
                            </svg>
                        </button>
                    </form>
                </div>
            </div>
        </div>
    )
}
