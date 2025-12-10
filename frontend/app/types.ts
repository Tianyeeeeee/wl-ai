export interface Document {
    id: string | number;
    title: string;
    content: string;
    similarity: number;
    metadata?: Record<string, any>;
  }
  
  export interface TraceLog {
    status: 'pending' | 'success' | 'error';
    tool: string;
    args?: any;
    message?: string;
    output?: string;
  }
  
  export interface ChartConfig {
    type: 'bar' | 'line' | 'pie' | 'area';
    xKey: string;
    yKey: string;
    title?: string;
  }
  
  export interface Message {
    role: 'user' | 'assistant';
    content: string;
    thoughts?: string;
    traceLogs?: TraceLog[];
    tableData?: any[];
    // 图表相关
    chartData?: any[];
    chartConfig?: ChartConfig;
    retrievedDocs?: Document[];
  }