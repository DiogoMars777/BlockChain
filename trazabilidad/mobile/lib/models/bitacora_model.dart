class BitacoraItem {
  final int idbitacora;
  final int idusuariotenant;
  final String accion;
  final String entidad;
  final int? identidad;
  final String? ip;
  final DateTime fechahora;

  BitacoraItem({
    required this.idbitacora,
    required this.idusuariotenant,
    required this.accion,
    required this.entidad,
    this.identidad,
    this.ip,
    required this.fechahora,
  });

  factory BitacoraItem.fromJson(Map<String, dynamic> json) {
    DateTime parsedFecha;
    try {
      final raw = (json['fechahora'] ?? '').toString().trim();
      if (raw.endsWith('Z') || raw.contains('+') || (raw.lastIndexOf('-') > 10)) {
        // Si el string incluye zona horaria explícita (como UTC o ISO con offset)
        final utcDate = DateTime.parse(raw).toUtc();
        // Convertir a hora oficial de Bolivia (BOT = UTC-4)
        parsedFecha = utcDate.subtract(const Duration(hours: 4));
      } else {
        // El backend ya lo registra y devuelve directamente en hora oficial de Bolivia
        parsedFecha = DateTime.parse(raw);
      }
    } catch (_) {
      parsedFecha = DateTime.now();
    }

    return BitacoraItem(
      idbitacora: json['idbitacora'] ?? 0,
      idusuariotenant: json['idusuariotenant'] ?? 0,
      accion: (json['accion'] ?? 'DESCONOCIDO').toString().trim().toUpperCase(),
      entidad: (json['entidad'] ?? 'Sistema').toString().trim(),
      identidad: json['identidad'],
      ip: json['ip'] ?? '127.0.0.1',
      fechahora: parsedFecha,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'idbitacora': idbitacora,
      'idusuariotenant': idusuariotenant,
      'accion': accion,
      'entidad': entidad,
      'identidad': identidad,
      'ip': ip,
      'fechahora': fechahora.toIso8601String(),
    };
  }

  String get formattedFecha {
    final d = fechahora.day.toString().padLeft(2, '0');
    final m = fechahora.month.toString().padLeft(2, '0');
    final y = fechahora.year;
    final h = fechahora.hour.toString().padLeft(2, '0');
    final min = fechahora.minute.toString().padLeft(2, '0');
    final sec = fechahora.second.toString().padLeft(2, '0');
    return '$d/$m/$y $h:$min:$sec';
  }
}

class BitacoraListResponse {
  final int total;
  final List<BitacoraItem> items;

  BitacoraListResponse({
    required this.total,
    required this.items,
  });

  factory BitacoraListResponse.fromJson(Map<String, dynamic> json) {
    final rawList = json['items'] as List<dynamic>? ?? [];
    final parsedItems = rawList
        .map((item) => BitacoraItem.fromJson(item as Map<String, dynamic>))
        .toList();

    return BitacoraListResponse(
      total: json['total'] ?? parsedItems.length,
      items: parsedItems,
    );
  }
}
