import 'package:flutter/material.dart';
import '../controllers/bitacora_controller.dart';
import '../models/bitacora_model.dart';

class BitacoraView extends StatefulWidget {
  final BitacoraController bitacoraController;

  const BitacoraView({super.key, required this.bitacoraController});

  @override
  State<BitacoraView> createState() => _BitacoraViewState();
}

class _BitacoraViewState extends State<BitacoraView> {
  final TextEditingController _searchController = TextEditingController();
  final List<String> _filtros = ['TODOS', 'GET', 'POST', 'PUT', 'DELETE', 'LOGIN'];

  @override
  void initState() {
    super.initState();
    widget.bitacoraController.fetchBitacora();
  }

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  // Color del badge según la acción (GET, POST, PUT, DELETE, LOGIN)
  Color _getMethodColor(String method) {
    switch (method.toUpperCase()) {
      case 'GET':
        return const Color(0xFF0284C7); // Celeste
      case 'POST':
        return const Color(0xFF059669); // Esmeralda
      case 'PUT':
      case 'PATCH':
        return const Color(0xFFD97706); // Ámbar
      case 'DELETE':
        return const Color(0xFFDC2626); // Rojo
      case 'LOGIN':
        return const Color(0xFF7C3AED); // Morado
      default:
        return const Color(0xFF64748B); // Pizarra
    }
  }

