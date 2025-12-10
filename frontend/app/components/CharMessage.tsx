import React, { useState } from 'react'
import ReactMarkdown from 'react-markdown'
import { Message } from '../types'
import TableDisplay from './TableDisplay'
import ChartDisplay from './ChartDisplay' // 引入 ECharts 组件

interface ChatMessageProps {
    msg: Message
}

export default function ChatMessage({ msg }: ChatMessageProps) {
    const isUser = msg.role === 'user'
    const [isThoughtsOpen, setIsThoughtsOpen] = useState(false)

    return (
        <div
            className={`flex w-full mb-8 ${
                isUser ? 'justify-end' : 'justify-start'
            }`}
        >
            <div
                className={`flex max-w-[90%] md:max-w-[80%] ${
                    isUser ? 'flex-row-reverse' : 'flex-row'
                }`}
            >
                {/* 头像 */}
                <div
                    className={`flex-shrink-0 h-10 w-10 rounded-full flex items-center justify-center shadow-sm ${
                        isUser
                            ? 'bg-indigo-600 ml-3 text-white'
                            : 'bg-emerald-500 mr-3 text-white'
                    }`}
                >
                    {isUser ? (
                        <svg
                            xmlns='http://www.w3.org/2000/svg'
                            viewBox='0 0 24 24'
                            fill='currentColor'
                            className='w-6 h-6'
                        >
                            <path
                                fillRule='evenodd'
                                d='M7.5 6a4.5 4.5 0 119 0 4.5 4.5 0 01-9 0zM3.751 20.105a8.25 8.25 0 0116.498 0 .75.75 0 01-.437.695A18.683 18.683 0 0112 22.5c-2.786 0-5.433-.608-7.812-1.7a.75.75 0 01-.437-.695z'
                                clipRule='evenodd'
                            />
                        </svg>
                    ) : (
                        <svg
                            xmlns='http://www.w3.org/2000/svg'
                            viewBox='0 0 24 24'
                            fill='currentColor'
                            className='w-6 h-6'
                        >
                            <path d='M16.5 7.5h-9v9h9v-9z' />
                            <path
                                fillRule='evenodd'
                                d='M8.25 2.25A.75.75 0 019 3v.75h2.25V3a.75.75 0 011.5 0v.75H15V3a.75.75 0 011.5 0v.75h.75a3 3 0 013 3v.75H21A.75.75 0 0121 9h-.75v2.25H21a.75.75 0 010 1.5h-.75V15H21a.75.75 0 010 1.5h-.75v.75a3 3 0 01-3 3h-.75V21a.75.75 0 01-1.5 0v-.75h-2.25V21a.75.75 0 01-1.5 0v-.75H9V21a.75.75 0 01-1.5 0v-.75h-.75a3 3 0 01-3-3v-.75H3A.75.75 0 013 15h.75v-2.25H3a.75.75 0 010-1.5h.75V9H3a.75.75 0 010-1.5h.75V6.75a3 3 0 013-3h.75V3a.75.75 0 01.75-.75zM6 6.75A1.5 1.5 0 017.5 5.25h9A1.5 1.5 0 0118 6.75v9A1.5 1.5 0 0116.5 17.25h-9A1.5 1.5 0 016 15.75v-9z'
                                clipRule='evenodd'
                            />
                        </svg>
                    )}
                </div>

                <div
                    className={`flex flex-col w-full ${
                        isUser ? 'items-end' : 'items-start'
                    }`}
                >
                    {/* ================= 🧠 思考过程 (AI Only) ================= */}
                    {!isUser && msg.thoughts && (
                        <div className='mb-2 w-full max-w-full'>
                            <button
                                onClick={() =>
                                    setIsThoughtsOpen(!isThoughtsOpen)
                                }
                                className='flex items-center gap-1 text-xs text-gray-500 hover:text-gray-700 bg-gray-100 hover:bg-gray-200 px-3 py-1.5 rounded-full transition-colors mb-2'
                            >
                                {isThoughtsOpen
                                    ? '🔽 收起思考过程'
                                    : '🤔 展开 DeepSeek 深度思考'}
                            </button>

                            {isThoughtsOpen && (
                                <div className='bg-gray-50 p-4 rounded-lg border border-gray-200 text-sm text-gray-600 font-mono whitespace-pre-wrap mb-2 animate-fade-in'>
                                    {msg.thoughts}
                                </div>
                            )}
                        </div>
                    )}

                    {/* ================= 🛠️ 执行痕迹 (AI Only) ================= */}
                    {!isUser && msg.traceLogs && msg.traceLogs.length > 0 && (
                        <div className='mb-3 w-full space-y-1.5'>
                            {msg.traceLogs.map((log, idx) => (
                                <div
                                    key={idx}
                                    className='flex items-center gap-2 text-xs bg-white border border-blue-100 text-slate-600 px-3 py-2 rounded-md shadow-sm'
                                >
                                    {log.status === 'pending' && (
                                        <span className='animate-spin text-blue-500'>
                                            ⏳
                                        </span>
                                    )}
                                    {log.status === 'success' && (
                                        <span className='text-green-500'>
                                            ✅
                                        </span>
                                    )}
                                    {log.status === 'error' && (
                                        <span className='text-red-500'>❌</span>
                                    )}
                                    <span className='font-medium font-mono'>
                                        {log.tool}
                                    </span>
                                    <span className='text-gray-400'>|</span>
                                    <span className='truncate max-w-[200px] md:max-w-md'>
                                        {log.message || 'Executing...'}
                                    </span>
                                </div>
                            ))}
                        </div>
                    )}

                    {/* ================= 💬 消息气泡 ================= */}
                    <div
                        className={`p-4 rounded-2xl shadow-sm leading-relaxed max-w-full overflow-hidden ${
                            isUser
                                ? 'bg-indigo-600 text-white rounded-tr-none'
                                : 'bg-white text-gray-800 border border-gray-100 rounded-tl-none'
                        }`}
                    >
                        {isUser ? (
                            <div className='whitespace-pre-wrap'>
                                {msg.content}
                            </div>
                        ) : (
                            <>
                                {/* 1. Markdown 文本 */}
                                {msg.content ? (
                                    <div className='prose prose-sm max-w-none prose-p:my-1 prose-headings:my-2'>
                                        <ReactMarkdown>
                                            {msg.content}
                                        </ReactMarkdown>
                                    </div>
                                ) : (
                                    !msg.tableData &&
                                    !msg.traceLogs &&
                                    !msg.chartData && (
                                        <span className='animate-pulse text-gray-400'>
                                            正在思考...
                                        </span>
                                    )
                                )}

                                {/* 2. 📊 表格渲染 */}
                                {msg.tableData && (
                                    <div className='mt-4 w-full'>
                                        <TableDisplay data={msg.tableData} />
                                    </div>
                                )}

                                {/* 3. 📈 图表渲染 (ECharts) */}
                                {msg.chartData && msg.chartConfig && (
                                    <div className='mt-4 w-full'>
                                        <ChartDisplay
                                            data={msg.chartData}
                                            config={msg.chartConfig}
                                        />
                                    </div>
                                )}
                            </>
                        )}
                    </div>

                    {/* ================= 📚 引用文档 (AI Only) ================= */}
                    {!isUser &&
                        msg.retrievedDocs &&
                        msg.retrievedDocs.length > 0 && (
                            <div className='mt-2 text-xs text-gray-400 flex flex-wrap gap-2'>
                                <span>参考资料:</span>
                                {msg.retrievedDocs.map((doc, i) => (
                                    <span
                                        key={i}
                                        className='bg-gray-100 px-1.5 py-0.5 rounded text-gray-500'
                                    >
                                        {doc.title || `文档 ${i + 1}`}
                                    </span>
                                ))}
                            </div>
                        )}
                </div>
            </div>
        </div>
    )
}
