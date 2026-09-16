class UnitQrModel {
  final int idunidad;
  final String numeroserie;
  final String? imei1;
  final String? imei2;
  final String uuidpublico;
  final String estado;
  final String productoNombre;
  final String varianteSku;
  final String? color;
  final String? almacenamiento;
  final bool tieneQr;
  final int? idcodigoqr;
  final String? tokenpublico;
  final String? url;
  final String? fechageneracion;

  UnitQrModel({
    required this.idunidad,
    required this.numeroserie,
    this.imei1,
    this.imei2,
    required this.uuidpublico,
    required this.estado,
    required this.productoNombre,
    required this.varianteSku,
    this.color,
    this.almacenamiento,
    required this.tieneQr,
    this.idcodigoqr,
    this.tokenpublico,
    this.url,
    this.fechageneracion,
  });

  factory UnitQrModel.fromJson(Map<String, dynamic> json) {
    return UnitQrModel(
      idunidad: json['idunidad'] ?? 0,
      numeroserie: json['numeroserie'] ?? '',
      imei1: json['imei1'],
      imei2: json['imei2'],
      uuidpublico: json['uuidpublico'] ?? '',
      estado: json['estado'] ?? '',
      productoNombre: json['producto_nombre'] ?? '',
      varianteSku: json['variante_sku'] ?? '',
      color: json['color'],
      almacenamiento: json['almacenamiento'],
      tieneQr: json['tiene_qr'] ?? false,
      idcodigoqr: json['idcodigoqr'],
      tokenpublico: json['tokenpublico'],
      url: json['url'],
      fechageneracion: json['fechageneracion'],
    );
  }
}

class GenerateQrResultModel {
  final int idcodigoqr;
  final int idunidad;
  final String numeroserie;
  final String uuidpublico;
  final String tokenpublico;
  final String url;
  final String fechageneracion;
  final String qrImageUrl;
  final String message;

  GenerateQrResultModel({
    required this.idcodigoqr,
    required this.idunidad,
    required this.numeroserie,
    required this.uuidpublico,
    required this.tokenpublico,
    required this.url,
    required this.fechageneracion,
    required this.qrImageUrl,
    required this.message,
  });

  factory GenerateQrResultModel.fromJson(Map<String, dynamic> json) {
    return GenerateQrResultModel(
      idcodigoqr: json['idcodigoqr'] ?? 0,
      idunidad: json['idunidad'] ?? 0,
      numeroserie: json['numeroserie'] ?? '',
      uuidpublico: json['uuidpublico'] ?? '',
      tokenpublico: json['tokenpublico'] ?? '',
      url: json['url'] ?? '',
      fechageneracion: json['fechageneracion'] ?? '',
      qrImageUrl: json['qr_image_url'] ?? '',
      message: json['message'] ?? '',
    );
  }
}
