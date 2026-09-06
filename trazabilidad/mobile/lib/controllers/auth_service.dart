import 'dart:convert';
import 'package:http/http.dart' as http;
import '../core/api_config.dart';
import '../core/secure_storage.dart';
import '../models/auth_models.dart';
import '../models/user_model.dart';

class AuthService {
  static Future<TokenResponse> login(LoginRequest request) async {
    final response = await http.post(
      Uri.parse(ApiConfig.login),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode(request.toJson()),
    );

    final responseData = jsonDecode(response.body);

    if (response.statusCode == 200) {
      final tokenResp = TokenResponse.fromJson(responseData);
      await SecureStorageService.saveToken(tokenResp.accessToken);
      return tokenResp;
    } else {
      throw Exception(responseData['detail'] ?? 'Error al iniciar sesión.');
    }
  }

  static Future<UserModel> getMe() async {
    final token = await SecureStorageService.getToken();
    if (token == null) throw Exception('No autenticado');

    final response = await http.get(
      Uri.parse(ApiConfig.me),
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer $token',
      },
    );

    final responseData = jsonDecode(response.body);

    if (response.statusCode == 200) {
      return UserModel.fromJson(responseData);
    } else {
      await SecureStorageService.deleteToken();
      throw Exception('Sesión expirada.');
    }
  }

  static Future<MessageResponse> forgotPassword(ForgotPasswordRequest request) async {
    final response = await http.post(
      Uri.parse(ApiConfig.forgotPassword),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode(request.toJson()),
    );

    final responseData = jsonDecode(response.body);

    if (response.statusCode == 200) {
      return MessageResponse.fromJson(responseData);
    } else {
      throw Exception(responseData['detail'] ?? 'Error al solicitar recuperación.');
    }
  }

  static Future<MessageResponse> resetPassword(ResetPasswordRequest request) async {
    final response = await http.post(
      Uri.parse(ApiConfig.resetPassword),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode(request.toJson()),
    );

    final responseData = jsonDecode(response.body);

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
        );
      } catch (_) {}
    }
    await SecureStorageService.deleteToken();
  }
}
