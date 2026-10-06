import 'dart:convert';

import 'package:flutter/foundation.dart';
import 'package:flutter_tts/flutter_tts.dart';
import 'package:http/http.dart' as http;

import '../core/api_config.dart';
import '../core/secure_storage.dart';
import '../models/recommendation_model.dart';

class RecommendationController extends ChangeNotifier {
  final FlutterTts _flutterTts = FlutterTts();

  static const List<String> priorityOptions = ['todas', 'critica', 'alta', 'media', 'baja'];

  bool _isLoading = false;
  bool _isPlayingAudio = false;
  int? _speakingId;
  String _priorityFilter = 'todas';
  String _searchQuery = '';
  String? _errorMessage;
  PricingRecommendationsModel? _recommendations;

  bool get isLoading => _isLoading;
  bool get isPlayingAudio => _isPlayingAudio;
  int? get speakingId => _speakingId;
  String get priorityFilter => _priorityFilter;
  String get searchQuery => _searchQuery;
  String? get errorMessage => _errorMessage;
  PricingRecommendationsModel? get recommendations => _recommendations;
  bool get hasRecommendations => _recommendations != null;

  RecommendationController() {
    _initTts();
  }

  Future<void> _initTts() async {
    try {
      await _flutterTts.setLanguage('es');
      await _flutterTts.setSpeechRate(0.5);
      await _flutterTts.setVolume(1.0);
      await _flutterTts.setPitch(1.0);

      _flutterTts.setCompletionHandler(() {
        _isPlayingAudio = false;
        _speakingId = null;
        notifyListeners();
      });

      _flutterTts.setErrorHandler((_) {
        _isPlayingAudio = false;
        _speakingId = null;
        notifyListeners();
      });
    } catch (e) {
      debugPrint('[Recommendations TTS Error]: $e');
    }
  }

  /// Genera las recomendaciones de pricing e inventario para el tenant del usuario
  Future<void> generateRecommendations({int topN = 12}) async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      final token = await SecureStorageService.getToken();
      final uri = Uri.parse(ApiConfig.pricingRecommendations);

      final response = await http
          .post(
            uri,
            headers: {
              'Content-Type': 'application/json',
              if (token != null) 'Authorization': 'Bearer $token',
            },
            body: jsonEncode({'top_n': topN}),
          )
          .timeout(const Duration(seconds: 25));

      if (response.statusCode == 200) {
        final data = jsonDecode(utf8.decode(response.bodyBytes));
        _recommendations = PricingRecommendationsModel.fromJson(data);
      } else {
        String message = 'Error al generar recomendaciones con IA.';
        try {
          final err = jsonDecode(utf8.decode(response.bodyBytes));
          message = err['detail'] ?? message;
        } catch (_) {}
        _errorMessage = message;
      }
    } catch (e) {
      _errorMessage = 'No se pudo conectar con el servidor: $e';
    }

    _isLoading = false;
    notifyListeners();
  }

  void setPriorityFilter(String priority) {
    _priorityFilter = priority;
    notifyListeners();
  }

  void setSearchQuery(String query) {
    _searchQuery = query.trim().toLowerCase();
    notifyListeners();
  }

  List<PricingRecommendationModel> get filteredRecommendations {
    var items = _recommendations?.recomendaciones ?? [];
    if (_priorityFilter != 'todas') {
      items = items.where((r) => r.prioridad == _priorityFilter).toList();
    }
    if (_searchQuery.isNotEmpty) {
      items = items.where((r) {
        final t = r.titulo.toLowerCase();
        final p = (r.producto ?? '').toLowerCase();
        final s = (r.sku ?? '').toLowerCase();
        final j = r.justificacion.toLowerCase();
        final a = r.accionSugerida.toLowerCase();
        return t.contains(_searchQuery) ||
            p.contains(_searchQuery) ||
            s.contains(_searchQuery) ||
            j.contains(_searchQuery) ||
            a.contains(_searchQuery);
      }).toList();
    }
    return items;
  }

  int countByPriority(String priority) {
    final items = _recommendations?.recomendaciones ?? [];
    if (priority == 'todas') return items.length;
    return items.where((r) => r.prioridad == priority).length;
  }

  /// Lee en voz alta una recomendación específica
  Future<void> speakRecommendation(PricingRecommendationModel rec) async {
    if (_isPlayingAudio && _speakingId == rec.idvariante) {
      await stopSpeaking();
      return;
    }

    await stopSpeaking();

    final texto =
        '${rec.titulo}. ${rec.justificacion}. Acción sugerida: ${rec.accionSugerida}';

    try {
      _isPlayingAudio = true;
      _speakingId = rec.idvariante;
      notifyListeners();
      await _flutterTts.speak(texto);
    } catch (e) {
      debugPrint('[Recommendations TTS Speak Error]: $e');
      _isPlayingAudio = false;
      _speakingId = null;
      notifyListeners();
    }
  }

  /// Lee en voz alta el resumen de la recomendación más prioritaria
  Future<void> speakSummary() async {
    if (_isPlayingAudio) {
      await stopSpeaking();
      return;
    }

    final items = filteredRecommendations.isNotEmpty
        ? filteredRecommendations
        : (_recommendations?.recomendaciones ?? []);

    if (items.isEmpty) return;

    final principal = items.first;
    final texto =
        '${principal.titulo}. ${principal.justificacion}. Acción sugerida: ${principal.accionSugerida}';

    try {
      _isPlayingAudio = true;
      _speakingId = principal.idvariante;
      notifyListeners();
      await _flutterTts.speak(texto);
    } catch (e) {
      debugPrint('[Recommendations TTS Speak Error]: $e');
      _isPlayingAudio = false;
      _speakingId = null;
      notifyListeners();
    }
  }

  Future<void> stopSpeaking() async {
    try {
      await _flutterTts.stop();
    } catch (_) {}
    _isPlayingAudio = false;
    _speakingId = null;
    notifyListeners();
  }

  void clear() {
    _recommendations = null;
    _errorMessage = null;
    _isLoading = false;
    _priorityFilter = 'todas';
    _searchQuery = '';
    _speakingId = null;
    notifyListeners();
  }

  @override
  void dispose() {
    _flutterTts.stop();
    super.dispose();
  }
}