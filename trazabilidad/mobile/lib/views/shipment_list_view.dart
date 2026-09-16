import 'package:flutter/material.dart';
import '../controllers/transport_controller.dart';
import '../models/transport_model.dart';
import 'record_transport_event_view.dart';

class ShipmentListView extends StatefulWidget {
  final TransportController transportController;

  const ShipmentListView({super.key, required this.transportController});

  @override
  State<ShipmentListView> createState() => _ShipmentListViewState();
}

class _ShipmentListViewState extends State<ShipmentListView> {
  final TextEditingController _searchController = TextEditingController();
  final List<String> _estados = [
    'TODOS',
    'preparacion',
    'en_transito',
    'en_aduana',
    'entregado',
    'cancelado'
  ];

  @override
  void initState() {
    super.initState();
    widget.transportController.loadShipments();
  }

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  Color _getEstadoColor(String estado) {
    switch (estado.toLowerCase()) {
      case 'preparacion':
        return const Color(0xFF64748B); // Slate
      case 'en_transito':
        return const Color(0xFF0284C7); // Sky blue
      case 'en_aduana':
        return const Color(0xFFD97706); // Amber
      case 'entregado':
        return const Color(0xFF059669); // Emerald
      case 'cancelado':
        return const Color(0xFFDC2626); // Red
      default:
        return const Color(0xFF38BDF8);
    }
  }

