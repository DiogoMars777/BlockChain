import 'package:flutter/material.dart';
import '../controllers/purchase_controller.dart';
import '../models/purchase_model.dart';

class PurchaseDetailView extends StatefulWidget {
  final CompraModel initialCompra;
  final PurchaseController controller;

  const PurchaseDetailView({
    super.key,
    required this.initialCompra,
    required this.controller,
  });

  @override
  State<PurchaseDetailView> createState() => _PurchaseDetailViewState();
}

class _PurchaseDetailViewState extends State<PurchaseDetailView> {
  late CompraModel _compra;
  final TextEditingController _rejectReasonController = TextEditingController();

  @override
  void initState() {
    super.initState();
    _compra = widget.initialCompra;
  }

  @override
  void dispose() {
    _rejectReasonController.dispose();
    super.dispose();
  }

  void _showApproveDialog() {
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        backgroundColor: const Color(0xFF1E293B),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        title: const Row(
          children: [
            Icon(Icons.check_circle_outline, color: Color(0xFF10B981)),
            SizedBox(width: 10),
            Text('Aprobar Orden de Compra', style: TextStyle(color: Colors.white, fontSize: 18)),
          ],
        ),
        content: Text(
          '¿Estás seguro de que deseas aprobar la orden #${_compra.numeroorden} por un total de \$${_compra.totalusd.toStringAsFixed(2)} USD?\n\n'
          'La orden pasará a estado "Enviada" y se notificará al proveedor.',
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
              final ok = await widget.controller.approve(_compra.idcompra);
              if (ok && mounted) {
                final updated = widget.controller.purchases.firstWhere(
                  (p) => p.idcompra == _compra.idcompra,
                  orElse: () => _compra,
                );
                setState(() => _compra = updated);
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(
                    content: Text(widget.controller.successMessage ?? 'Orden aprobada.'),
                    backgroundColor: const Color(0xFF059669),
                  ),
                );
              }
            },
            child: const Text('Confirmar y Aprobar', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
          ),
        ],
      ),
    );
  }

  void _showRejectDialog() {
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
              'Indica el motivo justificado del rechazo para la orden #${_compra.numeroorden}:',
              style: const TextStyle(color: Color(0xFF94A3B8), fontSize: 13),
            ),
            const SizedBox(height: 12),
            TextField(
              controller: _rejectReasonController,
              maxLines: 3,
              style: const TextStyle(color: Colors.white),
              decoration: InputDecoration(
                hintText: 'Ej: Precios fuera de presupuesto, cambio de proveedor...',
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
                  const SnackBar(
                    content: Text('El motivo de rechazo es obligatorio.'),
                    backgroundColor: Colors.redAccent,
                  ),
                );
                return;
              }
              Navigator.pop(ctx);
              final ok = await widget.controller.reject(
                _compra.idcompra,
                _rejectReasonController.text.trim(),
              );
              if (ok && mounted) {
                final updated = widget.controller.purchases.firstWhere(
                  (p) => p.idcompra == _compra.idcompra,
                  orElse: () => _compra,
                );
                setState(() => _compra = updated);
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(
                    content: Text(widget.controller.successMessage ?? 'Orden rechazada.'),
                    backgroundColor: const Color(0xFFDC2626),
                  ),
                );
              }
            },
            child: const Text('Confirmar Rechazo', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
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
        title: Text('Orden #${_compra.numeroorden}', style: const TextStyle(color: Colors.white, fontSize: 18)),
        actions: [
          Container(
            margin: const EdgeInsets.only(right: 16),
            padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
            decoration: BoxDecoration(
              color: _getStatusColor(_compra.estado).withValues(alpha: 0.2),
              borderRadius: BorderRadius.circular(20),
              border: Border.all(color: _getStatusColor(_compra.estado)),
            ),
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                Icon(_getStatusIcon(_compra.estado), size: 14, color: _getStatusColor(_compra.estado)),
                const SizedBox(width: 4),
                Text(
                  _compra.estadoLabel,
                  style: TextStyle(color: _getStatusColor(_compra.estado), fontSize: 11, fontWeight: FontWeight.bold),
                ),
              ],
            ),
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Resumen de la Orden
            Card(
              color: const Color(0xFF1E293B),
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text('Datos Generales', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: Colors.white)),
                    const Divider(color: Color(0xFF334155), height: 20),
                    _detailRow('Proveedor:', _compra.proveedorNombre, Icons.business),
                    _detailRow('Fecha de Emisión:', _compra.fechacompra, Icons.calendar_today),
                    _detailRow('Cantidad de Ítems:', '${_compra.totalItems} unidades', Icons.inventory_2_outlined),
                    _detailRow('Total Inversión:', '\$${_compra.totalusd.toStringAsFixed(2)} USD', Icons.attach_money, isHighlight: true),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 16),

            // Líneas de Detalle de Productos
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Text('Detalle de Productos', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: Colors.white)),
                Text('${_compra.detalles.length} líneas', style: const TextStyle(color: Color(0xFF94A3B8), fontSize: 13)),
              ],
            ),
            const SizedBox(height: 10),

            if (_compra.detalles.isEmpty)
              Container(
                padding: const EdgeInsets.all(20),
                decoration: BoxDecoration(
                  color: const Color(0xFF1E293B),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: const Center(
                  child: Text('Sin líneas de detalle registradas.', style: TextStyle(color: Color(0xFF94A3B8))),
                ),
              )
            else
              ListView.separated(
                shrinkWrap: true,
                physics: const NeverScrollableScrollPhysics(),
                itemCount: _compra.detalles.length,
                separatorBuilder: (_, __) => const SizedBox(height: 10),
                itemBuilder: (ctx, index) {
                  final det = _compra.detalles[index];
                  return Container(
                    padding: const EdgeInsets.all(14),
                    decoration: BoxDecoration(
                      color: const Color(0xFF1E293B),
                      borderRadius: BorderRadius.circular(12),
                      border: Border.all(color: const Color(0xFF334155)),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Expanded(
                              child: Text(
                                det.productoNombre,
                                style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 15),
                              ),
                            ),
                            Container(
                              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                              decoration: BoxDecoration(
                                color: const Color(0xFF0F172A),
                                borderRadius: BorderRadius.circular(6),
                              ),
                              child: Text(
                                det.sku,
                                style: const TextStyle(color: Color(0xFF38BDF8), fontSize: 11, fontWeight: FontWeight.bold),
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 6),
                        Row(
                          children: [
                            if (det.color != null) ...[
                              _tag('Color: ${det.color}'),
                              const SizedBox(width: 8),
                            ],
                            if (det.almacenamiento != null) ...[
                              _tag('Capacidad: ${det.almacenamiento}'),
                            ],
                          ],
                        ),
                        const Divider(color: Color(0xFF334155), height: 16),
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Text(
                              '${det.cantidad} un. × \$${det.costounitariousd.toStringAsFixed(2)}',
                              style: const TextStyle(color: Color(0xFF94A3B8), fontSize: 13),
                            ),
                            Text(
                              '\$${det.subtotalusd.toStringAsFixed(2)} USD',
                              style: const TextStyle(color: Color(0xFF38BDF8), fontWeight: FontWeight.bold, fontSize: 14),
                            ),
                          ],
                        ),
                      ],
                    ),
                  );
                },
              ),
          ],
        ),
      ),
      bottomNavigationBar: _compra.isPendiente
          ? Container(
              padding: const EdgeInsets.all(16),
              decoration: const BoxDecoration(
                color: Color(0xFF1E293B),
                border: Border(top: BorderSide(color: Color(0xFF334155))),
              ),
              child: Row(
                children: [
                  Expanded(
                    child: OutlinedButton.icon(
                      style: OutlinedButton.styleFrom(
                        side: const BorderSide(color: Color(0xFFEF4444)),
                        padding: const EdgeInsets.symmetric(vertical: 14),
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                      ),
                      icon: const Icon(Icons.close, color: Color(0xFFEF4444), size: 18),
                      label: const Text('Rechazar', style: TextStyle(color: Color(0xFFEF4444), fontWeight: FontWeight.bold)),
                      onPressed: widget.controller.isLoading ? null : _showRejectDialog,
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: ElevatedButton.icon(
                      style: ElevatedButton.styleFrom(
                        backgroundColor: const Color(0xFF10B981),
                        padding: const EdgeInsets.symmetric(vertical: 14),
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                      ),
                      icon: const Icon(Icons.check, color: Colors.white, size: 18),
                      label: const Text('Aprobar Orden', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
                      onPressed: widget.controller.isLoading ? null : _showApproveDialog,
                    ),
                  ),
                ],
              ),
            )
          : null,
    );
  }

  Widget _tag(String label) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
      decoration: BoxDecoration(
        color: const Color(0xFF0F172A),
        borderRadius: BorderRadius.circular(4),
      ),
      child: Text(label, style: const TextStyle(color: Color(0xFF94A3B8), fontSize: 11)),
    );
  }

  Widget _detailRow(String label, String value, IconData icon, {bool isHighlight = false}) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 5),
      child: Row(
        children: [
          Icon(icon, size: 16, color: const Color(0xFF64748B)),
          const SizedBox(width: 8),
          Text(label, style: const TextStyle(color: Color(0xFF94A3B8), fontSize: 13)),
          const Spacer(),
          Text(
            value,
            style: TextStyle(
              color: isHighlight ? const Color(0xFF38BDF8) : Colors.white,
              fontWeight: isHighlight ? FontWeight.bold : FontWeight.w500,
              fontSize: isHighlight ? 15 : 13,
            ),
          ),
        ],
      ),
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
