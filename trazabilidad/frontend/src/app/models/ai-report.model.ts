export interface KPIItem {
  label: string;
  value: string;
  trend?: string;
  color?: string;
}

export interface ChartData {
  chart_type: string;
  title: string;
  labels: string[];
  datasets: Array<{
    data: number[];
    backgroundColor?: string[];
    label?: string;
  }>;
}

export interface VoiceReportResponse {
  report_id: string;
  query_interpreted: string;
  category: string;
  voice_summary: string;
  executive_summary: string;
  kpis: KPIItem[];
  chart: ChartData;
  table_headers: string[];
  table_rows: any[][];
  generated_at: string;
  pdf_download_url: string;
  excel_download_url: string;
}
