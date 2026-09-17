import 'dart:io' show Platform;
import 'package:flutter/foundation.dart' show kIsWeb;

class ApiConfig {
  /// Detecta automáticamente el host adecuado:
  /// - En Emulador Android: 'http://10.0.2.2:8000/api/v1' (10.0.2.2 es el alias del host PC)
  /// - En Web o Windows Desktop: 'http://127.0.0.1:8000/api/v1'
  static String get baseUrl {
    if (kIsWeb) {
      return 'http://127.0.0.1:8000/api/v1';
    }
    try {
      if (Platform.isAndroid) {
        return 'http://10.0.2.2:8000/api/v1';
      }
    } catch (_) {}
    return 'http://127.0.0.1:8000/api/v1';
  }

  static String get login => '$baseUrl/auth/login';
  static String get refresh => '$baseUrl/auth/refresh';
  static String get logout => '$baseUrl/auth/logout';
  static String get me => '$baseUrl/auth/me';
  static String get forgotPassword => '$baseUrl/auth/forgot-password';
  static String get resetPassword => '$baseUrl/auth/reset-password';
  static String get notifications => '$baseUrl/notifications';
  static String get bitacora => '$baseUrl/bitacora';
  static String get qrUnits => '$baseUrl/qr/units';
  static String get qrGenerate => '$baseUrl/qr/generate';
  static String get qrBase => '$baseUrl/qr';
  static String get shipments => '$baseUrl/shipments';
}