  void _showTimelineModal(BuildContext context, ShipmentModel envio) async {
    await widget.transportController.loadTimeline(envio.idenvio);

    if (!context.mounted) return;

    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: const Color(0xFF1E293B),
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
      ),
      builder: (ctx) {
        return DraggableScrollableSheet(
          initialChildSize: 0.8,
          minChildSize: 0.5,
          maxChildSize: 0.95,
          expand: false,
          builder: (_, scrollController) {
            final timeline = widget.transportController.currentTimeline;
            final isBusy = widget.transportController.isTimelineLoading;

            return Padding(
              padding: const EdgeInsets.symmetric(horizontal: 20.0, vertical: 16.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Center(
                    child: Container(
                      width: 40,
                      height: 4,
                      decoration: BoxDecoration(
                        color: Colors.white24,
                        borderRadius: BorderRadius.circular(2),
                      ),
                    ),
                  ),
                  const SizedBox(height: 16),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              'Línea de Tiempo - ${envio.codigoenvio}',
                              style: const TextStyle(
                                fontSize: 18,
                                fontWeight: FontWeight.bold,
                                color: Colors.white,
                              ),
                            ),
                            const SizedBox(height: 4),
                            Text(
                              '${envio.actorOrigenNombre ?? "Origen"} → ${envio.actorDestinoNombre ?? "Destino"}',
                              style: const TextStyle(fontSize: 13, color: Color(0xFF94A3B8)),
                            ),
                          ],
                        ),
                      ),
                      IconButton(
                        icon: const Icon(Icons.close, color: Colors.white70),
                        onPressed: () => Navigator.pop(ctx),
                      ),
                    ],
                  ),
                  const SizedBox(height: 12),
                  SizedBox(
                    width: double.infinity,
                    child: ElevatedButton.icon(
                      style: ElevatedButton.styleFrom(
                        backgroundColor: const Color(0xFF0284C7),
                        foregroundColor: Colors.white,
                        padding: const EdgeInsets.symmetric(vertical: 12),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(10),
                        ),
                      ),
                      icon: const Icon(Icons.add_location_alt_outlined, size: 18),
                      label: const Text('Registrar Evento / Telemetría', style: TextStyle(fontWeight: FontWeight.bold)),
                      onPressed: () {
                        Navigator.pop(ctx);
                        Navigator.of(context).push(
                          MaterialPageRoute(
                            builder: (_) => RecordTransportEventView(
                              envio: envio,
                              transportController: widget.transportController,
                            ),
                          ),
                        );
                      },
                    ),
                  ),
                  const Divider(color: Color(0xFF334155), height: 24),
                  Expanded(
                    child: isBusy
                        ? const Center(child: CircularProgressIndicator(color: Color(0xFF38BDF8)))
                        : (timeline == null || timeline.eventos.isEmpty)
                            ? const Center(
                                child: Text(
                                  'No hay eventos registrados para este envío.',
                                  style: TextStyle(color: Color(0xFF94A3B8)),
                                ),
                              )
                            : ListView.separated(
                                controller: scrollController,
                                itemCount: timeline.eventos.length,
                                separatorBuilder: (_, __) => const Divider(color: Color(0xFF334155), height: 16),
                                itemBuilder: (_, idx) {
                                  final ev = timeline.eventos[idx];
                                  final cond = ev.condiciones;

                                  return Container(
                                    padding: const EdgeInsets.all(12),
                                    decoration: BoxDecoration(
                                      color: const Color(0xFF0F172A),
                                      borderRadius: BorderRadius.circular(12),
                                      border: Border.all(color: const Color(0xFF334155)),
                                    ),
                                    child: Column(
                                      crossAxisAlignment: CrossAxisAlignment.start,
                                      children: [
                                        Row(
                                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                          children: [
                                            Container(
                                              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                                              decoration: BoxDecoration(
                                                color: const Color(0xFF38BDF8).withValues(alpha: 0.15),
                                                borderRadius: BorderRadius.circular(6),
                                              ),
                                              child: Text(
                                                ev.tipoevento.toUpperCase(),
                                                style: const TextStyle(
                                                  color: Color(0xFF38BDF8),
                                                  fontWeight: FontWeight.bold,
                                                  fontSize: 11,
                                                ),
                                              ),
                                            ),
                                            Text(
                                              ev.fechahora,
                                              style: const TextStyle(color: Color(0xFF94A3B8), fontSize: 11),
                                            ),
                                          ],
                                        ),
                                        const SizedBox(height: 8),
                                        if (ev.descripcion != null && ev.descripcion!.isNotEmpty)
                                          Text(
                                            ev.descripcion!,
                                            style: const TextStyle(color: Colors.white, fontSize: 13),
                                          ),
                                        const SizedBox(height: 6),
                                        Row(
                                          children: [
                                            const Icon(Icons.place_outlined, size: 14, color: Color(0xFF94A3B8)),
                                            const SizedBox(width: 4),
                                            Text(
                                              ev.ubicacionNombre ?? 'Ubicación #${ev.idubicacion}',
                                              style: const TextStyle(color: Color(0xFF94A3B8), fontSize: 12),
                                            ),
                                            if (ev.usuarioNombre != null) ...[
                                              const SizedBox(width: 12),
                                              const Icon(Icons.person_outline, size: 14, color: Color(0xFF94A3B8)),
                                              const SizedBox(width: 4),
                                              Text(
                                                ev.usuarioNombre!,
                                                style: const TextStyle(color: Color(0xFF94A3B8), fontSize: 12),
                                              ),
                                            ],
                                          ],
                                        ),
                                        if (cond != null) ...[
                                          const SizedBox(height: 10),
                                          Wrap(
                                            spacing: 8,
                                            runSpacing: 4,
                                            children: [
                                              if (cond.temperatura != null)
                                                _telemetryChip(
                                                  Icons.thermostat,
                                                  '${cond.temperatura}°C',
                                                  (cond.temperatura! < 2 || cond.temperatura! > 8)
                                                      ? const Color(0xFFEF4444)
                                                      : const Color(0xFF10B981),
                                                ),
                                              if (cond.humedad != null)
                                                _telemetryChip(
                                                  Icons.water_drop,
                                                  '${cond.humedad}%',
                                                  (cond.humedad! > 65)
                                                      ? const Color(0xFFF59E0B)
                                                      : const Color(0xFF38BDF8),
                                                ),
                                              if (cond.nivelvibracion != null)
                                                _telemetryChip(
                                                  Icons.vibration,
                                                  '${cond.nivelvibracion}g',
                                                  const Color(0xFFA855F7),
                                                ),
                                              if (cond.presion != null)
                                                _telemetryChip(
                                                  Icons.speed,
                                                  '${cond.presion}hPa',
                                                  const Color(0xFF64748B),
                                                ),
                                            ],
                                          ),
                                        ],
                                      ],
                                    ),
                                  );
                                },
                              ),
                  ),
                ],
              ),
            );
          },
        );
      },
    );
  }

  Widget _telemetryChip(IconData icon, String label, Color color) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.15),
        borderRadius: BorderRadius.circular(6),
        border: Border.all(color: color.withValues(alpha: 0.3)),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 12, color: color),
          const SizedBox(width: 4),
          Text(
            label,
            style: TextStyle(color: color, fontSize: 11, fontWeight: FontWeight.bold),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: widget.transportController,
      builder: (context, _) {
        final ctrl = widget.transportController;

        final filteredShipments = ctrl.shipments.where((s) {
          final query = _searchController.text.toLowerCase().trim();
          if (query.isEmpty) return true;
          return s.codigoenvio.toLowerCase().contains(query) ||
              (s.actorDestinoNombre?.toLowerCase().contains(query) ?? false) ||
              (s.actorOrigenNombre?.toLowerCase().contains(query) ?? false) ||
              (s.transportistaNombre?.toLowerCase().contains(query) ?? false);
        }).toList();

        return Scaffold(
          backgroundColor: const Color(0xFF0F172A),
          appBar: AppBar(
            backgroundColor: const Color(0xFF1E293B),
            title: const Text(
              'Envíos y Transporte (CU-021)',
              style: TextStyle(color: Colors.white, fontSize: 18),
            ),
            iconTheme: const IconThemeData(color: Colors.white),
            actions: [
              IconButton(
                icon: const Icon(Icons.refresh, color: Color(0xFF38BDF8)),
                onPressed: () => ctrl.loadShipments(),
              ),
            ],
          ),
          body: Column(
            children: [
              // Barra de búsqueda
              Container(
                color: const Color(0xFF1E293B),
                padding: const EdgeInsets.fromLTRB(16, 8, 16, 8),
                child: TextField(
                  controller: _searchController,
                  style: const TextStyle(color: Colors.white),
                  decoration: InputDecoration(
                    hintText: 'Buscar por código, destino o transportista...',
                    hintStyle: const TextStyle(color: Color(0xFF64748B), fontSize: 14),
                    prefixIcon: const Icon(Icons.search, color: Color(0xFF38BDF8)),
                    suffixIcon: _searchController.text.isNotEmpty
                        ? IconButton(
                            icon: const Icon(Icons.clear, color: Colors.white54),
                            onPressed: () {
                              _searchController.clear();
                              setState(() {});
                            },
                          )
                        : null,
                    filled: true,
                    fillColor: const Color(0xFF0F172A),
                    contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(12),
                      borderSide: const BorderSide(color: Color(0xFF334155)),
                    ),
                    enabledBorder: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(12),
                      borderSide: const BorderSide(color: Color(0xFF334155)),
                    ),
                  ),
                  onChanged: (_) => setState(() {}),
                ),
              ),

              // Chips de filtros de estado
              Container(
                color: const Color(0xFF1E293B),
                height: 48,
                child: ListView.separated(
                  scrollDirection: Axis.horizontal,
                  padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 6),
                  itemCount: _estados.length,
                  separatorBuilder: (_, __) => const SizedBox(width: 8),
                  itemBuilder: (context, index) {
                    final estado = _estados[index];
                    final isSelected = (estado == 'TODOS' && ctrl.selectedEstado == null) ||
                        ctrl.selectedEstado == estado;

                    return ChoiceChip(
                      label: Text(estado.toUpperCase(), style: const TextStyle(fontSize: 11)),
                      selected: isSelected,
                      selectedColor: const Color(0xFF0284C7),
                      backgroundColor: const Color(0xFF0F172A),
                      labelStyle: TextStyle(
                        color: isSelected ? Colors.white : const Color(0xFF94A3B8),
                        fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
                      ),
                      side: BorderSide(
                        color: isSelected ? const Color(0xFF38BDF8) : const Color(0xFF334155),
                      ),
                      onSelected: (_) {
                        ctrl.filterByEstado(estado == 'TODOS' ? null : estado);
                      },
                    );
                  },
                ),
              ),

              // Mensaje de Error
              if (ctrl.errorMessage != null)
                Container(
                  width: double.infinity,
                  margin: const EdgeInsets.all(12),
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: const Color(0xFF7F1D1D),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Text(
                    ctrl.errorMessage!,
                    style: const TextStyle(color: Color(0xFFFCA5A5), fontSize: 12),
                  ),
                ),

              // Lista de Envíos
              Expanded(
                child: ctrl.isLoading
                    ? const Center(child: CircularProgressIndicator(color: Color(0xFF38BDF8)))
                    : filteredShipments.isEmpty
                        ? const Center(
                            child: Text(
                              'No se encontraron envíos.',
                              style: TextStyle(color: Color(0xFF94A3B8)),
                            ),
                          )
                        : ListView.builder(
                            padding: const EdgeInsets.all(16),
                            itemCount: filteredShipments.length,
                            itemBuilder: (context, index) {
                              final envio = filteredShipments[index];
                              final colorEstado = _getEstadoColor(envio.estado);

                              return Card(
                                color: const Color(0xFF1E293B),
                                margin: const EdgeInsets.only(bottom: 14),
                                shape: RoundedRectangleBorder(
                                  borderRadius: BorderRadius.circular(16),
                                  side: const BorderSide(color: Color(0xFF334155)),
                                ),
                                child: InkWell(
                                  borderRadius: BorderRadius.circular(16),
                                  onTap: () => _showTimelineModal(context, envio),
                                  child: Padding(
                                    padding: const EdgeInsets.all(16.0),
                                    child: Column(
                                      crossAxisAlignment: CrossAxisAlignment.start,
                                      children: [
                                        Row(
                                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                          children: [
                                            Text(
                                              envio.codigoenvio,
                                              style: const TextStyle(
                                                fontSize: 16,
                                                fontWeight: FontWeight.bold,
                                                color: Colors.white,
                                              ),
                                            ),
                                            Container(
                                              padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                                              decoration: BoxDecoration(
                                                color: colorEstado.withValues(alpha: 0.2),
                                                borderRadius: BorderRadius.circular(20),
                                                border: Border.all(color: colorEstado),
                                              ),
                                              child: Text(
                                                envio.estado.toUpperCase(),
                                                style: TextStyle(
                                                  color: colorEstado,
                                                  fontSize: 11,
                                                  fontWeight: FontWeight.bold,
                                                ),
                                              ),
                                            ),
                                          ],
                                        ),
                                        const Divider(color: Color(0xFF334155), height: 20),
                                        Row(
                                          children: [
                                            const Icon(Icons.outbox, size: 16, color: Color(0xFF94A3B8)),
                                            const SizedBox(width: 6),
                                            Expanded(
                                              child: Text(
                                                'Origen: ${envio.actorOrigenNombre ?? "No especificado"}',
                                                style: const TextStyle(color: Color(0xFF94A3B8), fontSize: 13),
                                              ),
                                            ),
                                          ],
                                        ),
                                        const SizedBox(height: 4),
                                        Row(
                                          children: [
                                            const Icon(Icons.move_to_inbox, size: 16, color: Color(0xFF94A3B8)),
                                            const SizedBox(width: 6),
                                            Expanded(
                                              child: Text(
                                                'Destino: ${envio.actorDestinoNombre ?? "No especificado"}',
                                                style: const TextStyle(color: Colors.white, fontSize: 13),
                                              ),
                                            ),
                                          ],
                                        ),
                                        const SizedBox(height: 4),
                                        Row(
                                          children: [
                                            const Icon(Icons.local_shipping_outlined, size: 16, color: Color(0xFF94A3B8)),
                                            const SizedBox(width: 6),
                                            Expanded(
                                              child: Text(
                                                'Transportista: ${envio.transportistaNombre ?? "No asignado"}',
                                                style: const TextStyle(color: Color(0xFF94A3B8), fontSize: 12),
                                              ),
                                            ),
                                          ],
                                        ),
                                        const SizedBox(height: 12),
                                        Row(
                                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                          children: [
                                            Text(
                                              '${envio.totalUnidades} Unidades en carga',
                                              style: const TextStyle(color: Color(0xFF38BDF8), fontSize: 12),
                                            ),
                                            const Row(
                                              children: [
                                                Text(
                                                  'Ver detalles / Línea de tiempo',
                                                  style: TextStyle(color: Color(0xFF38BDF8), fontSize: 12, fontWeight: FontWeight.bold),
                                                ),
                                                Icon(Icons.chevron_right, size: 16, color: Color(0xFF38BDF8)),
                                              ],
                                            ),
                                          ],
                                        ),
                                      ],
                                    ),
                                  ),
                                ),
                              );
                            },
                          ),
              ),
            ],
          ),
        );
      },
    );
  }
}
