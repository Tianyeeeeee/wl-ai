'use client'

import React from 'react'
import { Document } from '../types'

interface DocumentListProps {
    documents: Document[]
}

export default function DocumentList({ documents }: DocumentListProps) {
    if (!documents || documents.length === 0) return null

    return (
        <div className='bg-white shadow rounded-lg p-6'>
            <h2 className='text-xl font-semibold text-gray-900 mb-4 flex items-center gap-2'>
                📚 参考文档
                <span className='text-sm font-normal text-gray-500 bg-gray-100 px-2 py-0.5 rounded-full'>
                    {documents.length}篇
                </span>
            </h2>
            <div className='space-y-4'>
                {documents.map((doc, index) => (
                    <div
                        // 使用 id 或者 index 作为 key，防止有些临时数据没有 id
                        key={doc.id || index}
                        className='border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow group'
                    >
                        <div className='flex justify-between items-start mb-2'>
                            <h3 className='font-medium text-gray-900 group-hover:text-blue-600 transition-colors'>
                                {doc.title || '无标题文档'}
                            </h3>
                            {/* 只有当相似度存在且大于0时才显示 */}
                            {doc.similarity > 0 && (
                                <span
                                    className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                                        doc.similarity > 0.6
                                            ? 'bg-green-100 text-green-800'
                                            : 'bg-yellow-100 text-yellow-800'
                                    }`}
                                >
                                    相似度: {(doc.similarity * 100).toFixed(1)}%
                                </span>
                            )}
                        </div>
                        <p className='text-gray-600 text-sm leading-relaxed'>
                            {/* 截取前 150 个字符，防止内容太长 */}
                            {doc.content.length > 150
                                ? `${doc.content.substring(0, 150)}...`
                                : doc.content}
                        </p>

                        {/* 只有当 metadata 存在且不为空时渲染 */}
                        {doc.metadata &&
                            Object.keys(doc.metadata).length > 0 && (
                                <div className='mt-3 pt-3 border-t border-gray-100 flex flex-wrap gap-2 text-xs text-gray-500'>
                                    {doc.metadata.source && (
                                        <span className='bg-gray-50 px-2 py-1 rounded'>
                                            来源: {doc.metadata.source}
                                        </span>
                                    )}
                                    {doc.metadata.category && (
                                        <span className='bg-gray-50 px-2 py-1 rounded'>
                                            分类: {doc.metadata.category}
                                        </span>
                                    )}
                                </div>
                            )}
                    </div>
                ))}
            </div>
        </div>
    )
}
