import 'package:flutter/material.dart';
import '../models/purchase_model.dart';
import 'purchase_service.dart';

class PurchaseController extends ChangeNotifier {
  List<CompraModel> _purchases = [];
  bool _isLoading = false;
  String? _selectedEstado;
  String? _errorMessage;
  String? _successMessage;

  List<ActorModel> _proveedores = [];
  List<CatalogItemModel> _catalogItems = [];
  bool _isLoadingFormData = false;

  List<CompraModel> get purchases => _purchases;
  bool get isLoading => _isLoading;
  String? get selectedEstado => _selectedEstado;
  String? get errorMessage => _errorMessage;
  String? get successMessage => _successMessage;
  List<ActorModel> get proveedores => _proveedores;
  List<CatalogItemModel> get catalogItems => _catalogItems;
  bool get isLoadingFormData => _isLoadingFormData;

  int get pendingCount => _purchases.where((p) => p.isPendiente).length;
  double get totalUSD => _purchases.fold(0.0, (sum, p) => sum + p.totalusd);

  void clearMessages() {
    _errorMessage = null;
    _successMessage = null;
    notifyListeners();
  }

  Future<void> loadPurchases() async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      _purchases = await PurchaseService.fetchPurchases(estado: _selectedEstado);
      _isLoading = false;
      notifyListeners();
    } catch (e) {
      _isLoading = false;
      _errorMessage = e.toString().replaceAll('Exception: ', '');
      notifyListeners();
    }
  }

  void setFilter(String? estado) {
    if (_selectedEstado == estado) return;
    _selectedEstado = estado;
    loadPurchases();
  }

  Future<bool> approve(int idcompra) async {
    _isLoading = true;
    _errorMessage = null;
    _successMessage = null;
    notifyListeners();

    try {
      final updated = await PurchaseService.approvePurchase(idcompra);
      final index = _purchases.indexWhere((p) => p.idcompra == idcompra);
      if (index != -1) {
        _purchases[index] = updated;
      } else {
        await loadPurchases();
      }
      _successMessage = 'Orden #${updated.numeroorden} aprobada exitosamente y enviada.';
      _isLoading = false;
      notifyListeners();
      return true;
    } catch (e) {
      _isLoading = false;
      _errorMessage = e.toString().replaceAll('Exception: ', '');
      notifyListeners();
      return false;
    }
  }

  Future<bool> reject(int idcompra, String motivo) async {
    if (motivo.trim().isEmpty) {
      _errorMessage = 'El motivo de rechazo es obligatorio.';
      notifyListeners();
      return false;
    }

    _isLoading = true;
    _errorMessage = null;
    _successMessage = null;
    notifyListeners();

    try {
      final updated = await PurchaseService.rejectPurchase(idcompra, motivo);
      final index = _purchases.indexWhere((p) => p.idcompra == idcompra);
      if (index != -1) {
        _purchases[index] = updated;
      } else {
        await loadPurchases();
      }
      _successMessage = 'Orden #${updated.numeroorden} rechazada correctamente.';
      _isLoading = false;
      notifyListeners();
      return true;
    } catch (e) {
      _isLoading = false;
      _errorMessage = e.toString().replaceAll('Exception: ', '');
      notifyListeners();
      return false;
    }
  }

  Future<bool> create(CompraCreateModel request) async {
    _isLoading = true;
    _errorMessage = null;
    _successMessage = null;
    notifyListeners();

    try {
      final nueva = await PurchaseService.createPurchase(request);
      _purchases.insert(0, nueva);
      _successMessage = 'Orden #${nueva.numeroorden} registrada correctamente.';
      _isLoading = false;
      notifyListeners();
      return true;
    } catch (e) {
      _isLoading = false;
      _errorMessage = e.toString().replaceAll('Exception: ', '');
      notifyListeners();
      return false;
    }
  }

  Future<void> loadFormData() async {
    if (_proveedores.isNotEmpty && _catalogItems.isNotEmpty) return;
    _isLoadingFormData = true;
    notifyListeners();

    try {
      final results = await Future.wait([
        PurchaseService.fetchProveedores(),
        PurchaseService.fetchCatalogItems(),
      ]);
      _proveedores = results[0] as List<ActorModel>;
      _catalogItems = results[1] as List<CatalogItemModel>;
    } catch (_) {}

    _isLoadingFormData = false;
    notifyListeners();
  }
}
