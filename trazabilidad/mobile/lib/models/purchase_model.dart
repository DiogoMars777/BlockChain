class CompraDetalleModel {
  final int idcompradetalle;
  final int idcompra;
  final int idvariante;
  final String sku;
  final String productoNombre;
  final String? color;
  final String? almacenamiento;
  final int cantidad;
  final double costounitariousd;
  final double subtotalusd;

  CompraDetalleModel({
    required this.idcompradetalle,
    required this.idcompra,
    required this.idvariante,
    required this.sku,
    required this.productoNombre,
    this.color,
    this.almacenamiento,
    required this.cantidad,
    required this.costounitariousd,
    required this.subtotalusd,
  });

  factory CompraDetalleModel.fromJson(Map<String, dynamic> json) {
    return CompraDetalleModel(
      idcompradetalle: json['idcompradetalle'] ?? 0,
      idcompra: json['idcompra'] ?? 0,
      idvariante: json['idvariante'] ?? 0,
      sku: json['sku'] ?? 'SKU-${json['idvariante']}',
      productoNombre: json['producto_nombre'] ?? 'Producto',
      color: json['color'],
      almacenamiento: json['almacenamiento'],
      cantidad: json['cantidad'] ?? 1,
      costounitariousd: double.tryParse(json['costounitariousd']?.toString() ?? '0.0') ?? 0.0,
      subtotalusd: double.tryParse(json['subtotalusd']?.toString() ?? '0.0') ?? 0.0,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'idcompradetalle': idcompradetalle,
      'idcompra': idcompra,
      'idvariante': idvariante,
      'sku': sku,
      'producto_nombre': productoNombre,
      'color': color,
      'almacenamiento': almacenamiento,
      'cantidad': cantidad,
      'costounitariousd': costounitariousd,
      'subtotalusd': subtotalusd,
    };
  }
}

class CompraModel {
  final int idcompra;
  final int idtenant;
  final int idproveedor;
  final String proveedorNombre;
  final String numeroorden;
  final String fechacompra;
  final double totalusd;
  final String estado;
  final int totalItems;
  final List<CompraDetalleModel> detalles;

  CompraModel({
    required this.idcompra,
    required this.idtenant,
    required this.idproveedor,
    required this.proveedorNombre,
    required this.numeroorden,
    required this.fechacompra,
    required this.totalusd,
    required this.estado,
    required this.totalItems,
    required this.detalles,
  });

  factory CompraModel.fromJson(Map<String, dynamic> json) {
    var rawDetalles = json['detalles'] as List? ?? [];
    List<CompraDetalleModel> parsedDetalles = rawDetalles
        .map((d) => CompraDetalleModel.fromJson(d as Map<String, dynamic>))
        .toList();

    return CompraModel(
      idcompra: json['idcompra'] ?? 0,
      idtenant: json['idtenant'] ?? 1,
      idproveedor: json['idproveedor'] ?? 0,
      proveedorNombre: json['proveedor_nombre'] ?? 'Proveedor #${json['idproveedor']}',
      numeroorden: json['numeroorden'] ?? '',
      fechacompra: json['fechacompra'] ?? '',
      totalusd: double.tryParse(json['totalusd']?.toString() ?? '0.0') ?? 0.0,
      estado: json['estado']?.toString().toLowerCase() ?? 'pendiente',
      totalItems: json['total_items'] ?? parsedDetalles.fold<int>(0, (sum, d) => sum + d.cantidad),
      detalles: parsedDetalles,
    );
  }

  bool get isPendiente => estado == 'pendiente';
  bool get isEnviada => estado == 'enviada';
  bool get isRecibidaTotal => estado == 'recibida_total';
  bool get isCancelada => estado == 'cancelada';

  String get estadoLabel {
    switch (estado) {
      case 'pendiente':
        return 'Pendiente';
      case 'enviada':
        return 'Aprobada / Enviada';
      case 'recibida_total':
        return 'Recibida en Almacén';
      case 'cancelada':
        return 'Rechazada / Cancelada';
      default:
        return estado.toUpperCase();
    }
  }
}

class CompraDetalleCreateModel {
  final int idvariante;
  final String nombreProducto;
  final String sku;
  final int cantidad;
  final double costounitariousd;

  CompraDetalleCreateModel({
    required this.idvariante,
    required this.nombreProducto,
    required this.sku,
    required this.cantidad,
    required this.costounitariousd,
  });

  double get subtotal => cantidad * costounitariousd;

  Map<String, dynamic> toJson() {
    return {
      'idvariante': idvariante,
      'cantidad': cantidad,
      'costounitariousd': costounitariousd.toStringAsFixed(2),
    };
  }
}

class CompraCreateModel {
  final int idproveedor;
  final String numeroorden;
  final String fechacompra;
  final List<CompraDetalleCreateModel> detalles;

  CompraCreateModel({
    required this.idproveedor,
    required this.numeroorden,
    required this.fechacompra,
    required this.detalles,
  });

  Map<String, dynamic> toJson() {
    return {
      'idproveedor': idproveedor,
      'numeroorden': numeroorden.trim(),
      'fechacompra': fechacompra,
      'detalles': detalles.map((d) => d.toJson()).toList(),
    };
  }
}

class ActorModel {
  final int idactor;
  final String nombre;
  final String razonsocial;
  final String tipoactor;

  ActorModel({
    required this.idactor,
    required this.nombre,
    required this.razonsocial,
    required this.tipoactor,
  });

  factory ActorModel.fromJson(Map<String, dynamic> json) {
    return ActorModel(
      idactor: json['idactor'] ?? 0,
      nombre: json['nombre'] ?? json['razonsocial'] ?? '',
      razonsocial: json['razonsocial'] ?? json['nombre'] ?? '',
      tipoactor: json['tipoactor'] ?? '',
    );
  }

  String get displayName => razonsocial.isNotEmpty ? razonsocial : nombre;
}

class CatalogItemModel {
  final int idcatalogotenant;
  final int idvariante;
  final String skuinterno;
  final double precioventa;
  final double costopromedio;
  final String productoNombre;
  final String sku;
  final String? color;
  final String? capacidad;

  CatalogItemModel({
    required this.idcatalogotenant,
    required this.idvariante,
    required this.skuinterno,
    required this.precioventa,
    required this.costopromedio,
    required this.productoNombre,
    required this.sku,
    this.color,
    this.capacidad,
  });

  factory CatalogItemModel.fromJson(Map<String, dynamic> json) {
    final v = json['variante'] as Map<String, dynamic>? ?? {};
    return CatalogItemModel(
      idcatalogotenant: json['idcatalogotenant'] ?? 0,
      idvariante: json['idvariante'] ?? v['idvariante'] ?? 0,
      skuinterno: json['skuinterno'] ?? '',
      precioventa: double.tryParse(json['precioventa']?.toString() ?? '0.0') ?? 0.0,
      costopromedio: double.tryParse(json['costopromedio']?.toString() ?? '0.0') ?? 0.0,
      productoNombre: json['producto_nombre'] ?? v['producto_nombre'] ?? 'iPhone / Producto',
      sku: v['sku'] ?? json['skuinterno'] ?? 'SKU',
      color: v['color'],
      capacidad: v['capacidad'],
    );
  }

  String get displayName {
    final details = [if (color != null) color, if (capacidad != null) capacidad].join(' - ');
    return '$sku ${details.isNotEmpty ? "($details)" : ""}';
  }
}
