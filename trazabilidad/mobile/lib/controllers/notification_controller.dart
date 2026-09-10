import 'dart:convert';
import 'package:http/http.dart' as http;
import '../core/api_config.dart';
import '../core/secure_storage.dart';
import '../models/notification_model.dart';
import 'auth_controller.dart';

class NotificationController {
  final AuthController authController;

  NotificationController({required this.authController});

  List<NotificationModel> notifications = [];
  int unreadCount = 0;
  bool isLoading = false;
  String? errorMessage;

  Future<void> fetchNotifications() async {
    isLoading = true;
    errorMessage = null;

    try {
      final token = await SecureStorageService.getToken();
      if (token == null) {
        errorMessage = 'No hay sesión activa.';
        isLoading = false;
        return;
      }

      final url = Uri.parse(ApiConfig.notifications);
      final response = await http.get(
        url,
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $token',
        },
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        unreadCount = data['unread_count'] ?? 0;
        final List items = data['items'] ?? [];
        notifications = items.map((x) => NotificationModel.fromJson(x)).toList();
      } else {
        errorMessage = 'Error al cargar notificaciones (${response.statusCode})';
      }
    } catch (e) {
      errorMessage = 'Error de conexión: $e';
    } finally {
      isLoading = false;
    }
  }

  Future<bool> markAsRead(int idnotificacion) async {
    try {
      final token = await SecureStorageService.getToken();
      if (token == null) return false;

      final url = Uri.parse('${ApiConfig.notifications}/$idnotificacion/read');
      final response = await http.patch(
        url,
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $token',
        },
      );

      if (response.statusCode == 200) {
        await fetchNotifications();
        return true;
      }
    } catch (e) {
      // Ignorar excepción
    }
    return false;
  }
}
