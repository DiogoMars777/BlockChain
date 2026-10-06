import 'package:flutter/material.dart';

import '../../controllers/recommendation_controller.dart';
import '../../models/recommendation_model.dart';

class RecommendationsSheet extends StatefulWidget {
  final RecommendationController controller;

  const RecommendationsSheet({super.key, required this.controller});

  static Future<void> show(BuildContext context, RecommendationController controller) {
    if (!controller.hasRecommendations && !controller.isLoading) {
      controller.generateRecommendations();
    }
    return showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: const Color(0xFF0F172A),
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
      ),
      builder: (ctx) => RecommendationsSheet(controller: controller),
    );
  }

  static Color priorityColor(String prioridad) {
    switch (prioridad) {
      case 'critica':
        return const Color(0xFFEF4444);
      case 'alta':
        return const Color(0xFFF97316);
      case 'media':
        return const Color(0xFFEAB308);
      default:
        return const Color(0xFF38BDF8);
    }
  }

  static Color priorityBg(String prioridad) {
    switch (prioridad) {
      case 'critica':
        return const Color(0xFF7F1D1D);
      case 'alta':
        return const Color(0xFF7C2D12);
      case 'media':
        return const Color(0xFF715805);
      default:
        return const Color(0xFF0284C7);
    }
  }

  @override
  State<RecommendationsSheet> createState() => _RecommendationsSheetState();
}

class _RecommendationsSheetState extends State<RecommendationsSheet> {
  final TextEditingController _searchCtrl = TextEditingController();

  @override
  void initState() {
    super.initState();
    _searchCtrl.text = widget.controller.searchQuery;
  }

