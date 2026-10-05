import 'package:flutter/material.dart';
import '../controllers/purchase_controller.dart';
import '../models/purchase_model.dart';
import 'purchase_detail_view.dart';
import 'purchase_create_view.dart';

class PurchaseListView extends StatefulWidget {
  final PurchaseController controller;
  final bool initialOnlyPending;

  const PurchaseListView({
    super.key,
    required this.controller,
    this.initialOnlyPending = false,
  });

  @override
  State<PurchaseListView> createState() => _PurchaseListViewState();
}

class _PurchaseListViewState extends State<PurchaseListView> {
  final TextEditingController _searchController = TextEditingController();
  final TextEditingController _rejectReasonController = TextEditingController();
  String _searchQuery = '';

  @override
  void initState() {
    super.initState();
    if (widget.initialOnlyPending) {
      widget.controller.setFilter('pendiente');
    } else {
      widget.controller.loadPurchases();
    }
    _searchController.addListener(() {
      setState(() => _searchQuery = _searchController.text.trim().toLowerCase());
    });
  }

  @override
  void dispose() {
    _searchController.dispose();
    _rejectReasonController.dispose();
    super.dispose();
  }

  void _showApproveDialog(CompraModel compra) {
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        backgroundColor: const Color(0xFF1E293B),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        title: const Row(
          children: [
            Icon(Icons.check_circle_outline, color: Color(0xFF10B981)),
            SizedBox(width: 10),
            Text('Aprobar Orden', style: TextStyle(color: Colors.white, fontSize: 18)),
          ],
        ),
        content: Text(
          '¿Deseas aprobar la orden #${compra.numeroorden}?\nTotal: \$${compra.totalusd.toStringAsFixed(2)} USD\nProveedor: ${compra.proveedorNombre}',
          style: const TextStyle(color: Color(0xFF94A3B8), fontSize: 14),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text('Cancelar', style: TextStyle(color: Color(0xFF94A3B8))),
          ),
          ElevatedButton(
            style: ElevatedButton.styleFrom(backgroundColor: const Color(0xFF10B981)),
            onPressed: () async {
              Navigator.pop(ctx);
              final ok = await widget.controller.approve(compra.idcompra);
              if (ok && mounted) {
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(
                    content: Text(widget.controller.successMessage ?? 'Orden aprobada.'),
                    backgroundColor: const Color(0xFF059669),
                  ),
                );
              }
            },
            child: const Text('Aprobar', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
          ),
        ],
      ),
    );
  }

  void _showRejectDialog(CompraModel compra) {
    _rejectReasonController.clear();
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        backgroundColor: const Color(0xFF1E293B),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        title: const Row(
          children: [
            Icon(Icons.cancel_outlined, color: Color(0xFFEF4444)),
            SizedBox(width: 10),
            Text('Rechazar Orden', style: TextStyle(color: Colors.white, fontSize: 18)),
          ],
        ),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Indica el motivo del rechazo para #${compra.numeroorden}:',
              style: const TextStyle(color: Color(0xFF94A3B8), fontSize: 13),
            ),
            const SizedBox(height: 10),
            TextField(
              controller: _rejectReasonController,
              maxLines: 3,
              style: const TextStyle(color: Colors.white),
              decoration: InputDecoration(
                hintText: 'Motivo justificado de rechazo...',
                hintStyle: const TextStyle(color: Color(0xFF64748B), fontSize: 13),
                filled: true,
                fillColor: const Color(0xFF0F172A),
                border: OutlineInputBorder(borderRadius: BorderRadius.circular(8)),
              ),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text('Cancelar', style: TextStyle(color: Color(0xFF94A3B8))),
          ),
          ElevatedButton(
            style: ElevatedButton.styleFrom(backgroundColor: const Color(0xFFEF4444)),
            onPressed: () async {
              if (_rejectReasonController.text.trim().isEmpty) {
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('El motivo es obligatorio.'), backgroundColor: Colors.redAccent),
                );
                return;
              }
              Navigator.pop(ctx);
              final ok = await widget.controller.reject(compra.idcompra, _rejectReasonController.text.trim());
              if (ok && mounted) {
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(
                    content: Text(widget.controller.successMessage ?? 'Orden rechazada.'),
                    backgroundColor: const Color(0xFFDC2626),
                  ),
                );
              }
            },
            child: const Text('Rechazar', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0F172A),
      appBar: AppBar(
        backgroundColor: const Color(0xFF1E293B),
        title: const Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Órdenes de Compra', style: TextStyle(color: Colors.white, fontSize: 18, fontWeight: FontWeight.bold)),
            Text('CU-010 Gestión / CU-011 Aprobaciones', style: TextStyle(color: Color(0xFF38BDF8), fontSize: 11)),
          ],
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh, color: Color(0xFF38BDF8)),
            tooltip: 'Actualizar',
            onPressed: () => widget.controller.loadPurchases(),
          ),
        ],
      ),
      body: ListenableBuilder(
        listenable: widget.controller,
        builder: (context, _) {
          final all = widget.controller.purchases;
          final filtered = all.where((c) {
            if (_searchQuery.isEmpty) return true;
            return c.numeroorden.toLowerCase().contains(_searchQuery) ||
                c.proveedorNombre.toLowerCase().contains(_searchQuery);
          }).toList();

          return Column(
            children: [
              // Barra de Métricas Superiores
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                color: const Color(0xFF1E293B),
                child: Row(
                  children: [
                    _metricChip(
                      icon: Icons.receipt_long,
                      label: 'Total',
                      value: '${all.length}',
                      color: const Color(0xFF38BDF8),
                    ),
                    const SizedBox(width: 8),
                    _metricChip(
                      icon: Icons.pending_actions,
                      label: 'Pendientes',
                      value: '${widget.controller.pendingCount}',
                      color: const Color(0xFFF59E0B),
                      onTap: () => widget.controller.setFilter(widget.controller.selectedEstado == 'pendiente' ? null : 'pendiente'),
                      isSelected: widget.controller.selectedEstado == 'pendiente',
                    ),
                    const SizedBox(width: 8),
                    _metricChip(
                      icon: Icons.monetization_on_outlined,
                      label: 'Inversión',
                      value: '\$${(widget.controller.totalUSD / 1000).toStringAsFixed(1)}k',
                      color: const Color(0xFF10B981),
                    ),
                  ],
                ),
              ),

              // Buscador y Filtros
              Padding(
                padding: const EdgeInsets.fromLTRB(16, 12, 16, 8),
                child: TextField(
                  controller: _searchController,
                  style: const TextStyle(color: Colors.white, fontSize: 14),
                  decoration: InputDecoration(
                    hintText: 'Buscar por orden o proveedor...',
                    hintStyle: const TextStyle(color: Color(0xFF64748B), fontSize: 13),
                    prefixIcon: const Icon(Icons.search, color: Color(0xFF94A3B8), size: 20),
                    suffixIcon: _searchQuery.isNotEmpty
                        ? IconButton(
                            icon: const Icon(Icons.clear, color: Color(0xFF94A3B8), size: 18),
                            onPressed: () => _searchController.clear(),
                          )
                        : null,
                    filled: true,
                    fillColor: const Color(0xFF1E293B),
                    contentPadding: const EdgeInsets.symmetric(vertical: 10),
                    border: OutlineInputBorder(borderRadius: BorderRadius.circular(10), borderSide: BorderSide.none),
                  ),
                ),
              ),

              // Chips de Estado
              SingleChildScrollView(
                scrollDirection: Axis.horizontal,
                padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
                child: Row(
                  children: [
                    _filterChip(label: 'Todos', value: null),
                    const SizedBox(width: 8),
                    _filterChip(label: 'Pendientes', value: 'pendiente', count: widget.controller.pendingCount),
                    const SizedBox(width: 8),
                    _filterChip(label: 'Aprobadas', value: 'enviada'),
                    const SizedBox(width: 8),
                    _filterChip(label: 'Recibidas', value: 'recibida_total'),
                    const SizedBox(width: 8),
                    _filterChip(label: 'Canceladas', value: 'cancelada'),
                  ],
                ),
              ),

              const SizedBox(height: 6),

              // Lista de Órdenes
              Expanded(
                child: RefreshIndicator(
                  color: const Color(0xFF0EA5E9),
                  onRefresh: () => widget.controller.loadPurchases(),
                  child: widget.controller.isLoading
                      ? const Center(child: CircularProgressIndicator(color: Color(0xFF0EA5E9)))
                      : filtered.isEmpty
                          ? Center(
                              child: SingleChildScrollView(
                                physics: const AlwaysScrollableScrollPhysics(),
                                child: Column(
                                  mainAxisAlignment: MainAxisAlignment.center,
                                  children: [
                                    const Icon(Icons.inventory_2_outlined, size: 50, color: Color(0xFF64748B)),
                                    const SizedBox(height: 12),
                                    const Text('No se encontraron órdenes de compra', style: TextStyle(color: Color(0xFF94A3B8), fontSize: 15)),
                                    const SizedBox(height: 6),
                                    Text(
                                      widget.controller.selectedEstado != null
                                          ? 'Prueba cambiando el filtro de estado.'
                                          : 'Crea una nueva orden con el botón inferior "+".',
                                      style: const TextStyle(color: Color(0xFF64748B), fontSize: 12),
                                    ),
                                  ],
                                ),
                              ),
                            )
                          : ListView.separated(
                              padding: const EdgeInsets.fromLTRB(16, 8, 16, 80),
                              itemCount: filtered.length,
                              separatorBuilder: (_, __) => const SizedBox(height: 12),
                              itemBuilder: (ctx, index) {
                                final compra = filtered[index];
                                return _buildPurchaseCard(compra);
                              },
                            ),
                ),
              ),
            ],
          );
        },
      ),
      floatingActionButton: FloatingActionButton.extended(
        backgroundColor: const Color(0xFF0EA5E9),
        icon: const Icon(Icons.add, color: Colors.white),
        label: const Text('Nueva Orden', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
        onPressed: () {
          Navigator.of(context).push(
            MaterialPageRoute(
              builder: (_) => PurchaseCreateView(controller: widget.controller),
            ),
          );
        },
      ),
    );
  }

  Widget _buildPurchaseCard(CompraModel compra) {
    final statusColor = _getStatusColor(compra.estado);

    return Container(
      decoration: BoxDecoration(
        color: const Color(0xFF1E293B),
        borderRadius: BorderRadius.circular(14),
        border: Border.all(
          color: compra.isPendiente ? const Color(0xFFF59E0B).withValues(alpha: 0.5) : const Color(0xFF334155),
          width: compra.isPendiente ? 1.5 : 1,
        ),
        boxShadow: const [
          BoxShadow(color: Color(0x33000000), blurRadius: 6, offset: Offset(0, 3)),
        ],
      ),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Cabecera: Número y Estado
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Row(
                  children: [
                    const Icon(Icons.receipt_rounded, size: 18, color: Color(0xFF38BDF8)),
                    const SizedBox(width: 6),
                    Text(
                      compra.numeroorden,
                      style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 15),
                    ),
                  ],
                ),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                  decoration: BoxDecoration(
                    color: statusColor.withValues(alpha: 0.15),
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(color: statusColor, width: 1),
                  ),
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Icon(_getStatusIcon(compra.estado), size: 12, color: statusColor),
                      const SizedBox(width: 4),
                      Text(
                        compra.estadoLabel,
                        style: TextStyle(color: statusColor, fontSize: 11, fontWeight: FontWeight.bold),
                      ),
                    ],
                  ),
                ),
              ],
            ),
            const Divider(color: Color(0xFF334155), height: 18),

            // Proveedor y Fecha
            Row(
              children: [
                const Icon(Icons.business_outlined, size: 15, color: Color(0xFF64748B)),
                const SizedBox(width: 6),
                Expanded(
                  child: Text(
                    compra.proveedorNombre,
                    style: const TextStyle(color: Color(0xFFCBD5E1), fontSize: 13, fontWeight: FontWeight.w500),
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
                const SizedBox(width: 8),
                Text(
                  compra.fechacompra,
                  style: const TextStyle(color: Color(0xFF94A3B8), fontSize: 12),
                ),
              ],
            ),
            const SizedBox(height: 10),

            // Métricas: Cantidad de ítems y Total USD
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  '${compra.totalItems} unidades (${compra.detalles.length} líneas)',
                  style: const TextStyle(color: Color(0xFF94A3B8), fontSize: 12),
                ),
                Text(
                  '\$${compra.totalusd.toStringAsFixed(2)} USD',
                  style: const TextStyle(color: Color(0xFF38BDF8), fontWeight: FontWeight.bold, fontSize: 16),
                ),
              ],
            ),
            const SizedBox(height: 12),

            // Acciones: Aprobar / Rechazar (CU-011) si es pendiente, o Ver Detalle
            Row(
              children: [
                if (compra.isPendiente) ...[
                  Expanded(
                    child: OutlinedButton.icon(
                      style: OutlinedButton.styleFrom(
                        side: const BorderSide(color: Color(0xFFEF4444)),
                        padding: const EdgeInsets.symmetric(vertical: 8),
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                      ),
                      icon: const Icon(Icons.close, color: Color(0xFFEF4444), size: 16),
                      label: const Text('Rechazar', style: TextStyle(color: Color(0xFFEF4444), fontSize: 12, fontWeight: FontWeight.bold)),
                      onPressed: () => _showRejectDialog(compra),
                    ),
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: ElevatedButton.icon(
                      style: ElevatedButton.styleFrom(
                        backgroundColor: const Color(0xFF10B981),
                        padding: const EdgeInsets.symmetric(vertical: 8),
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                      ),
                      icon: const Icon(Icons.check, color: Colors.white, size: 16),
                      label: const Text('Aprobar', style: TextStyle(color: Colors.white, fontSize: 12, fontWeight: FontWeight.bold)),
                      onPressed: () => _showApproveDialog(compra),
                    ),
                  ),
                  const SizedBox(width: 8),
                ],
                IconButton(
                  style: IconButton.styleFrom(backgroundColor: const Color(0xFF0F172A)),
                  icon: const Icon(Icons.visibility_outlined, color: Color(0xFF38BDF8), size: 18),
                  tooltip: 'Ver Detalle Completo',
                  onPressed: () {
                    Navigator.of(context).push(
                      MaterialPageRoute(
                        builder: (_) => PurchaseDetailView(initialCompra: compra, controller: widget.controller),
                      ),
                    );
                  },
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _metricChip({
    required IconData icon,
    required String label,
    required String value,
    required Color color,
    VoidCallback? onTap,
    bool isSelected = false,
  }) {
    return Expanded(
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(8),
        child: Container(
          padding: const EdgeInsets.symmetric(vertical: 8, horizontal: 8),
          decoration: BoxDecoration(
            color: isSelected ? color.withValues(alpha: 0.25) : const Color(0xFF0F172A),
            borderRadius: BorderRadius.circular(8),
            border: Border.all(color: isSelected ? color : const Color(0xFF334155)),
          ),
          child: Column(
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(icon, size: 14, color: color),
                  const SizedBox(width: 4),
                  Text(label, style: const TextStyle(color: Color(0xFF94A3B8), fontSize: 11)),
                ],
              ),
              const SizedBox(height: 2),
              Text(value, style: TextStyle(color: color, fontSize: 14, fontWeight: FontWeight.bold)),
            ],
          ),
        ),
      ),
    );
  }

  Widget _filterChip({required String label, required String? value, int? count}) {
    final isSelected = widget.controller.selectedEstado == value;
    return ChoiceChip(
      selected: isSelected,
      label: Text(
        count != null && count > 0 ? '$label ($count)' : label,
        style: TextStyle(
          color: isSelected ? Colors.white : const Color(0xFF94A3B8),
          fontSize: 12,
          fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
        ),
      ),
      selectedColor: const Color(0xFF0EA5E9),
      backgroundColor: const Color(0xFF1E293B),
      side: BorderSide(color: isSelected ? const Color(0xFF0EA5E9) : const Color(0xFF334155)),
      onSelected: (_) => widget.controller.setFilter(value),
    );
  }

  Color _getStatusColor(String estado) {
    switch (estado) {
      case 'pendiente':
        return const Color(0xFFF59E0B);
      case 'enviada':
        return const Color(0xFF0EA5E9);
      case 'recibida_total':
        return const Color(0xFF10B981);
      case 'cancelada':
        return const Color(0xFFEF4444);
      default:
        return Colors.grey;
    }
  }

  IconData _getStatusIcon(String estado) {
    switch (estado) {
      case 'pendiente':
        return Icons.pending_actions;
      case 'enviada':
        return Icons.send_rounded;
      case 'recibida_total':
        return Icons.check_circle_outline;
      case 'cancelada':
        return Icons.cancel_outlined;
      default:
        return Icons.help_outline;
    }
  }
}
