class ShipmentModel {
  final int idenvio;
  final int idtenant;
  final String codigoenvio;
  final String? actorOrigenNombre;
  final String? actorDestinoNombre;
  final String? transportistaNombre;
  final String? fechasalida;
  final String? fechaestimada;
  final String? fechaentrega;
  final String estado;
  final String? trackingexterno;
  final int totalUnidades;

  ShipmentModel({
    required this.idenvio,
    required this.idtenant,
    required this.codigoenvio,
    this.actorOrigenNombre,
    this.actorDestinoNombre,
    this.transportistaNombre,
    this.fechasalida,
    this.fechaestimada,
    this.fechaentrega,
    required this.estado,
    this.trackingexterno,
    required this.totalUnidades,
  });

  factory ShipmentModel.fromJson(Map<String, dynamic> json) {
    return ShipmentModel(
      idenvio: json['idenvio'] ?? 0,
      idtenant: json['idtenant'] ?? 0,
      codigoenvio: json['codigoenvio'] ?? '',
      actorOrigenNombre: json['actor_origen_nombre'],
      actorDestinoNombre: json['actor_destino_nombre'],
      transportistaNombre: json['transportista_nombre'],
      fechasalida: json['fechasalida'],
      fechaestimada: json['fechaestimada'],
      fechaentrega: json['fechaentrega'],
      estado: json['estado'] ?? 'preparacion',
      trackingexterno: json['trackingexterno'],
      totalUnidades: json['total_unidades'] ?? 0,
    );
  }
}

class TransportConditionModel {
  final int? idcondicion;
  final int? idevento;
  final double? temperatura;
  final double? humedad;
  final double? presion;
  final double? nivelvibracion;
  final String? timestampregistro;
  final String? fuentedatos;

  TransportConditionModel({
    this.idcondicion,
    this.idevento,
    this.temperatura,
    this.humedad,
    this.presion,
    this.nivelvibracion,
    this.timestampregistro,
    this.fuentedatos,
  });

  factory TransportConditionModel.fromJson(Map<String, dynamic> json) {
    return TransportConditionModel(
      idcondicion: json['idcondicion'],
      idevento: json['idevento'],
      temperatura: json['temperatura'] != null ? double.tryParse(json['temperatura'].toString()) : null,
      humedad: json['humedad'] != null ? double.tryParse(json['humedad'].toString()) : null,
      presion: json['presion'] != null ? double.tryParse(json['presion'].toString()) : null,
      nivelvibracion: json['nivelvibracion'] != null ? double.tryParse(json['nivelvibracion'].toString()) : null,
      timestampregistro: json['timestampregistro'],
      fuentedatos: json['fuentedatos'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      if (temperatura != null) 'temperatura': temperatura,
      if (humedad != null) 'humedad': humedad,
      if (presion != null) 'presion': presion,
      if (nivelvibracion != null) 'nivelvibracion': nivelvibracion,
      'fuentedatos': fuentedatos ?? 'App Móvil Operador',
    };
  }
}

class TransportEventModel {
  final int idevento;
  final int idtenant;
  final String tipoevento;
  final String fechahora;
  final int idubicacion;
  final String? ubicacionNombre;
  final String? usuarioNombre;
  final String? descripcion;
  final String? payloadhash;
  final String? estadoverificacion;
  final TransportConditionModel? condiciones;

  TransportEventModel({
    required this.idevento,
    required this.idtenant,
    required this.tipoevento,
    required this.fechahora,
    required this.idubicacion,
    this.ubicacionNombre,
    this.usuarioNombre,
    this.descripcion,
    this.payloadhash,
    this.estadoverificacion,
    this.condiciones,
  });

  factory TransportEventModel.fromJson(Map<String, dynamic> json) {
    return TransportEventModel(
      idevento: json['idevento'] ?? 0,
      idtenant: json['idtenant'] ?? 0,
      tipoevento: json['tipoevento'] ?? '',
      fechahora: json['fechahora'] ?? '',
      idubicacion: json['idubicacion'] ?? 0,
      ubicacionNombre: json['ubicacion_nombre'],
      usuarioNombre: json['usuario_nombre'],
      descripcion: json['descripcion'],
      payloadhash: json['payloadhash'],
      estadoverificacion: json['estadoverificacion'],
      condiciones: json['condiciones'] != null ? TransportConditionModel.fromJson(json['condiciones']) : null,
    );
  }
}

class ShipmentTimelineModel {
  final ShipmentModel envio;
  final List<TransportEventModel> eventos;
  final List<String> unidadesNumeros;

  ShipmentTimelineModel({
    required this.envio,
    required this.eventos,
    required this.unidadesNumeros,
  });

  factory ShipmentTimelineModel.fromJson(Map<String, dynamic> json) {
    return ShipmentTimelineModel(
      envio: ShipmentModel.fromJson(json['envio']),
      eventos: (json['eventos'] as List<dynamic>?)
              ?.map((e) => TransportEventModel.fromJson(e))
              .toList() ??
          [],
      unidadesNumeros: (json['unidades_numeros'] as List<dynamic>?)
              ?.map((e) => e.toString())
              .toList() ??
          [],
    );
  }
}
