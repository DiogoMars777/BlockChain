class KPIItemModel {
  final String label;
  final String value;
  final String? trend;
  final String color;

  KPIItemModel({
    required this.label,
    required this.value,
    this.trend,
    this.color = '#38BDF8',
  });

  factory KPIItemModel.fromJson(Map<String, dynamic> json) {
    return KPIItemModel(
      label: json['label'] ?? '',
      value: json['value'] ?? '',
      trend: json['trend'],
      color: json['color'] ?? '#38BDF8',
    );
  }
}

class ChartDataModel {
  final String chartType; // 'pie', 'bar', 'line', 'kpi'
  final String title;
  final List<String> labels;
  final List<Map<String, dynamic>> datasets;

  ChartDataModel({
    required this.chartType,
    required this.title,
    required this.labels,
    required this.datasets,
  });

  factory ChartDataModel.fromJson(Map<String, dynamic> json) {
    return ChartDataModel(
      chartType: json['chart_type'] ?? 'pie',
      title: json['title'] ?? 'Resumen Gráfico',
      labels: List<String>.from(json['labels'] ?? []),
      datasets: List<Map<String, dynamic>>.from(json['datasets'] ?? []),
    );
  }
}

class VoiceReportModel {
  final String reportId;
  final String queryInterpreted;
  final String category;
  final String voiceSummary;
  final String executiveSummary;
  final List<KPIItemModel> kpis;
  final ChartDataModel chart;
  final List<String> tableHeaders;
  final List<List<dynamic>> tableRows;
  final String generatedAt;
  final String pdfDownloadUrl;
  final String excelDownloadUrl;

  VoiceReportModel({
    required this.reportId,
    required this.queryInterpreted,
    required this.category,
    required this.voiceSummary,
    required this.executiveSummary,
    required this.kpis,
    required this.chart,
    required this.tableHeaders,
    required this.tableRows,
    required this.generatedAt,
    required this.pdfDownloadUrl,
    required this.excelDownloadUrl,
  });

  factory VoiceReportModel.fromJson(Map<String, dynamic> json) {
    return VoiceReportModel(
      reportId: json['report_id'] ?? '',
      queryInterpreted: json['query_interpreted'] ?? '',
      category: json['category'] ?? 'general',
      voiceSummary: json['voice_summary'] ?? '',
      executiveSummary: json['executive_summary'] ?? '',
      kpis: (json['kpis'] as List<dynamic>?)
              ?.map((k) => KPIItemModel.fromJson(k as Map<String, dynamic>))
              .toList() ??
          [],
      chart: ChartDataModel.fromJson(json['chart'] ?? {}),
      tableHeaders: List<String>.from(json['table_headers'] ?? []),
      tableRows: List<List<dynamic>>.from(
          (json['table_rows'] ?? []).map((row) => List<dynamic>.from(row))),
      generatedAt: json['generated_at'] ?? '',
      pdfDownloadUrl: json['pdf_download_url'] ?? '',
      excelDownloadUrl: json['excel_download_url'] ?? '',
    );
  }
}
