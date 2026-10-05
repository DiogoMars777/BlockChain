import 'dart:async';
import 'dart:convert';
import 'dart:io' show SocketException;
import 'package:http/http.dart' as http;
import '../core/api_config.dart';
import '../core/secure_storage.dart';
import '../models/auth_models.dart';
import '../models/user_model.dart';

class AuthService {
  static const Duration _timeout = Duration(seconds: 10);

  static Future<TokenResponse> login(LoginRequest request) async {
    http.Response response;
    try {
      response = await http.post(
        Uri.parse(ApiConfig.login),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode(request.toJson()),
      ).timeout(_timeout);
    } on SocketException catch (_) {
      throw Exception(
        'No se pudo conectar al servidor en ${ApiConfig.baseUrl}.\n\n'
        '• En USB físico: ejecuta en tu PC "adb reverse tcp:8000 tcp:8000".\n'
        '• En Wi-Fi: usa la IP local de tu PC (ej: http://192.168.0.103:8000/api/v1).\n'
        '• Toca "⚙️ Configurar Servidor" abajo para cambiarlo o auto-detectarlo.',
      );
    } on http.ClientException catch (e) {
      throw Exception('Fallo de conexión al backend (${ApiConfig.baseUrl}): ${e.message}');
    } on TimeoutException {
      throw Exception('Tiempo de espera agotado al conectar a ${ApiConfig.baseUrl}. Verifica que uvicorn esté corriendo.');
    } catch (e) {
      throw Exception('Error de red: $e');
    }

    dynamic responseData;
    try {
      responseData = jsonDecode(utf8.decode(response.bodyBytes));
    } catch (_) {
      throw Exception('Respuesta no válida del servidor (${response.statusCode}): ${response.body}');
    }

    if (response.statusCode == 200 && responseData is Map<String, dynamic>) {
      final tokenResp = TokenResponse.fromJson(responseData);
      await SecureStorageService.saveToken(tokenResp.accessToken);
      return tokenResp;
    } else {
      String errorMsg = 'Error al iniciar sesión (${response.statusCode}).';
      if (responseData is Map && responseData.containsKey('detail')) {
        final detail = responseData['detail'];
        if (detail is String) {
          errorMsg = detail;
        } else if (detail is List && detail.isNotEmpty) {
          errorMsg = detail.map((e) => e is Map ? e['msg'] ?? e.toString() : e.toString()).join('\n');
        }
      }
      throw Exception(errorMsg);
    }
  }

  static Future<UserModel> getMe() async {
    final token = await SecureStorageService.getToken();
    if (token == null) throw Exception('No autenticado');

    http.Response response;
    try {
      response = await http.get(
        Uri.parse(ApiConfig.me),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $token',
        },
      ).timeout(_timeout);
    } on SocketException catch (_) {
      throw Exception('No se pudo conectar con el servidor para validar sesión.');
    } catch (e) {
      throw Exception('Error de conexión: $e');
    }

    dynamic responseData;
    try {
      responseData = jsonDecode(utf8.decode(response.bodyBytes));
    } catch (_) {
      throw Exception('Respuesta inesperada del servidor.');
    }

    if (response.statusCode == 200 && responseData is Map<String, dynamic>) {
      return UserModel.fromJson(responseData);
    } else {
      await SecureStorageService.deleteToken();
      throw Exception('Sesión expirada.');
    }
  }

  static Future<MessageResponse> forgotPassword(ForgotPasswordRequest request) async {
    http.Response response;
    try {
      response = await http.post(
        Uri.parse(ApiConfig.forgotPassword),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode(request.toJson()),
      ).timeout(_timeout);
    } catch (e) {
      throw Exception('Error de conexión al solicitar recuperación: $e');
    }

    final responseData = jsonDecode(utf8.decode(response.bodyBytes));

    if (response.statusCode == 200) {
      return MessageResponse.fromJson(responseData);
    } else {
      throw Exception(responseData['detail'] ?? 'Error al solicitar recuperación.');
    }
  }

  static Future<MessageResponse> resetPassword(ResetPasswordRequest request) async {
    http.Response response;
    try {
      response = await http.post(
        Uri.parse(ApiConfig.resetPassword),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode(request.toJson()),
      ).timeout(_timeout);
    } catch (e) {
      throw Exception('Error de conexión al restablecer contraseña: $e');
    }

    final responseData = jsonDecode(utf8.decode(response.bodyBytes));

    if (response.statusCode == 200) {
      return MessageResponse.fromJson(responseData);
    } else {
      throw Exception(responseData['detail'] ?? 'Error al restablecer contraseña.');
    }
  }

  static Future<void> logout() async {
    final token = await SecureStorageService.getToken();
    if (token != null) {
      try {
        await http.post(
          Uri.parse(ApiConfig.logout),
          headers: {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer $token',
          },
        ).timeout(const Duration(seconds: 4));
      } catch (_) {}
    }
    await SecureStorageService.deleteToken();
  }
}

