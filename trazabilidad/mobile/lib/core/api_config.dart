class ApiConfig {
  // Use 10.0.2.2 for Android Emulator, or localhost for iOS / Web / Desktop
  static const String baseUrl = 'http://10.0.2.2:8000/api/v1';

  static const String login = '$baseUrl/auth/login';
  static const String refresh = '$baseUrl/auth/refresh';
  static const String logout = '$baseUrl/auth/logout';
  static const String me = '$baseUrl/auth/me';
  static const String forgotPassword = '$baseUrl/auth/forgot-password';
  static const String resetPassword = '$baseUrl/auth/reset-password';
  static const String notifications = '$baseUrl/notifications';
}
