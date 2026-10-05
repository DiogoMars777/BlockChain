import 'package:flutter/foundation.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

class SecureStorageService {
  static const _storage = FlutterSecureStorage(
    aOptions: AndroidOptions(
      encryptedSharedPreferences: true,
      resetOnError: true,
    ),
  );
  static const _tokenKey = 'access_token';
  static const _serverUrlKey = 'server_base_url';

  static String? _memoryToken;
  static String? _memoryServerUrl;

  static Future<void> saveToken(String token) async {
    _memoryToken = token;
    try {
      await _storage.write(key: _tokenKey, value: token);
    } catch (e) {
      debugPrint('[SecureStorageService] Warning al guardar token: $e');
    }
  }

  static Future<String?> getToken() async {
    if (_memoryToken != null && _memoryToken!.isNotEmpty) {
      return _memoryToken;
    }
    try {
      _memoryToken = await _storage.read(key: _tokenKey);
      return _memoryToken;
    } catch (e) {
      debugPrint('[SecureStorageService] Warning al leer token: $e');
      return _memoryToken;
    }
  }

  static Future<void> deleteToken() async {
    _memoryToken = null;
    try {
      await _storage.delete(key: _tokenKey);
    } catch (e) {
      debugPrint('[SecureStorageService] Warning al eliminar token: $e');
    }
  }

  static Future<void> saveServerUrl(String url) async {
    _memoryServerUrl = url;
    try {
      await _storage.write(key: _serverUrlKey, value: url);
    } catch (e) {
      debugPrint('[SecureStorageService] Warning al guardar URL servidor: $e');
    }
  }

  static Future<String?> getServerUrl() async {
    if (_memoryServerUrl != null && _memoryServerUrl!.isNotEmpty) {
      return _memoryServerUrl;
    }
    try {
      _memoryServerUrl = await _storage.read(key: _serverUrlKey);
      return _memoryServerUrl;
    } catch (e) {
      debugPrint('[SecureStorageService] Warning al leer URL servidor: $e');
      return _memoryServerUrl;
    }
  }
}