  @override
  void dispose() {
    _searchCtrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final controller = widget.controller;

    return ListenableBuilder(
      listenable: controller,
      builder: (context, _) {
        return DraggableScrollableSheet(
          initialChildSize: 0.88,
          minChildSize: 0.45,
          maxChildSize: 0.95,
          expand: false,
          builder: (context, scrollController) {
            return Container(
              padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
              decoration: const BoxDecoration(
                color: Color(0xFF0F172A),
                borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
              ),
              child: Column(
                children: [
                  Center(
                    child: Container(
                      width: 48,
                      height: 5,
                      margin: const EdgeInsets.only(bottom: 12),
                      decoration: BoxDecoration(
                        color: const Color(0xFF334155),
                        borderRadius: BorderRadius.circular(10),
                      ),
                    ),
                  ),

                  // Header
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      const Row(
                        children: [
                          Icon(Icons.auto_awesome, color: Color(0xFF38BDF8), size: 22),
                          SizedBox(width: 8),
                          Text(
                            'Recomendaciones de Pricing',
                            style: TextStyle(
                              color: Colors.white,
                              fontSize: 17,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ],
                      ),
                      Row(
                        children: [
                          if (controller.hasRecommendations)
                            IconButton(
                              icon: Icon(
                                controller.isPlayingAudio && controller.speakingId == null
                                    ? Icons.stop_circle_outlined
                                    : Icons.volume_up_outlined,
                                color: controller.isPlayingAudio && controller.speakingId == null
                                    ? const Color(0xFFEF4444)
                                    : const Color(0xFF38BDF8),
                              ),
                              tooltip: 'Leer resumen general en voz alta',
                              onPressed: controller.speakSummary,
                            ),
                          IconButton(
                            icon: const Icon(Icons.close, color: Colors.white70),
                            onPressed: () => Navigator.pop(context),
                          ),
                        ],
                      ),
                    ],
                  ),
                  const Divider(color: Color(0xFF1E293B)),

                  // Scrollable Body with Pull to Refresh
                  Expanded(
                    child: RefreshIndicator(
                      color: const Color(0xFF38BDF8),
                      backgroundColor: const Color(0xFF1E293B),
                      onRefresh: () => controller.generateRecommendations(),
                      child: ListView(
                        controller: scrollController,
                        physics: const AlwaysScrollableScrollPhysics(),
                        padding: const EdgeInsets.only(bottom: 24),
                        children: [
                          _buildToolbar(context, controller),
                          if (controller.errorMessage != null) ...[
                            const SizedBox(height: 12),
                            _buildError(controller.errorMessage!),
                          ],
                          const SizedBox(height: 12),
                          _buildBody(context, controller),
                        ],
                      ),
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

  Widget _buildToolbar(BuildContext context, RecommendationController controller) {
    return Column(
      children: [
        Row(
          children: [
            Expanded(
              child: FilledButton.icon(
                onPressed: controller.isLoading ? null : controller.generateRecommendations,
                style: FilledButton.styleFrom(
                  backgroundColor: const Color(0xFF0284C7),
                  padding: const EdgeInsets.symmetric(vertical: 13),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                ),
                icon: controller.isLoading
                    ? const SizedBox(
                        width: 16,
                        height: 16,
                        child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white),
                      )
                    : const Icon(Icons.refresh, size: 18),
                label: Text(
                  controller.isLoading ? 'Analizando catálogo...' : 'Volver a analizar',
                  style: const TextStyle(fontSize: 13, fontWeight: FontWeight.bold),
                ),
              ),
            ),
          ],
        ),
        if (controller.hasRecommendations) ...[
          const SizedBox(height: 10),
          TextField(
            controller: _searchCtrl,
            onChanged: controller.setSearchQuery,
            style: const TextStyle(color: Colors.white, fontSize: 13),
            decoration: InputDecoration(
              isDense: true,
              hintText: 'Buscar variante, SKU o justificación...',
              hintStyle: const TextStyle(color: Color(0xFF64748B), fontSize: 12),
              prefixIcon: const Icon(Icons.search, color: Color(0xFF64748B), size: 18),
              suffixIcon: controller.searchQuery.isNotEmpty
                  ? IconButton(
                      icon: const Icon(Icons.clear, color: Color(0xFF64748B), size: 16),
                      onPressed: () {
                        _searchCtrl.clear();
                        controller.setSearchQuery('');
                      },
                    )
                  : null,
              filled: true,
              fillColor: const Color(0xFF1E293B),
              border: OutlineInputBorder(
                borderRadius: BorderRadius.circular(10),
                borderSide: const BorderSide(color: Color(0xFF334155)),
              ),
              enabledBorder: OutlineInputBorder(
                borderRadius: BorderRadius.circular(10),
                borderSide: const BorderSide(color: Color(0xFF334155)),
              ),
              focusedBorder: OutlineInputBorder(
                borderRadius: BorderRadius.circular(10),
                borderSide: const BorderSide(color: Color(0xFF38BDF8)),
              ),
            ),
          ),
        ],
      ],
    );
  }

  Widget _buildError(String message) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: const Color(0xFF7F1D1D),
        borderRadius: BorderRadius.circular(10),
      ),
      child: Row(
        children: [
          const Icon(Icons.error_outline, color: Color(0xFFFECACA), size: 20),
          const SizedBox(width: 10),
          Expanded(
            child: Text(
              message,
              style: const TextStyle(color: Color(0xFFFECACA), fontSize: 12),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildBody(BuildContext context, RecommendationController controller) {
    final data = controller.recommendations;

    if (controller.isLoading && data == null) {
      return Container(
        padding: const EdgeInsets.symmetric(vertical: 48),
        child: const Column(
          children: [
            CircularProgressIndicator(color: Color(0xFF38BDF8)),
            SizedBox(height: 16),
            Text(
              'Analizando ventas, inventario y órdenes de compra del catálogo...',
              textAlign: TextAlign.center,
              style: TextStyle(color: Color(0xFF94A3B8), fontSize: 13),
            ),
          ],
        ),
      );
    }

    if (data == null) {
      return Container(
        padding: const EdgeInsets.symmetric(vertical: 40),
        child: const Text(
          'Presiona "Volver a analizar" para obtener recomendaciones del catálogo.',
          textAlign: TextAlign.center,
          style: TextStyle(color: Color(0xFF64748B), fontSize: 13),
        ),
      );
    }

    final items = controller.filteredRecommendations;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              'Analizado el ${data.generatedAt}',
              style: const TextStyle(color: Color(0xFF94A3B8), fontSize: 11),
            ),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
              decoration: BoxDecoration(
                color: const Color(0xFF1E293B),
                borderRadius: BorderRadius.circular(10),
              ),
              child: Text(
                '${data.totalRecomendaciones} hallazgos',
                style: const TextStyle(color: Color(0xFF38BDF8), fontSize: 11, fontWeight: FontWeight.bold),
              ),
            ),
          ],
        ),
        const SizedBox(height: 10),
        _buildFilterChips(controller),
        const SizedBox(height: 14),
        if (items.isEmpty)
          Container(
            padding: const EdgeInsets.symmetric(vertical: 36),
            alignment: Alignment.center,
            child: Text(
              controller.searchQuery.isNotEmpty
                  ? 'No se encontraron recomendaciones con el término "${controller.searchQuery}".'
                  : 'No hay recomendaciones para el filtro seleccionado.',
              textAlign: TextAlign.center,
              style: const TextStyle(color: Color(0xFF64748B), fontSize: 12),
            ),
          )
        else
          ...items.map((r) => _RecommendationCard(rec: r, controller: controller)),
      ],
    );
  }

  Widget _buildFilterChips(RecommendationController controller) {
    return SingleChildScrollView(
      scrollDirection: Axis.horizontal,
      child: Row(
        children: RecommendationController.priorityOptions.map((p) {
          final selected = controller.priorityFilter == p;
          final count = controller.countByPriority(p);
          return Padding(
            padding: const EdgeInsets.only(right: 8),
            child: ChoiceChip(
              label: Text(
                '${p == 'todas' ? 'Todas' : _capitalize(p)} ($count)',
                style: TextStyle(
                  fontSize: 12,
                  fontWeight: selected ? FontWeight.bold : FontWeight.normal,
                ),
              ),
              selected: selected,
              selectedColor: const Color(0xFF0284C7),
              backgroundColor: const Color(0xFF0F172A),
              side: BorderSide(color: selected ? const Color(0xFF0284C7) : const Color(0xFF334155)),
              labelStyle: TextStyle(color: selected ? Colors.white : const Color(0xFF94A3B8)),
              showCheckmark: false,
              onSelected: (_) => controller.setPriorityFilter(p),
            ),
          );
        }).toList(),
      ),
    );
  }

  static String _capitalize(String value) =>
      value.isEmpty ? value : value[0].toUpperCase() + value.substring(1);

}

class _RecommendationCard extends StatelessWidget {
  final PricingRecommendationModel rec;
  final RecommendationController controller;

  const _RecommendationCard({required this.rec, required this.controller});

  @override
  Widget build(BuildContext context) {
    final accent = RecommendationsSheet.priorityColor(rec.prioridad);
    final metrics = rec.metricas.displayEntries;
    final isSpeakingThis = controller.isPlayingAudio && controller.speakingId == rec.idvariante;

    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: const Color(0xFF1E293B),
        borderRadius: BorderRadius.circular(14),
        border: Border.all(
          color: isSpeakingThis ? accent : const Color(0xFF334155),
          width: isSpeakingThis ? 1.5 : 1,
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Container(
                width: 4,
                height: 44,
                margin: const EdgeInsets.only(right: 10),
                decoration: BoxDecoration(
                  color: accent,
                  borderRadius: BorderRadius.circular(4),
                ),
              ),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      rec.titulo,
                      style: const TextStyle(
                        color: Colors.white,
                        fontSize: 14,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    if (rec.descripcionVariante.isNotEmpty)
                      Text(
                        rec.descripcionVariante +
                            (rec.sku != null && rec.sku!.isNotEmpty ? ' · SKU ${rec.sku}' : ''),
                        style: const TextStyle(color: Color(0xFF94A3B8), fontSize: 11),
                      ),
                  ],
                ),
              ),
              const SizedBox(width: 8),
              _buildTags(),
            ],
          ),
          const SizedBox(height: 10),
          Text(
            rec.justificacion,
            style: const TextStyle(color: Color(0xFFE2E8F0), fontSize: 12, height: 1.45),
          ),
          const SizedBox(height: 8),
          Container(
            padding: const EdgeInsets.all(10),
            decoration: BoxDecoration(
              color: const Color(0xFF064E3B).withValues(alpha: 0.45),
              borderRadius: BorderRadius.circular(8),
              border: Border.all(color: const Color(0xFF059669).withValues(alpha: 0.3)),
            ),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text('👉 ', style: TextStyle(fontSize: 12)),
                Expanded(
                  child: Text(
                    rec.accionSugerida,
                    style: const TextStyle(color: Color(0xFF6EE7B7), fontSize: 12, height: 1.4),
                  ),
                ),
              ],
            ),
          ),
          if (metrics.isNotEmpty) ...[
            const SizedBox(height: 10),
            Wrap(
              spacing: 6,
              runSpacing: 6,
              children: metrics
                  .map(
                    (m) => Container(
                      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                      decoration: BoxDecoration(
                        color: const Color(0xFF0F172A),
                        borderRadius: BorderRadius.circular(6),
                        border: Border.all(color: const Color(0xFF334155)),
                      ),
                      child: Text(
                        '${m.label}: ${m.value}',
                        style: const TextStyle(
                          color: Color(0xFFCBD5E1),
                          fontSize: 10,
                          fontFamily: 'monospace',
                        ),
                      ),
                    ),
                  )
                  .toList(),
            ),
          ],
          if (rec.evidencia.isNotEmpty) ...[
            const SizedBox(height: 8),
            ...rec.evidencia.map(
              (ev) => Padding(
                padding: const EdgeInsets.only(bottom: 2),
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text('• ', style: TextStyle(color: Color(0xFF94A3B8), fontSize: 11)),
                    Expanded(
                      child: Text(
                        ev,
                        style: const TextStyle(color: Color(0xFF94A3B8), fontSize: 11),
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ],
          const SizedBox(height: 8),
          Row(
            mainAxisAlignment: MainAxisAlignment.end,
            children: [
              TextButton.icon(
                style: TextButton.styleFrom(
                  visualDensity: VisualDensity.compact,
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                ),
                icon: Icon(
                  isSpeakingThis ? Icons.stop_circle_outlined : Icons.volume_up_outlined,
                  size: 16,
                  color: isSpeakingThis ? const Color(0xFFEF4444) : const Color(0xFF38BDF8),
                ),
                label: Text(
                  isSpeakingThis ? 'Detener audio' : 'Escuchar',
                  style: TextStyle(
                    fontSize: 11,
                    color: isSpeakingThis ? const Color(0xFFEF4444) : const Color(0xFF38BDF8),
                  ),
                ),
                onPressed: () => controller.speakRecommendation(rec),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildTags() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.end,
      children: [
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
          decoration: BoxDecoration(
            color: RecommendationsSheet.priorityBg(rec.prioridad),
            borderRadius: BorderRadius.circular(10),
          ),
          child: Text(
            rec.prioridadLabel,
            style: const TextStyle(color: Colors.white, fontSize: 10, fontWeight: FontWeight.bold),
          ),
        ),
        const SizedBox(height: 4),
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
          decoration: BoxDecoration(
            color: const Color(0xFF334155),
            borderRadius: BorderRadius.circular(10),
          ),
          child: Text(
            rec.tipoLabel,
            style: const TextStyle(color: Color(0xFFCBD5E1), fontSize: 10),
          ),
        ),
      ],
    );
  }
}