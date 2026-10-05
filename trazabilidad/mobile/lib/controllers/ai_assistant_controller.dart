import 'dart:convert';
import 'dart:io';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import 'package:speech_to_text/speech_to_text.dart';
import 'package:flutter_tts/flutter_tts.dart';
import 'package:path_provider/path_provider.dart';
import 'package:open_filex/open_filex.dart';
import 'package:share_plus/share_plus.dart';

import '../core/api_config.dart';
import '../core/secure_storage.dart';
import '../models/ai_report_model.dart';

class AiAssistantController extends ChangeNotifier {
  final SpeechToText _speechToText = SpeechToText();
  final FlutterTts _flutterTts = FlutterTts();

  bool _isSpeechInitialized = false;
  bool _isListening = false;
  bool _isLoading = false;
  bool _isPlayingAudio = false;
  bool _isDownloading = false;

  String _spokenText = '';
  String? _errorMessage;
  VoiceReportModel? _currentReport;

  // Getters
  bool get isListening => _isListening;
  bool get isLoading => _isLoading;
  bool get isPlayingAudio => _isPlayingAudio;
  bool get isDownloading => _isDownloading;
  String get spokenText => _spokenText;
  String? get errorMessage => _errorMessage;
  VoiceReportModel? get currentReport => _currentReport;
  bool get hasReport => _currentReport != null;

  AiAssistantController() {
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
        notifyListeners();
      });

      _flutterTts.setErrorHandler((_) {
        _isPlayingAudio = false;
        notifyListeners();
      });
    } catch (e) {
      debugPrint('[AI Assistant TTS Error]: $e');
    }
  }

  Future<bool> initSpeech() async {
    if (_isSpeechInitialized) return true;
    try {
      _isSpeechInitialized = await _speechToText.initialize(
        onError: (err) {
          debugPrint('[SpeechToText Error]: ${err.errorMsg}');
          _isListening = false;
          notifyListeners();
        },
        onStatus: (status) {
          if (status == 'done' || status == 'notListening') {
            _isListening = false;
            notifyListeners();
          }
        },
      );
      return _isSpeechInitialized;
    } catch (e) {
      debugPrint('[SpeechToText Init Exception]: $e');
      return false;
    }
  }

  Future<void> startListening() async {
    _errorMessage = null;
    final available = await initSpeech();
    if (!available) {
      _errorMessage = 'El micrófono o reconocimiento de voz no está disponible en este dispositivo.';
      notifyListeners();
      return;
    }

    _spokenText = '';
    _isListening = true;
    notifyListeners();

    await _speechToText.listen(
      listenOptions: SpeechListenOptions(
        localeId: 'es_ES',
      ),
      onResult: (result) {
        _spokenText = result.recognizedWords;
        notifyListeners();
      },
    );
  }

  Future<void> stopListeningAndSubmit() async {
    if (_isListening) {
      await _speechToText.stop();
      _isListening = false;
      notifyListeners();
    }

    if (_spokenText.trim().isNotEmpty) {
      await submitQuery(_spokenText.trim());
    }
  }

  Future<void> cancelListening() async {
    if (_isListening) {
      await _speechToText.cancel();
      _isListening = false;
      _spokenText = '';
      notifyListeners();
    }
  }

  Future<void> submitQuery(String queryText) async {
    if (queryText.trim().isEmpty) return;

    _isLoading = true;
    _errorMessage = null;
    _spokenText = queryText;
    notifyListeners();

    try {
      final token = await SecureStorageService.getToken();
      final uri = Uri.parse(ApiConfig.aiVoiceReport);

      final response = await http
          .post(
            uri,
            headers: {
              'Content-Type': 'application/json',
              if (token != null) 'Authorization': 'Bearer $token',
            },
            body: jsonEncode({
              'query': queryText,
              'context': 'mobile_dashboard',
            }),
          )
          .timeout(const Duration(seconds: 25));

      if (response.statusCode == 200) {
        final data = jsonDecode(utf8.decode(response.bodyBytes));
        _currentReport = VoiceReportModel.fromJson(data);
        _isLoading = false;
        notifyListeners();

        // Reproducir automáticamente el resumen de voz
        if (_currentReport != null && _currentReport!.voiceSummary.isNotEmpty) {
          speakSummary();
        }
      } else {
        final err = jsonDecode(utf8.decode(response.bodyBytes));
        _errorMessage = err['detail'] ?? 'Error al procesar el reporte con IA.';
        _isLoading = false;
        notifyListeners();
      }
    } catch (e) {
      _isLoading = false;
      _errorMessage = 'No se pudo conectar con el servidor: $e';
      notifyListeners();
    }
  }

  Future<void> speakSummary() async {
    if (_currentReport == null || _currentReport!.voiceSummary.isEmpty) return;
    try {
      _isPlayingAudio = true;
      notifyListeners();
      await _flutterTts.speak(_currentReport!.voiceSummary);
    } catch (e) {
      _isPlayingAudio = false;
      notifyListeners();
    }
  }

  Future<void> stopSpeaking() async {
    try {
      await _flutterTts.stop();
      _isPlayingAudio = false;
      notifyListeners();
    } catch (_) {}
  }

  /// Descarga el documento (PDF o Excel), lo guarda localmente y lo abre o comparte
  Future<String?> downloadAndOpenReport({
    required String reportId,
    required String format, // 'pdf' o 'excel'
    bool share = false,
  }) async {
    _isDownloading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      final token = await SecureStorageService.getToken();
      final uri = Uri.parse(ApiConfig.aiReportExport(reportId, format));

      final response = await http.get(
        uri,
        headers: {
          if (token != null) 'Authorization': 'Bearer $token',
        },
      ).timeout(const Duration(seconds: 30));

      if (response.statusCode == 200) {
        final dir = await getTemporaryDirectory();
        final ext = format == 'excel' ? 'xlsx' : 'pdf';
        final fileName = 'reporte_ia_${reportId.substring(0, 8)}.$ext';
        final filePath = '${dir.path}/$fileName';

        final file = File(filePath);
        await file.writeAsBytes(response.bodyBytes);

        _isDownloading = false;
        notifyListeners();

        if (share) {
          await Share.shareXFiles(
            [XFile(filePath)],
            text: 'Reporte Oficial de Trazabilidad generado con IA',
          );
        } else {
          final openResult = await OpenFilex.open(filePath);
          if (openResult.type != ResultType.done) {
            debugPrint('[OpenFilex Warning]: ${openResult.message}');
          }
        }

        return filePath;
      } else {
        _errorMessage = 'Error ${response.statusCode} al descargar el archivo.';
        _isDownloading = false;
        notifyListeners();
        return null;
      }
    } catch (e) {
      _errorMessage = 'Error al exportar documento: $e';
      _isDownloading = false;
      notifyListeners();
      return null;
    }
  }

  void reset() {
    _currentReport = null;
    _spokenText = '';
    _errorMessage = null;
    _isListening = false;
    _isLoading = false;
    _isPlayingAudio = false;
    stopSpeaking();
    notifyListeners();
  }

  @override
  void dispose() {
    _speechToText.stop();
    _flutterTts.stop();
    super.dispose();
  }
}
