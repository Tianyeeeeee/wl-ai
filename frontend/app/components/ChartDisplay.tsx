'use client'

import React, { useMemo } from 'react'
import ReactECharts from 'echarts-for-react'
import { ChartConfig } from '../types'

interface ChartDisplayProps {
    data: any[]
    config: ChartConfig
}

export default function ChartDisplay({ data, config }: ChartDisplayProps) {
    if (!data || data.length === 0) return null

    const { type, xKey, yKey, title } = config

    // 使用 useMemo 优化性能，防止不必要的重渲染
    const option = useMemo(() => {
        // 通用颜色盘 (Tailwind 风格)
        const colors = [
            '#4F46E5',
            '#10B981',
            '#F59E0B',
            '#EF4444',
            '#8B5CF6',
            '#EC4899',
        ]

        // 基础配置
        const baseOption = {
            title: {
                show: false, // 我们在外部渲染标题
            },
            tooltip: {
                trigger: type === 'pie' ? 'item' : 'axis',
                backgroundColor: 'rgba(255, 255, 255, 0.9)',
                borderColor: '#E5E7EB',
                textStyle: { color: '#374151' },
            },
            grid: {
                top: 30,
                right: 30,
                bottom: 30,
                left: 40,
                containLabel: true,
            },
            legend: {
                bottom: 0,
                textStyle: { color: '#6B7280' },
            },
        }

        // 1. 饼图特殊处理
        if (type === 'pie') {
            return {
                ...baseOption,
                series: [
                    {
                        name: title || '数据分布',
                        type: 'pie',
                        radius: ['40%', '70%'], // 环形图更现代
                        avoidLabelOverlap: false,
                        itemStyle: {
                            borderRadius: 10,
                            borderColor: '#fff',
                            borderWidth: 2,
                        },
                        label: {
                            show: false,
                            position: 'center',
                        },
                        emphasis: {
                            label: {
                                show: true,
                                fontSize: 14,
                                fontWeight: 'bold',
                            },
                        },
                        labelLine: { show: false },
                        // ECharts 饼图数据格式需要 { name: ..., value: ... }
                        data: data.map(item => ({
                            name: item[xKey],
                            value: item[yKey],
                        })),
                        color: colors,
                    },
                ],
            }
        }

        // 2. 直角坐标系图表 (Bar, Line, Area)
        const xAxisData = data.map(item => item[xKey])
        const seriesData = data.map(item => item[yKey])

        const commonSeriesConfig = {
            name: yKey, // 图例名称
            data: seriesData,
            smooth: true, // 平滑曲线
            itemStyle: { color: '#4F46E5' }, // 默认 Indigo 色
        }

        let seriesConfig = {}

        switch (type) {
            case 'bar':
                seriesConfig = {
                    ...commonSeriesConfig,
                    type: 'bar',
                    barMaxWidth: 50,
                    itemStyle: {
                        color: '#4F46E5',
                        borderRadius: [4, 4, 0, 0],
                    },
                }
                break
            case 'area':
                seriesConfig = {
                    ...commonSeriesConfig,
                    type: 'line',
                    areaStyle: {
                        color: {
                            type: 'linear',
                            x: 0,
                            y: 0,
                            x2: 0,
                            y2: 1,
                            colorStops: [
                                { offset: 0, color: 'rgba(79, 70, 229, 0.4)' },
                                { offset: 1, color: 'rgba(79, 70, 229, 0.05)' },
                            ],
                        },
                    },
                }
                break
            case 'line':
            default:
                seriesConfig = {
                    ...commonSeriesConfig,
                    type: 'line',
                    symbol: 'circle',
                    symbolSize: 8,
                    lineStyle: { width: 3 },
                }
                break
        }

        return {
            ...baseOption,
            xAxis: {
                type: 'category',
                data: xAxisData,
                axisLine: { lineStyle: { color: '#E5E7EB' } },
                axisLabel: { color: '#6B7280' },
            },
            yAxis: {
                type: 'value',
                splitLine: { lineStyle: { type: 'dashed', color: '#F3F4F6' } },
                axisLabel: { color: '#6B7280' },
            },
            series: [seriesConfig],
        }
    }, [data, config, type, xKey, yKey, title])

    return (
        <div className='my-4 bg-white p-4 rounded-xl border border-gray-200 shadow-sm animate-fade-in-up'>
            {title && (
                <h3 className='text-sm font-bold text-gray-700 mb-4 flex items-center gap-2'>
                    📊 {title}
                </h3>
            )}
            <div className='w-full'>
                <ReactECharts
                    option={option}
                    style={{
                        height: '450px',
                        width: '100%',
                        minWidth: '600px',
                    }}
                    opts={{ renderer: 'svg' }} // 使用 SVG 渲染更清晰
                />
            </div>
        </div>
    )
}
