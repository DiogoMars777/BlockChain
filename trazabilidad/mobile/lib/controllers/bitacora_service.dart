import 'dart:convert';
import 'package:http/http.dart' as http;
import '../core/api_config.dart';
import '../core/secure_storage.dart';
import '../models/bitacora_model.dart';

class BitacoraService {
  static Future<BitacoraListResponse> fetchBitacora({
    String? accion,
    String? entidad,
    int skip = 0,
    int limit = 50,
  }) async {
    final token = await SecureStorageService.getToken();
    if (token == null) {
      throw Exception('No autenticado. Inicie sesión nuevamente.');
    }

    final queryParams = <String, String>{
      'skip': skip.toString(),
      'limit': limit.toString(),
    };

    if (accion != null && accion.trim().isNotEmpty && accion.trim().toUpperCase() != 'TODOS') {
      queryParams['accion'] = accion.trim();
    }
    if (entidad != null && entidad.trim().isNotEmpty) {
      queryParams['entidad'] = entidad.trim();
    }

    final uri = Uri.parse(ApiConfig.bitacora).replace(queryParameters: queryParams);

    final response = await http.get(
      uri,
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer $token',
      },
    );

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      return BitacoraListResponse.fromJson(data);
    } else {
      try {
        final errorData = jsonDecode(response.body);
        throw Exception(errorData['detail'] ?? 'Error al consultar la bitácora (${response.statusCode})');
      } catch (e) {
        if (e is Exception) rethrow;
        throw Exception('Error del servidor al consultar la bitácora (${response.statusCode})');
      }
    }
  }
}
