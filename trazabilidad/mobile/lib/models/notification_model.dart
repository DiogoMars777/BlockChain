class NotificationModel {
  final int idnotificacion;
  final int idusuariotenant;
  final String titulo;
  final String contenido;
  final bool leida;
  final String fechaenvio;
  final String? fechalectura;
  final String? enlaceaccion;

  NotificationModel({
    required this.idnotificacion,
    required this.idusuariotenant,
    required this.titulo,
    required this.contenido,
    required this.leida,
    required this.fechaenvio,
    this.fechalectura,
    this.enlaceaccion,
  });

  factory NotificationModel.fromJson(Map<String, dynamic> json) {
    return NotificationModel(
      idnotificacion: json['idnotificacion'] ?? 0,
      idusuariotenant: json['idusuariotenant'] ?? 0,
      titulo: json['titulo'] ?? '',
      contenido: json['contenido'] ?? '',
      leida: json['leida'] ?? false,
      fechaenvio: json['fechaenvio'] ?? '',
      fechalectura: json['fechalectura'],
      enlaceaccion: json['enlaceaccion'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'idnotificacion': idnotificacion,
      'idusuariotenant': idusuariotenant,
      'titulo': titulo,
      'contenido': contenido,
      'leida': leida,
      'fechaenvio': fechaenvio,
      'fechalectura': fechalectura,
      'enlaceaccion': enlaceaccion,
    };
  }
}
