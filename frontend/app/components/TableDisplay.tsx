// components/TableDisplay.tsx
import React from 'react'

interface TableDisplayProps {
  data: any[] | null
}

export default function TableDisplay({ data }: TableDisplayProps) {
  if (!data || data.length === 0) return null

  // 动态获取表头
  const headers = Object.keys(data[0])

  return (
    <div className="my-4 overflow-hidden border border-gray-200 rounded-lg shadow-sm bg-white animate-fade-in-up">
      <div className="bg-blue-50 px-4 py-2 border-b border-blue-100 flex items-center justify-between">
        <h3 className="text-sm font-bold text-blue-700 flex items-center gap-2">
          📊 查询结果
        </h3>
        <span className="text-xs text-blue-500 bg-white px-2 py-0.5 rounded-full border border-blue-200">
          {data.length} 条记录
        </span>
      </div>
      
      <div className="overflow-x-auto max-h-[400px] min-w-[600px]">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50 sticky top-0 z-10">
            <tr>
              {headers.map((header) => (
                <th
                  key={header}
                  scope="col"
                  className="px-4 py-3 text-left text-xs font-bold text-gray-500 uppercase tracking-wider whitespace-nowrap"
                >
                  {header}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {data.map((row, rowIndex) => (
              <tr key={rowIndex} className="hover:bg-gray-50 transition-colors">
                {headers.map((header) => (
                  <td
                    key={`${rowIndex}-${header}`}
                    className="px-4 py-3 whitespace-nowrap text-sm text-gray-700 font-mono"
                  >
                    {typeof row[header] === 'object' && row[header] !== null
                      ? JSON.stringify(row[header])
                      : String(row[header] ?? '-')}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}