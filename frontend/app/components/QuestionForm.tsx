'use client'

import React from 'react'

interface QuestionFormProps {
    question: string
    setQuestion: (value: string) => void
    isLoading: boolean
    onSubmit: (e: React.FormEvent) => void
}

export default function QuestionForm({
    question,
    setQuestion,
    isLoading,
    onSubmit,
}: QuestionFormProps) {
    return (
        <div className='bg-white shadow rounded-lg p-6 mb-8'>
            <form onSubmit={onSubmit}>
                <div className='mb-4'>
                    <label
                        htmlFor='question'
                        className='block text-sm font-medium text-gray-700 mb-2'
                    >
                        请输入您的问题
                    </label>
                    <textarea
                        id='question'
                        rows={3}
                        value={question}
                        onChange={e => setQuestion(e.target.value)}
                        onKeyDown={e => {
                            if (
                                e.key === 'Enter' &&
                                !isLoading &&
                                question.trim()
                            ) {
                                onSubmit(e as unknown as React.FormEvent)
                            }
                        }}
                        className='shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border border-gray-300 rounded-md p-3'
                        placeholder='例如：什么是人工智能？'
                    />
                </div>
                <button
                    type='submit'
                    disabled={isLoading || !question.trim()}
                    className='w-full flex justify-center py-3 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed'
                >
                    {isLoading ? (
                        <>
                            <svg
                                className='animate-spin -ml-1 mr-3 h-5 w-5 text-white'
                                xmlns='http://www.w3.org/2000/svg'
                                fill='none'
                                viewBox='0 0 24 24'
                            >
                                <circle
                                    className='opacity-25'
                                    cx='12'
                                    cy='12'
                                    r='10'
                                    stroke='currentColor'
                                    strokeWidth='4'
                                ></circle>
                                <path
                                    className='opacity-75'
                                    fill='currentColor'
                                    d='M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z'
                                ></path>
                            </svg>
                            正在搜索...
                        </>
                    ) : (
                        '🚀 开始查询'
                    )}
                </button>
            </form>
        </div>
    )
}
