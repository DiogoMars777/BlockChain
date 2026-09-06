class TenantModel {
  final int idtenant;
  final String nombre;
  final String razonsocial;
  final String nit;
  final String email;
  final String? telefono;
  final bool activo;
  final String? fechacreacion;

  TenantModel({
    required this.idtenant,
    required this.nombre,
    required this.razonsocial,
    required this.nit,
    required this.email,
    this.telefono,
    required this.activo,
    this.fechacreacion,
  });

  factory TenantModel.fromJson(Map<String, dynamic> json) {
    return TenantModel(
      idtenant: json['idtenant'] is int
          ? json['idtenant']
          : int.tryParse(json['idtenant']?.toString() ?? '1') ?? 1,
      nombre: json['nombre'] ?? json['name'] ?? 'Empresa',
      razonsocial: json['razonsocial'] ?? json['razon_social'] ?? json['nombre'] ?? '',
      nit: json['nit'] ?? '',
      email: json['email'] ?? '',
      telefono: json['telefono'],
      activo: json['activo'] ?? json['is_active'] ?? true,
      fechacreacion: json['fechacreacion'] ?? json['created_at'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'idtenant': idtenant,
      'nombre': nombre,
      'razonsocial': razonsocial,
      'nit': nit,
      'email': email,
      'telefono': telefono,
      'activo': activo,
      'fechacreacion': fechacreacion,
    };
  }
}
