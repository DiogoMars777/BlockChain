import 'package:flutter/material.dart';
import '../models/bitacora_model.dart';
import 'bitacora_service.dart';

class BitacoraController extends ChangeNotifier {
  List<BitacoraItem> _items = [];
  int _total = 0;
  bool _isLoading = false;
  String? _errorMessage;
  String _selectedFiltro = 'TODOS';
  String _searchQuery = '';

  List<BitacoraItem> get items {
    if (_searchQuery.trim().isEmpty) {
      return _items;
    }
    final q = _searchQuery.trim().toLowerCase();
    return _items.where((it) {
      return it.accion.toLowerCase().contains(q) ||
          it.entidad.toLowerCase().contains(q) ||
          (it.ip != null && it.ip!.toLowerCase().contains(q)) ||
          it.idusuariotenant.toString().contains(q) ||
          it.formattedFecha.toLowerCase().contains(q);
    }).toList();
  }

  int get total => _total;
  bool get isLoading => _isLoading;
  String? get errorMessage => _errorMessage;
  String get selectedFiltro => _selectedFiltro;
  String get searchQuery => _searchQuery;

  Future<void> fetchBitacora({String? accion, bool showLoading = true}) async {
    if (showLoading) {
      _isLoading = true;
      _errorMessage = null;
      notifyListeners();
    }

    try {
      final filtro = accion ?? _selectedFiltro;
      final response = await BitacoraService.fetchBitacora(
        accion: filtro == 'TODOS' ? null : filtro,
        limit: 100,
      );
      _items = response.items;
      _total = response.total;
      _errorMessage = null;
    } catch (e) {
      _errorMessage = e.toString().replaceAll('Exception: ', '');
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  void setFiltro(String filtro) {
    if (_selectedFiltro == filtro) return;
    _selectedFiltro = filtro;
    notifyListeners();
    fetchBitacora(accion: filtro);
  }

  void setSearchQuery(String query) {
    _searchQuery = query;
    notifyListeners();
  }

  Future<void> refresh() async {
    await fetchBitacora(showLoading: false);
  }
}
