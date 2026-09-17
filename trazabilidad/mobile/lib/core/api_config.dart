class ApiConfig {
  // Backend local: http://127.0.0.1:8000/api/v1 (en emulador Android usar http://10.0.2.2:8000/api/v1)
  static const String baseUrl = 'http://127.0.0.1:8000/api/v1';

  static const String login = '$baseUrl/auth/login';
  static const String refresh = '$baseUrl/auth/refresh';
  static const String logout = '$baseUrl/auth/logout';
  static const String me = '$baseUrl/auth/me';
  static const String forgotPassword = '$baseUrl/auth/forgot-password';
  static const String resetPassword = '$baseUrl/auth/reset-password';
  static const String notifications = '$baseUrl/notifications';
  static const String bitacora = '$baseUrl/bitacora';
  static const String qrUnits = '$baseUrl/qr/units';
  static const String qrGenerate = '$baseUrl/qr/generate';
  static const String qrBase = '$baseUrl/qr';
  static const String shipments = '$baseUrl/shipments';
}
