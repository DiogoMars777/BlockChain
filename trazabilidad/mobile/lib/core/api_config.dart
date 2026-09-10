class ApiConfig {
  // Backend de producción en Railway
  static const String baseUrl = 'https://blockchain-production-8de2.up.railway.app/api/v1';

  static const String login = '$baseUrl/auth/login';
  static const String refresh = '$baseUrl/auth/refresh';
  static const String logout = '$baseUrl/auth/logout';
  static const String me = '$baseUrl/auth/me';
  static const String forgotPassword = '$baseUrl/auth/forgot-password';
  static const String resetPassword = '$baseUrl/auth/reset-password';
  static const String notifications = '$baseUrl/notifications';
  static const String bitacora = '$baseUrl/bitacora';
}
