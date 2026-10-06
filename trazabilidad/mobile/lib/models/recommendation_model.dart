class RecommendationMetricModel {
  final num? vendidas;
  final num? disponibles;
  final num? devueltas;
  final num? pedidas;
  final num? recibidas;
  final num? precioventa;
  final num? costopromedio;
  final num? margenPct;
  final num? margenAbsUsd;
  final num? rotacionMensual;
  final num? devolucionPct;
  final num? brechaDemanda;
  final num? precioSugeridoUsd;

  RecommendationMetricModel({
    this.vendidas,
    this.disponibles,
    this.devueltas,
    this.pedidas,
    this.recibidas,
    this.precioventa,
    this.costopromedio,
    this.margenPct,
    this.margenAbsUsd,
    this.rotacionMensual,
    this.devolucionPct,
    this.brechaDemanda,
    this.precioSugeridoUsd,
  });

  static num? _num(dynamic value) =>
      value == null ? null : (value is num ? value : num.tryParse(value.toString()));

  factory RecommendationMetricModel.fromJson(Map<String, dynamic> json) {
    return RecommendationMetricModel(
      vendidas: _num(json['vendidas']),
      disponibles: _num(json['disponibles']),
      devueltas: _num(json['devueltas']),
      pedidas: _num(json['pedidas']),
      recibidas: _num(json['recibidas']),
      precioventa: _num(json['precioventa']),
      costopromedio: _num(json['costopromedio']),
      margenPct: _num(json['margen_pct']),
      margenAbsUsd: _num(json['margen_abs_usd']),
      rotacionMensual: _num(json['rotacion_mensual']),
      devolucionPct: _num(json['devolucion_pct']),
      brechaDemanda: _num(json['brecha_demanda']),
      precioSugeridoUsd: _num(json['precio_sugerido_usd']),
    );
  }

  /// Lista de métricas con etiqueta y valor ya formateado para mostrar en pantalla
  List<({String label, String value})> get displayEntries {
    final entries = <({String label, String value})>[];

    void addNum(String label, num? value) {
      if (value != null) entries.add((label: label, value: value.toString()));
    }

    void addMoney(String label, num? value) {
      if (value != null) entries.add((label: label, value: '\$${value.toStringAsFixed(2)}'));
    }

    void addPercent(String label, num? value) {
      if (value != null) entries.add((label: label, value: '${value.toStringAsFixed(1)}%'));
    }

    addNum('Vendidas', vendidas);
    addNum('Disponibles', disponibles);
    addNum('Devueltas', devueltas);
    addNum('Pedidas', pedidas);
    addNum('Recibidas', recibidas);
    addMoney('Precio venta', precioventa);
    addMoney('Costo prom.', costopromedio);
    addPercent('Margen', margenPct);
    addMoney('Margen \$', margenAbsUsd);
    if (rotacionMensual != null) {
      entries.add((label: 'Rotación mensual', value: rotacionMensual!.toStringAsFixed(2)));
    }
    addPercent('Devolución', devolucionPct);
    addNum('Brecha demanda', brechaDemanda);
    addMoney('Precio sugerido', precioSugeridoUsd);

    return entries;
  }
}

class PricingRecommendationModel {
  final int idvariante;
  final String? sku;
  final String? producto;
  final String? capacidad;
  final String? color;
  final String tipo;
  final String prioridad;
  final String titulo;
  final String justificacion;
  final String accionSugerida;
  final RecommendationMetricModel metricas;
  final List<String> evidencia;

  PricingRecommendationModel({
    required this.idvariante,
    this.sku,
    this.producto,
    this.capacidad,
    this.color,
    required this.tipo,
    required this.prioridad,
    required this.titulo,
    required this.justificacion,
    required this.accionSugerida,
    required this.metricas,
    required this.evidencia,
  });

  factory PricingRecommendationModel.fromJson(Map<String, dynamic> json) {
    return PricingRecommendationModel(
      idvariante: json['idvariante'] ?? 0,
      sku: json['sku'],
      producto: json['producto'],
      capacidad: json['capacidad'],
      color: json['color'],
      tipo: json['tipo'] ?? '',
      prioridad: json['prioridad'] ?? 'baja',
      titulo: json['titulo'] ?? '',
      justificacion: json['justificacion'] ?? '',
      accionSugerida: json['accion_sugerida'] ?? '',
      metricas: RecommendationMetricModel.fromJson(
          Map<String, dynamic>.from(json['metricas'] ?? {})),
      evidencia: List<String>.from(json['evidencia'] ?? []),
    );
  }

  String get prioridadLabel => const {
        'critica': 'Crítica',
        'alta': 'Alta',
        'media': 'Media',
        'baja': 'Baja',
      }[prioridad] ??
      prioridad;

  String get tipoLabel => const {
        'MARGEN_NEGATIVO': 'Margen negativo',
        'SUBIR_PRECIO': 'Subir precio',
        'BAJAR_PRECIO': 'Bajar precio',
        'SOBRESTOCK': 'Sobrestock',
        'REPOSICION_URGENTE': 'Reposición urgente',
        'RIESGO_DEVOLUCION': 'Riesgo de devolución',
        'BRECHA_DEMANDA': 'Brecha de demanda',
      }[tipo] ??
      tipo;

  String get descripcionVariante {
    final partes = <String>[
      if (producto != null && producto!.isNotEmpty) producto!,
      if (capacidad != null && capacidad!.isNotEmpty) capacidad!,
      if (color != null && color!.isNotEmpty) color!,
    ];
    return partes.join(' · ');
  }
}

class PricingRecommendationsModel {
  final int tenantId;
  final String generatedAt;
  final int totalRecomendaciones;
  final List<PricingRecommendationModel> recomendaciones;

  PricingRecommendationsModel({
    required this.tenantId,
    required this.generatedAt,
    required this.totalRecomendaciones,
    required this.recomendaciones,
  });

  factory PricingRecommendationsModel.fromJson(Map<String, dynamic> json) {
    return PricingRecommendationsModel(
      tenantId: json['tenant_id'] ?? 0,
      generatedAt: json['generated_at'] ?? '',
      totalRecomendaciones: json['total_recomendaciones'] ?? 0,
      recomendaciones: (json['recomendaciones'] as List<dynamic>? ?? [])
          .map((r) => PricingRecommendationModel.fromJson(r as Map<String, dynamic>))
          .toList(),
    );
  }
}