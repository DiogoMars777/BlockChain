import 'dart:async';
import 'package:flutter/foundation.dart' show debugPrint;
import 'package:http/http.dart' as http;
import 'secure_storage.dart';

class ApiConfig {
  /// Presets recomendados según el tipo de conexión:
  static const String cloudProduction = 'https://blockchain-production-8de2.up.railway.app/api/v1';
  static const String usbLocalhost = 'http://127.0.0.1:8000/api/v1';
  static const String wifiLanHost = 'http://192.168.0.103:8000/api/v1';
  static const String emulatorHost = 'http://10.0.2.2:8000/api/v1';

  static const List<String> candidateHosts = [
    cloudProduction,
    usbLocalhost,
    wifiLanHost,
    emulatorHost,
  ];

  static String _activeBaseUrl = cloudProduction;
  static bool _initialized = false;

  static String get baseUrl => _activeBaseUrl;

  /// Inicializa la configuración cargando la URL guardada o auto-detectando
  static Future<void> initialize() async {
    if (_initialized) return;
    _initialized = true;

    try {
      final saved = await SecureStorageService.getServerUrl();
      if (saved != null && saved.trim().isNotEmpty) {
        final clean = saved.trim().toLowerCase();
        // Si el usuario tenía configurado un host local antiguo, priorizar la nube
        if (clean.contains('127.0.0.1') || clean.contains('localhost') || clean.contains('10.0.2.2') || clean.contains('192.168.')) {
          _activeBaseUrl = cloudProduction;
          await SecureStorageService.saveServerUrl(cloudProduction);
          debugPrint('[ApiConfig] Migrando host local previo a la nube: $_activeBaseUrl');
          return;
        }

        _activeBaseUrl = _normalizeUrl(saved);
        debugPrint('[ApiConfig] Usando URL guardada: $_activeBaseUrl');
        return;
      }

      // Si no hay guardada, fijar nube
      _activeBaseUrl = cloudProduction;
      await SecureStorageService.saveServerUrl(cloudProduction);
      debugPrint('[ApiConfig] URL por defecto establecida en la nube: $_activeBaseUrl');
    } catch (e) {
      debugPrint('[ApiConfig] Error al inicializar: $e');
    }
  }

  /// Establece manualmente una nueva URL base y la persiste
  static Future<void> setBaseUrl(String url) async {
    _activeBaseUrl = _normalizeUrl(url);
    await SecureStorageService.saveServerUrl(_activeBaseUrl);
    debugPrint('[ApiConfig] Nueva URL base fijada: $_activeBaseUrl');
  }

  /// Normaliza la URL agregando http:// y /api/v1 si corresponde
  static String _normalizeUrl(String url) {
    var clean = url.trim();
    if (!clean.startsWith('http://') && !clean.startsWith('https://')) {
      clean = 'http://$clean';
    }
    while (clean.endsWith('/')) {
      clean = clean.substring(0, clean.length - 1);
    }
    if (!clean.endsWith('/api/v1')) {
      clean = '$clean/api/v1';
    }
    return clean;
  }

  /// Prueba si un host responde HTTP (el endpoint /auth/me responde 401 si está vivo)
  static Future<bool> testConnection(String url, {Duration timeout = const Duration(milliseconds: 1800)}) async {
    final normalized = _normalizeUrl(url);
    try {
      final uri = Uri.parse('$normalized/auth/me');
      final resp = await http.get(uri).timeout(timeout);
      return resp.statusCode > 0;
    } catch (_) {
      return false;
    }
  }

  /// Escanea candidatos en paralelo y retorna el primero que responda
  static Future<String?> autoDetectWorkingUrl() async {
    final listToTest = <String>[
      _activeBaseUrl,
      ...candidateHosts.where((h) => h != _activeBaseUrl),
    ];

    for (final candidate in listToTest) {
      final isAlive = await testConnection(candidate);
      if (isAlive) {
        return candidate;
      }
    }
    return null;
  }

  // Rutas de la API
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
  static String get purchases => '$baseUrl/purchases';
  static String get actors => '$baseUrl/actors';
  static String get tenantCatalog => '$baseUrl/tenant-catalog';
  static String get aiVoiceReport => '$baseUrl/ai/voice-report';
  static String get pricingRecommendations => '$baseUrl/tenant-catalog/recommendations';
  static String aiReportExport(String reportId, String format) => '$baseUrl/ai/reports/$reportId/export?format=$format';
}

