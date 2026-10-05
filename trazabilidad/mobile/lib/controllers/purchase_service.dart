import 'dart:convert';
import 'package:http/http.dart' as http;
import '../core/api_config.dart';
import '../core/secure_storage.dart';
import '../models/purchase_model.dart';

class PurchaseService {
  static const Duration _timeout = Duration(seconds: 10);

  static Future<Map<String, String>> _getHeaders() async {
    final token = await SecureStorageService.getToken();
    return {
      'Content-Type': 'application/json',
      if (token != null) 'Authorization': 'Bearer $token',
    };
  }

  /// CU-010: Listar órdenes de compra con filtro opcional de estado
  static Future<List<CompraModel>> fetchPurchases({
    String? estado,
    int skip = 0,
    int limit = 50,
  }) async {
    final headers = await _getHeaders();
    final queryParams = <String, String>{
      'skip': skip.toString(),
      'limit': limit.toString(),
    };
    if (estado != null && estado.trim().isNotEmpty) {
      queryParams['estado'] = estado.trim();
    }

    final uri = Uri.parse(ApiConfig.purchases).replace(queryParameters: queryParams);

    final response = await http.get(uri, headers: headers).timeout(_timeout);

    if (response.statusCode == 200) {
      final data = jsonDecode(utf8.decode(response.bodyBytes));
      final List items = data['items'] ?? [];
      return items.map((e) => CompraModel.fromJson(e as Map<String, dynamic>)).toList();
    } else {
      final err = jsonDecode(utf8.decode(response.bodyBytes));
      throw Exception(err['detail'] ?? 'Error al obtener órdenes de compra.');
    }
  }

  /// CU-010: Obtener detalle completo de una orden
  static Future<CompraModel> getPurchase(int idcompra) async {
    final headers = await _getHeaders();
    final uri = Uri.parse('${ApiConfig.purchases}/$idcompra');

    final response = await http.get(uri, headers: headers).timeout(_timeout);

    if (response.statusCode == 200) {
      final data = jsonDecode(utf8.decode(response.bodyBytes));
      return CompraModel.fromJson(data);
    } else {
      final err = jsonDecode(utf8.decode(response.bodyBytes));
      throw Exception(err['detail'] ?? 'Orden no encontrada.');
    }
  }

  /// CU-010: Crear una nueva orden de compra
  static Future<CompraModel> createPurchase(CompraCreateModel request) async {
    final headers = await _getHeaders();
    final uri = Uri.parse(ApiConfig.purchases);

    final response = await http
        .post(uri, headers: headers, body: jsonEncode(request.toJson()))
        .timeout(_timeout);

    final data = jsonDecode(utf8.decode(response.bodyBytes));

    if (response.statusCode == 201 || response.statusCode == 200) {
      return CompraModel.fromJson(data);
    } else {
      String msg = data['detail'] is String
          ? data['detail']
          : (data['detail'] is List ? data['detail'][0]['msg'] : 'Error al registrar orden de compra');
      throw Exception(msg);
    }
  }

  /// CU-011: Aprobar orden de compra
  static Future<CompraModel> approvePurchase(int idcompra) async {
    final headers = await _getHeaders();
    final uri = Uri.parse('${ApiConfig.purchases}/$idcompra/approve');

    final response = await http.patch(uri, headers: headers).timeout(_timeout);

    final data = jsonDecode(utf8.decode(response.bodyBytes));

    if (response.statusCode == 200) {
      final compraData = data['compra'] ?? data;
      return CompraModel.fromJson(compraData);
    } else {
      throw Exception(data['detail'] ?? 'Error al aprobar orden de compra.');
    }
  }

  /// CU-011: Rechazar orden de compra con motivo
  static Future<CompraModel> rejectPurchase(int idcompra, String motivo) async {
    final headers = await _getHeaders();
    final uri = Uri.parse('${ApiConfig.purchases}/$idcompra/reject');

    final response = await http
        .patch(uri, headers: headers, body: jsonEncode({'motivo': motivo}))
        .timeout(_timeout);

    final data = jsonDecode(utf8.decode(response.bodyBytes));

    if (response.statusCode == 200) {
      final compraData = data['compra'] ?? data;
      return CompraModel.fromJson(compraData);
    } else {
      throw Exception(data['detail'] ?? 'Error al rechazar orden de compra.');
    }
  }

  /// Cargar proveedores para el formulario de compra
  static Future<List<ActorModel>> fetchProveedores() async {
    final headers = await _getHeaders();
    final uri = Uri.parse(ApiConfig.actors).replace(queryParameters: {'limit': '100'});

    try {
      final response = await http.get(uri, headers: headers).timeout(_timeout);
      if (response.statusCode == 200) {
        final data = jsonDecode(utf8.decode(response.bodyBytes));
        final List items = data['items'] ?? [];
        return items.map((e) => ActorModel.fromJson(e as Map<String, dynamic>)).toList();
      }
    } catch (_) {}
    return [];
  }

  /// Cargar variantes del catálogo para el formulario de compra
  static Future<List<CatalogItemModel>> fetchCatalogItems() async {
    final headers = await _getHeaders();
    final uri = Uri.parse(ApiConfig.tenantCatalog).replace(queryParameters: {'limit': '100'});

    try {
      final response = await http.get(uri, headers: headers).timeout(_timeout);
      if (response.statusCode == 200) {
        final data = jsonDecode(utf8.decode(response.bodyBytes));
        final List items = data['items'] ?? [];
        return items
            .map((e) => CatalogItemModel.fromJson(e as Map<String, dynamic>))
            .toList();
      }
    } catch (_) {}
    return [];
  }
}