  // Modal con detalles completos del registro seleccionado
  void _showDetailModal(BuildContext context, BitacoraItem item) {
    showModalBottomSheet(
      context: context,
      backgroundColor: const Color(0xFF1E293B),
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (_) {
        return Padding(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                    decoration: BoxDecoration(
                      color: _getMethodColor(item.accion).withValues(alpha: 0.2),
                      borderRadius: BorderRadius.circular(8),
                      border: Border.all(color: _getMethodColor(item.accion)),
                    ),
                    child: Text(
                      item.accion,
                      style: TextStyle(
                        color: _getMethodColor(item.accion),
                        fontWeight: FontWeight.bold,
                        fontSize: 14,
                      ),
                    ),
                  ),
                  Text(
                    'ID Bitácora: #${item.idbitacora}',
                    style: const TextStyle(color: Color(0xFF94A3B8), fontSize: 13),
                  ),
                ],
              ),
              const SizedBox(height: 16),
              const Divider(color: Color(0xFF334155)),
              const SizedBox(height: 12),
              _modalRow('Entidad:', item.entidad, Icons.layers_outlined),
              if (item.identidad != null)
                _modalRow('ID Recurso / Entidad:', '#${item.identidad}', Icons.tag),
              _modalRow('Usuario (ID Tenant):', 'UsuarioTenant #${item.idusuariotenant}', Icons.person_outline),
              _modalRow('Dirección IP:', item.ip ?? 'No registrada', Icons.lan_outlined),
              _modalRow('Fecha y Hora:', item.formattedFecha, Icons.access_time),
              const SizedBox(height: 20),
              SizedBox(
                width: double.infinity,
                child: ElevatedButton(
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFF334155),
                    foregroundColor: Colors.white,
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                  ),
                  onPressed: () => Navigator.of(context).pop(),
                  child: const Text('Cerrar'),
                ),
              ),
            ],
          ),
        );
      },
    );
  }

  Widget _modalRow(String label, String value, IconData icon) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 6.0),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(icon, size: 18, color: const Color(0xFF38BDF8)),
          const SizedBox(width: 10),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(label, style: const TextStyle(color: Color(0xFF94A3B8), fontSize: 12)),
                const SizedBox(height: 2),
                Text(value, style: const TextStyle(color: Colors.white, fontSize: 14, fontWeight: FontWeight.w600)),
              ],
            ),
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
        title: const Text(
          'Bitácora de Auditoría',
          style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Colors.white),
        ),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back, color: Colors.white),
          onPressed: () => Navigator.of(context).pop(),
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh, color: Color(0xFF38BDF8)),
            tooltip: 'Actualizar',
            onPressed: () => widget.bitacoraController.fetchBitacora(),
          ),
        ],
      ),
      body: ListenableBuilder(
        listenable: widget.bitacoraController,
        builder: (context, _) {
          return Column(
            children: [
              // Barra de búsqueda
              Padding(
                padding: const EdgeInsets.fromLTRB(16, 16, 16, 8),
                child: TextField(
                  controller: _searchController,
                  style: const TextStyle(color: Colors.white, fontSize: 14),
                  decoration: InputDecoration(
                    hintText: 'Buscar por acción, entidad o IP...',
                    hintStyle: const TextStyle(color: Color(0xFF64748B)),
                    prefixIcon: const Icon(Icons.search, color: Color(0xFF38BDF8), size: 20),
                    suffixIcon: _searchController.text.isNotEmpty
                        ? IconButton(
                            icon: const Icon(Icons.clear, color: Color(0xFF64748B), size: 18),
                            onPressed: () {
                              _searchController.clear();
                              widget.bitacoraController.setSearchQuery('');
                            },
                          )
                        : null,
                    filled: true,
                    fillColor: const Color(0xFF1E293B),
                    contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(12),
                      borderSide: BorderSide.none,
                    ),
                  ),
                  onChanged: (val) => widget.bitacoraController.setSearchQuery(val),
                ),
              ),

              // Chips de filtros de método HTTP
              SingleChildScrollView(
                scrollDirection: Axis.horizontal,
                padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                child: Row(
                  children: _filtros.map((filtro) {
                    final isSelected = widget.bitacoraController.selectedFiltro == filtro;
                    final chipColor = filtro == 'TODOS'
                        ? const Color(0xFF38BDF8)
                        : _getMethodColor(filtro);

                    return Padding(
                      padding: const EdgeInsets.only(right: 8.0),
                      child: FilterChip(
                        label: Text(
                          filtro,
                          style: TextStyle(
                            color: isSelected ? Colors.white : const Color(0xFF94A3B8),
                            fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
                            fontSize: 12,
                          ),
                        ),
                        selected: isSelected,
                        selectedColor: chipColor.withValues(alpha: 0.3),
                        backgroundColor: const Color(0xFF1E293B),
                        side: BorderSide(
                          color: isSelected ? chipColor : const Color(0xFF334155),
                          width: isSelected ? 1.5 : 1,
                        ),
                        onSelected: (_) => widget.bitacoraController.setFiltro(filtro),
                      ),
                    );
                  }).toList(),
                ),
              ),

              // Contenido principal (Lista, Loading o Error)
              Expanded(
                child: _buildBody(),
              ),
            ],
          );
        },
      ),
    );
  }

  Widget _buildBody() {
    final controller = widget.bitacoraController;

    if (controller.isLoading) {
      return const Center(
        child: CircularProgressIndicator(color: Color(0xFF38BDF8)),
      );
    }

    if (controller.errorMessage != null) {
      return Center(
        child: Padding(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Icon(Icons.error_outline, size: 48, color: Color(0xFFF87171)),
              const SizedBox(height: 12),
              Text(
                controller.errorMessage!,
                textAlign: TextAlign.center,
                style: const TextStyle(color: Color(0xFFF87171), fontSize: 14),
              ),
              const SizedBox(height: 16),
              ElevatedButton.icon(
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFF38BDF8),
                  foregroundColor: const Color(0xFF0F172A),
                ),
                onPressed: () => controller.fetchBitacora(),
                icon: const Icon(Icons.refresh, size: 18),
                label: const Text('Reintentar'),
              ),
            ],
          ),
        ),
      );
    }

    final items = controller.items;

    if (items.isEmpty) {
      return RefreshIndicator(
        color: const Color(0xFF38BDF8),
        backgroundColor: const Color(0xFF1E293B),
        onRefresh: () => controller.refresh(),
        child: ListView(
          physics: const AlwaysScrollableScrollPhysics(),
          children: const [
            SizedBox(height: 80),
            Icon(Icons.inbox_outlined, size: 56, color: Color(0xFF475569)),
            SizedBox(height: 12),
            Text(
              'No se encontraron registros en la bitácora',
              textAlign: TextAlign.center,
              style: TextStyle(color: Color(0xFF94A3B8), fontSize: 15),
            ),
          ],
        ),
      );
    }

    return RefreshIndicator(
      color: const Color(0xFF38BDF8),
      backgroundColor: const Color(0xFF1E293B),
      onRefresh: () => controller.refresh(),
      child: ListView.builder(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
        itemCount: items.length,
        itemBuilder: (context, index) {
          final item = items[index];
          final badgeColor = _getMethodColor(item.accion);

          return Card(
            color: const Color(0xFF1E293B),
            elevation: 2,
            margin: const EdgeInsets.only(bottom: 12),
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(14),
              side: const BorderSide(color: Color(0xFF334155), width: 0.8),
            ),
            child: InkWell(
              borderRadius: BorderRadius.circular(14),
              onTap: () => _showDetailModal(context, item),
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // Fila superior: Badge de Acción y Fecha
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                          decoration: BoxDecoration(
                            color: badgeColor.withValues(alpha: 0.18),
                            borderRadius: BorderRadius.circular(6),
                            border: Border.all(color: badgeColor, width: 1),
                          ),
                          child: Text(
                            item.accion,
                            style: TextStyle(
                              color: badgeColor,
                              fontWeight: FontWeight.bold,
                              fontSize: 12,
                            ),
                          ),
                        ),
                        Row(
                          children: [
                            const Icon(Icons.access_time, size: 14, color: Color(0xFF94A3B8)),
                            const SizedBox(width: 4),
                            Text(
                              item.formattedFecha,
                              style: const TextStyle(color: Color(0xFF94A3B8), fontSize: 12),
                            ),
                          ],
                        ),
                      ],
                    ),
                    const SizedBox(height: 12),

                    // Fila media: Entidad
                    Text(
                      item.entidad,
                      style: const TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.bold,
                        color: Colors.white,
                      ),
                    ),
                    const SizedBox(height: 8),

                    // Fila inferior: Usuario e IP
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Row(
                          children: [
                            const Icon(Icons.person_outline, size: 15, color: Color(0xFF38BDF8)),
                            const SizedBox(width: 4),
                            Text(
                              'Usuario #${item.idusuariotenant}',
                              style: const TextStyle(color: Color(0xFFCBD5E1), fontSize: 12),
                            ),
                          ],
                        ),
                        Row(
                          children: [
                            const Icon(Icons.lan_outlined, size: 15, color: Color(0xFF10B981)),
                            const SizedBox(width: 4),
                            Text(
                              item.ip ?? '127.0.0.1',
                              style: const TextStyle(
                                color: Color(0xFFCBD5E1),
                                fontSize: 12,
                                fontFamily: 'monospace',
                              ),
                            ),
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
    );
  }
}
