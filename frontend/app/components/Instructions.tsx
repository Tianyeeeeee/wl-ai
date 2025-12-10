'use client'

import React from 'react'

export default function Instructions() {
    return (
        <div className='bg-white shadow rounded-lg p-6 mt-8'>
            <h2 className='text-lg font-medium text-gray-900 mb-3'>
                📋 使用说明
            </h2>
            <ul className='list-disc pl-5 space-y-2 text-gray-600'>
                <li>在上方输入框中输入您的问题</li>
                <li>系统会在知识库中检索相关信息</li>
                <li>基于检索结果生成答案</li>
                <li>
                    可以尝试的问题：什么是人工智能？机器学习是什么？
                </li>
            </ul>
        </div>
    )
}