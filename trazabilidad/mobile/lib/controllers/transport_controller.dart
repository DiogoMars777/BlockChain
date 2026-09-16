import 'package:flutter/material.dart';
import '../models/transport_model.dart';
import 'transport_service.dart';

class TransportController extends ChangeNotifier {
  List<ShipmentModel> shipments = [];
  bool isLoading = false;
  String? errorMessage;
  String? successMessage;

  String? selectedEstado;

  ShipmentTimelineModel? currentTimeline;
  bool isTimelineLoading = false;

  Future<void> loadShipments() async {
    isLoading = true;
    errorMessage = null;
    notifyListeners();

    try {
      shipments = await TransportService.fetchShipments(estado: selectedEstado);
    } catch (e) {
      errorMessage = e.toString().replaceAll('Exception: ', '');
    } finally {
      isLoading = false;
      notifyListeners();
    }
  }

  void filterByEstado(String? estado) {
    selectedEstado = (estado != null && estado.isNotEmpty) ? estado : null;
    loadShipments();
  }

  Future<void> loadTimeline(int idenvio) async {
    isTimelineLoading = true;
    notifyListeners();

    try {
      currentTimeline = await TransportService.fetchTimeline(idenvio);
    } catch (e) {
      errorMessage = e.toString().replaceAll('Exception: ', '');
    } finally {
      isTimelineLoading = false;
      notifyListeners();
    }
  }

  Future<bool> recordEvent({
    required int idenvio,
    required String tipoevento,
    required int idubicacion,
    String? descripcion,
    TransportConditionModel? condiciones,
  }) async {
    isLoading = true;
    errorMessage = null;
    notifyListeners();

    try {
      await TransportService.recordEvent(
        idenvio: idenvio,
        tipoevento: tipoevento,
        idubicacion: idubicacion,
        descripcion: descripcion,
        condiciones: condiciones,
      );
      successMessage = 'Evento de transporte registrado exitosamente.';
      await loadShipments();
      await loadTimeline(idenvio);
      return true;
    } catch (e) {
      errorMessage = e.toString().replaceAll('Exception: ', '');
      notifyListeners();
      return false;
    } finally {
      isLoading = false;
      notifyListeners();
    }
  }
}
