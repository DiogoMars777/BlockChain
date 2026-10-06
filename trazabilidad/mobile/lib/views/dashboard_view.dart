import 'package:flutter/material.dart';
import '../controllers/auth_controller.dart';
import '../controllers/notification_controller.dart';
import '../controllers/bitacora_controller.dart';
import '../controllers/qr_controller.dart';
import '../controllers/transport_controller.dart';
import '../controllers/purchase_controller.dart';
import 'login_view.dart';
import 'notifications_view.dart';
import 'bitacora_view.dart';
import 'qr_generator_view.dart';
import 'shipment_list_view.dart';
import 'purchase_list_view.dart';
import '../controllers/ai_assistant_controller.dart';
import 'widgets/voice_assistant_sheet.dart';
import '../controllers/recommendation_controller.dart';
import 'widgets/recommendations_sheet.dart';

class DashboardView extends StatefulWidget {
  final AuthController authController;

  const DashboardView({super.key, required this.authController});

  @override
  State<DashboardView> createState() => _DashboardViewState();
}

class _DashboardViewState extends State<DashboardView> {
  late final NotificationController _notificationController;
  late final BitacoraController _bitacoraController;
  late final QrController _qrController;
  late final TransportController _transportController;
  late final PurchaseController _purchaseController;
  late final AiAssistantController _aiController;
  late final RecommendationController _recommendationController;

  @override
  void initState() {
    super.initState();
    _aiController = AiAssistantController();
    _recommendationController = RecommendationController();
    _notificationController = NotificationController(authController: widget.authController);
    _bitacoraController = BitacoraController();
    _qrController = QrController();
    _transportController = TransportController();
    _purchaseController = PurchaseController();
    _purchaseController.loadPurchases();
    _notificationController.fetchNotifications().then((_) {
      if (mounted) setState(() {});
    });
  }

  @override
  void dispose() {
    _aiController.dispose();
    _recommendationController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final user = widget.authController.currentUser;

    return Scaffold(
      backgroundColor: const Color(0xFF0F172A),
      appBar: AppBar(
        backgroundColor: const Color(0xFF1E293B),
        elevation: 2,
        title: const Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(Icons.shield, color: Color(0xFF38BDF8), size: 22),
            SizedBox(width: 8),
            Text(
              'Trazabilidad',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Colors.white, letterSpacing: 0.3),
            ),
          ],
        ),
        actions: [
          // Botón Micrófono (Informes de Voz IA) - Botón Sólido Destacado
          Padding(
            padding: const EdgeInsets.symmetric(vertical: 9, horizontal: 3),
            child: InkWell(
              borderRadius: BorderRadius.circular(10),
              onTap: () => VoiceAssistantSheet.show(context, _aiController),
              child: Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 6),
                decoration: BoxDecoration(
                  color: const Color(0xFF0284C7),
                  borderRadius: BorderRadius.circular(10),
                  border: Border.all(color: const Color(0xFF38BDF8), width: 1.2),
                  boxShadow: [
                    BoxShadow(
                      color: const Color(0xFF0284C7).withValues(alpha: 0.35),
                      blurRadius: 4,
                      offset: const Offset(0, 1),
                    ),
                  ],
                ),
                child: const Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Icon(Icons.mic, color: Colors.white, size: 17),
                    SizedBox(width: 3),
                    Text('Voz', style: TextStyle(color: Colors.white, fontSize: 11, fontWeight: FontWeight.bold)),
                  ],
                ),
              ),
            ),
          ),

          // Botón Estrella (Recomendaciones de Pricing IA) - Botón Sólido Destacado
          Padding(
            padding: const EdgeInsets.symmetric(vertical: 9, horizontal: 3),
            child: InkWell(
              borderRadius: BorderRadius.circular(10),
              onTap: () => RecommendationsSheet.show(context, _recommendationController),
              child: Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 6),
                decoration: BoxDecoration(
                  color: const Color(0xFF7C3AED),
                  borderRadius: BorderRadius.circular(10),
                  border: Border.all(color: const Color(0xFFA78BFA), width: 1.2),
                  boxShadow: [
                    BoxShadow(
                      color: const Color(0xFF7C3AED).withValues(alpha: 0.35),
                      blurRadius: 4,
                      offset: const Offset(0, 1),
                    ),
                  ],
                ),
                child: const Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Icon(Icons.auto_awesome, color: Color(0xFFFDE047), size: 16),
                    SizedBox(width: 3),
                    Text('IA', style: TextStyle(color: Colors.white, fontSize: 11, fontWeight: FontWeight.bold)),
                  ],
                ),
              ),
            ),
          ),

          // Bitácora
          IconButton(
            icon: const Icon(Icons.receipt_long_outlined, color: Color(0xFF94A3B8), size: 21),
            tooltip: 'Consultar Bitácora',
            padding: const EdgeInsets.all(6),
            constraints: const BoxConstraints(),
            onPressed: () {
              Navigator.of(context).push(
                MaterialPageRoute(
                  builder: (_) => BitacoraView(bitacoraController: _bitacoraController),
                ),
              );
            },
          ),

          // Notificaciones
          Stack(
            alignment: Alignment.center,
            children: [
              IconButton(
                icon: const Icon(Icons.notifications_outlined, color: Color(0xFF94A3B8), size: 21),
                tooltip: 'Notificaciones',
                padding: const EdgeInsets.all(6),
                constraints: const BoxConstraints(),
                onPressed: () {
                  Navigator.of(context).push(
                    MaterialPageRoute(
                      builder: (_) => NotificationsView(notificationController: _notificationController),
                    ),
                  ).then((_) => setState(() {}));
                },
              ),
              if (_notificationController.unreadCount > 0)
                Positioned(
                  right: 2,
                  top: 8,
                  child: Container(
                    padding: const EdgeInsets.all(3.5),
                    decoration: const BoxDecoration(
                      color: Colors.red,
                      shape: BoxShape.circle,
                    ),
                    child: Text(
                      '${_notificationController.unreadCount}',
                      style: const TextStyle(color: Colors.white, fontSize: 9, fontWeight: FontWeight.bold),
                    ),
                  ),
                ),
            ],
          ),

          // Logout
          IconButton(
            icon: const Icon(Icons.logout, color: Color(0xFFF87171), size: 21),
            tooltip: 'Cerrar Sesión',
            padding: const EdgeInsets.all(6),
            constraints: const BoxConstraints(),
            onPressed: () async {
              await widget.authController.logout();
              if (context.mounted) {
                Navigator.of(context).pushReplacement(
                  MaterialPageRoute(
                    builder: (_) => LoginView(authController: widget.authController),
                  ),
                );
              }
            },
          ),
          const SizedBox(width: 4),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(20.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Banner de autenticación exitosa
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: const Color(0xFF064E3B),
                borderRadius: BorderRadius.circular(12),
              ),
              child: const Row(
                children: [
                  Icon(Icons.check_circle_outline, color: Color(0xFFA7F3D0)),
                  SizedBox(width: 12),
                  Expanded(
                    child: Text(
                      'Autenticado exitosamente en la app móvil',
                      style: TextStyle(color: Color(0xFFA7F3D0), fontWeight: FontWeight.bold),
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 20),

            // Tarjeta de Información de Usuario
            if (user != null) ...[
              Card(
                color: const Color(0xFF1E293B),
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                child: Padding(
                  padding: const EdgeInsets.all(20.0),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          const Text(
                            'Información del Usuario',
                            style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Colors.white),
                          ),
                          Container(
                            padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                            decoration: BoxDecoration(
                              color: const Color(0xFF0284C7),
                              borderRadius: BorderRadius.circular(20),
                            ),
                            child: const Text('Activo', style: TextStyle(color: Colors.white, fontSize: 12)),
                          ),
                        ],
                      ),
                      const Divider(color: Color(0xFF334155), height: 24),

                      _infoRow('Nombre Completo:', user.nombrecompleto),
                      _infoRow('Correo Electrónico:', user.email),
                      if (user.tenant != null) ...[
                        _infoRow('Empresa (Tenant):', user.tenant!.nombre),
                        _infoRow('NIT / Razón Social:', '${user.tenant!.nit} - ${user.tenant!.razonsocial}'),
                      ],
                      _infoRow('ID Usuario:', '#${user.idusuario}'),
                    ],
                  ),
                ),
              ),
            ],

            const SizedBox(height: 20),

            // Sección de Casos de Uso / Módulos
            const Text(
              'Módulos y Auditoría',
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: Colors.white),
            ),
            const SizedBox(height: 12),

            // Tarjeta Destacada: Informes Dinámicos por Voz con IA (CU-022)
            Card(
              color: const Color(0xFF1E293B),
              elevation: 6,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(16),
                side: const BorderSide(color: Color(0xFF38BDF8), width: 1.8),
              ),
              child: InkWell(
                borderRadius: BorderRadius.circular(16),
                onTap: () => VoiceAssistantSheet.show(context, _aiController),
                child: Container(
                  decoration: BoxDecoration(
                    borderRadius: BorderRadius.circular(16),
                    gradient: LinearGradient(
                      begin: Alignment.topLeft,
                      end: Alignment.bottomRight,
                      colors: [
                        const Color(0xFF0284C7).withValues(alpha: 0.18),
                        const Color(0xFF1E293B),
                      ],
                    ),
                  ),
                  padding: const EdgeInsets.all(18.0),
                  child: Row(
                    children: [
                      Container(
                        padding: const EdgeInsets.all(12),
                        decoration: BoxDecoration(
                          color: const Color(0xFF0284C7).withValues(alpha: 0.25),
                          borderRadius: BorderRadius.circular(14),
                          border: Border.all(color: const Color(0xFF38BDF8).withValues(alpha: 0.4)),
                        ),
                        child: const Icon(
                          Icons.mic_rounded,
                          size: 32,
                          color: Color(0xFF38BDF8),
                        ),
                      ),
                      const SizedBox(width: 16),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Row(
                              children: [
                                const Text(
                                  'Informes con Voz (IA)',
                                  style: TextStyle(
                                    fontSize: 16,
                                    fontWeight: FontWeight.bold,
                                    color: Colors.white,
                                  ),
                                ),
                                const SizedBox(width: 8),
                                Container(
                                  padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                                  decoration: const BoxDecoration(
                                    color: Color(0xFF0284C7),
                                    borderRadius: BorderRadius.all(Radius.circular(6)),
                                  ),
                                  child: const Text('CU-022', style: TextStyle(color: Colors.white, fontSize: 10, fontWeight: FontWeight.bold)),
                                ),
                              ],
                            ),
                            const SizedBox(height: 4),
                            const Text(
                              'Consultas dinámicas de stock, compras y telemetría con descarga en PDF y Excel',
                              style: TextStyle(
                                fontSize: 12,
                                color: Color(0xFF94A3B8),
                              ),
                            ),
                          ],
                        ),
                      ),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                        decoration: BoxDecoration(
                          color: const Color(0xFF0284C7),
                          borderRadius: BorderRadius.circular(8),
                          border: Border.all(color: const Color(0xFF38BDF8), width: 1.2),
                        ),
                        child: const Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            Icon(Icons.mic, size: 14, color: Colors.white),
                            SizedBox(width: 4),
                            Text('Hablar', style: TextStyle(color: Colors.white, fontSize: 11, fontWeight: FontWeight.bold)),
                          ],
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ),
            const SizedBox(height: 12),

            // Tarjeta Destacada: Recomendaciones de Pricing e Inventario (IA)
            Card(
              color: const Color(0xFF1E293B),
              elevation: 6,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(16),
                side: const BorderSide(color: Color(0xFF7C3AED), width: 1.8),
              ),
              child: InkWell(
                borderRadius: BorderRadius.circular(16),
                onTap: () => RecommendationsSheet.show(context, _recommendationController),
                child: Container(
                  decoration: BoxDecoration(
                    borderRadius: BorderRadius.circular(16),
                    gradient: LinearGradient(
                      begin: Alignment.topLeft,
                      end: Alignment.bottomRight,
                      colors: [
                        const Color(0xFF7C3AED).withValues(alpha: 0.18),
                        const Color(0xFF1E293B),
                      ],
                    ),
                  ),
                  padding: const EdgeInsets.all(18.0),
                  child: Row(
                    children: [
                      Container(
                        padding: const EdgeInsets.all(12),
                        decoration: BoxDecoration(
                          color: const Color(0xFF7C3AED).withValues(alpha: 0.25),
                          borderRadius: BorderRadius.circular(14),
                          border: Border.all(color: const Color(0xFFA78BFA).withValues(alpha: 0.4)),
                        ),
                        child: const Icon(
                          Icons.trending_up_rounded,
                          size: 32,
                          color: Color(0xFFA78BFA),
                        ),
                      ),
                      const SizedBox(width: 16),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Row(
                              children: [
                                const Text(
                                  'Recomendaciones de Pricing',
                                  style: TextStyle(
                                    fontSize: 16,
                                    fontWeight: FontWeight.bold,
                                    color: Colors.white,
                                  ),
                                ),
                                const SizedBox(width: 8),
                                Container(
                                  padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                                  decoration: const BoxDecoration(
                                    color: Color(0xFF7C3AED),
                                    borderRadius: BorderRadius.all(Radius.circular(6)),
                                  ),
                                  child: const Text('IA', style: TextStyle(color: Colors.white, fontSize: 10, fontWeight: FontWeight.bold)),
                                ),
                              ],
                            ),
                            const SizedBox(height: 4),
                            const Text(
                              'Análisis de márgenes, rotación, sobrestock y devoluciones del catálogo',
                              style: TextStyle(
                                fontSize: 12,
                                color: Color(0xFF94A3B8),
                              ),
                            ),
                          ],
                        ),
                      ),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                        decoration: BoxDecoration(
                          color: const Color(0xFF7C3AED),
                          borderRadius: BorderRadius.circular(8),
                          border: Border.all(color: const Color(0xFFA78BFA), width: 1.2),
                        ),
                        child: const Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            Icon(Icons.auto_awesome, size: 14, color: Color(0xFFFDE047)),
                            SizedBox(width: 4),
                            Text('Ver Precios', style: TextStyle(color: Colors.white, fontSize: 11, fontWeight: FontWeight.bold)),
                          ],
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ),
            const SizedBox(height: 12),

            // Botón/Tarjeta destacada para CU-005 Bitácora de Auditoría
            Card(
              color: const Color(0xFF1E293B),
              elevation: 4,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(16),
                side: const BorderSide(color: Color(0xFF38BDF8), width: 1.2),
              ),
              child: InkWell(
                borderRadius: BorderRadius.circular(16),
                onTap: () {
                  Navigator.of(context).push(
                    MaterialPageRoute(
                      builder: (_) => BitacoraView(bitacoraController: _bitacoraController),
                    ),
                  );
                },
                child: Padding(
                  padding: const EdgeInsets.all(18.0),
                  child: Row(
                    children: [
                      Container(
                        padding: const EdgeInsets.all(12),
                        decoration: BoxDecoration(
                          color: const Color(0xFF38BDF8).withValues(alpha: 0.15),
                          borderRadius: BorderRadius.circular(12),
                        ),
                        child: const Icon(
                          Icons.receipt_long_rounded,
                          size: 30,
                          color: Color(0xFF38BDF8),
                        ),
                      ),
                      const SizedBox(width: 16),
                      const Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              'Bitácora de Auditoría',
                              style: TextStyle(
                                fontSize: 16,
                                fontWeight: FontWeight.bold,
                                color: Colors.white,
                              ),
                            ),
                            SizedBox(height: 4),
                            Text(
                              'Consultar métodos GET/POST/PUT, usuarios, IPs y fechas',
                              style: TextStyle(
                                fontSize: 12,
                                color: Color(0xFF94A3B8),
                              ),
                            ),
                          ],
                        ),
                      ),
                      const Icon(
                        Icons.arrow_forward_ios_rounded,
                        size: 18,
                        color: Color(0xFF38BDF8),
                      ),
                    ],
                  ),
                ),
              ),
            ),
            const SizedBox(height: 12),

            // Tarjeta CU-016: Códigos QR de Unidades
            Card(
              color: const Color(0xFF1E293B),
              elevation: 4,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(16),
                side: const BorderSide(color: Color(0xFF10B981), width: 1.2),
              ),
              child: InkWell(
                borderRadius: BorderRadius.circular(16),
                onTap: () {
                  Navigator.of(context).push(
                    MaterialPageRoute(
                      builder: (_) => QrGeneratorView(qrController: _qrController),
                    ),
                  );
                },
                child: Padding(
                  padding: const EdgeInsets.all(18.0),
                  child: Row(
                    children: [
                      Container(
                        padding: const EdgeInsets.all(12),
                        decoration: BoxDecoration(
                          color: const Color(0xFF10B981).withValues(alpha: 0.15),
                          borderRadius: BorderRadius.circular(12),
                        ),
                        child: const Icon(
                          Icons.qr_code_2_rounded,
                          size: 30,
                          color: Color(0xFF10B981),
                        ),
                      ),
                      const SizedBox(width: 16),
                      const Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              'Códigos QR (CU-016)',
                              style: TextStyle(
                                fontSize: 16,
                                fontWeight: FontWeight.bold,
                                color: Colors.white,
                              ),
                            ),
                            SizedBox(height: 4),
                            Text(
                              'Generar y visualizar códigos QR de unidades individuales y en lote',
                              style: TextStyle(
                                fontSize: 12,
                                color: Color(0xFF94A3B8),
                              ),
                            ),
                          ],
                        ),
                      ),
                      const Icon(
                        Icons.arrow_forward_ios_rounded,
                        size: 18,
                        color: Color(0xFF10B981),
                      ),
                    ],
                  ),
                ),
              ),
            ),
            const SizedBox(height: 12),

            // Tarjeta CU-021: Envíos y Telemetría de Transporte
            Card(
              color: const Color(0xFF1E293B),
              elevation: 4,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(16),
                side: const BorderSide(color: Color(0xFFF59E0B), width: 1.2),
              ),
              child: InkWell(
                borderRadius: BorderRadius.circular(16),
                onTap: () {
                  Navigator.of(context).push(
                    MaterialPageRoute(
                      builder: (_) => ShipmentListView(transportController: _transportController),
                    ),
                  );
                },
                child: Padding(
                  padding: const EdgeInsets.all(18.0),
                  child: Row(
                    children: [
                      Container(
                        padding: const EdgeInsets.all(12),
                        decoration: BoxDecoration(
                          color: const Color(0xFFF59E0B).withValues(alpha: 0.15),
                          borderRadius: BorderRadius.circular(12),
                        ),
                        child: const Icon(
                          Icons.local_shipping_rounded,
                          size: 30,
                          color: Color(0xFFF59E0B),
                        ),
                      ),
                      const SizedBox(width: 16),
                      const Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              'Transporte y Telemetría (CU-021)',
                              style: TextStyle(
                                fontSize: 16,
                                fontWeight: FontWeight.bold,
                                color: Colors.white,
                              ),
                            ),
                            SizedBox(height: 4),
                            Text(
                              'Monitoreo de envíos, línea de tiempo y registro de condiciones IoT',
                              style: TextStyle(
                                fontSize: 12,
                                color: Color(0xFF94A3B8),
                              ),
                            ),
                          ],
                        ),
                      ),
                      const Icon(
                        Icons.arrow_forward_ios_rounded,
                        size: 18,
                        color: Color(0xFFF59E0B),
                      ),
                    ],
                  ),
                ),
              ),
            ),
            const SizedBox(height: 12),

            // Tarjeta CU-010: Gestión de Órdenes de Compra
            Card(
              color: const Color(0xFF1E293B),
              elevation: 4,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(16),
                side: const BorderSide(color: Color(0xFF0284C7), width: 1.2),
              ),
              child: InkWell(
                borderRadius: BorderRadius.circular(16),
                onTap: () {
                  Navigator.of(context).push(
                    MaterialPageRoute(
                      builder: (_) => PurchaseListView(controller: _purchaseController),
                    ),
                  ).then((_) => _purchaseController.loadPurchases());
                },
                child: Padding(
                  padding: const EdgeInsets.all(18.0),
                  child: Row(
                    children: [
                      Container(
                        padding: const EdgeInsets.all(12),
                        decoration: BoxDecoration(
                          color: const Color(0xFF0284C7).withValues(alpha: 0.15),
                          borderRadius: BorderRadius.circular(12),
                        ),
                        child: const Icon(
                          Icons.shopping_cart_checkout_rounded,
                          size: 30,
                          color: Color(0xFF38BDF8),
                        ),
                      ),
                      const SizedBox(width: 16),
                      const Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              'Órdenes de Compra (CU-010)',
                              style: TextStyle(
                                fontSize: 16,
                                fontWeight: FontWeight.bold,
                                color: Colors.white,
                              ),
                            ),
                            SizedBox(height: 4),
                            Text(
                              'Gestión de adquisiciones, emisión de órdenes y catálogo de variantes',
                              style: TextStyle(
                                fontSize: 12,
                                color: Color(0xFF94A3B8),
                              ),
                            ),
                          ],
                        ),
                      ),
                      const Icon(
                        Icons.arrow_forward_ios_rounded,
                        size: 18,
                        color: Color(0xFF38BDF8),
                      ),
                    ],
                  ),
                ),
              ),
            ),
            const SizedBox(height: 12),

            // Tarjeta CU-011: Aprobación / Rechazo de Compras
            ListenableBuilder(
              listenable: _purchaseController,
              builder: (context, _) {
                final pending = _purchaseController.pendingCount;
                return Card(
                  color: const Color(0xFF1E293B),
                  elevation: 4,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(16),
                    side: BorderSide(
                      color: pending > 0 ? const Color(0xFFF59E0B) : const Color(0xFF334155),
                      width: pending > 0 ? 1.5 : 1.0,
                    ),
                  ),
                  child: InkWell(
                    borderRadius: BorderRadius.circular(16),
                    onTap: () {
                      Navigator.of(context).push(
                        MaterialPageRoute(
                          builder: (_) => PurchaseListView(
                            controller: _purchaseController,
                            initialOnlyPending: true,
                          ),
                        ),
                      ).then((_) => _purchaseController.loadPurchases());
                    },
                    child: Padding(
                      padding: const EdgeInsets.all(18.0),
                      child: Row(
                        children: [
                          Container(
                            padding: const EdgeInsets.all(12),
                            decoration: BoxDecoration(
                              color: const Color(0xFFF59E0B).withValues(alpha: 0.15),
                              borderRadius: BorderRadius.circular(12),
                            ),
                            child: const Icon(
                              Icons.fact_check_rounded,
                              size: 30,
                              color: Color(0xFFF59E0B),
                            ),
                          ),
                          const SizedBox(width: 16),
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Row(
                                  children: [
                                    const Text(
                                      'Aprobar Compras (CU-011)',
                                      style: TextStyle(
                                        fontSize: 16,
                                        fontWeight: FontWeight.bold,
                                        color: Colors.white,
                                      ),
                                    ),
                                    if (pending > 0) ...[
                                      const SizedBox(width: 8),
                                      Container(
                                        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                                        decoration: BoxDecoration(
                                          color: const Color(0xFFF59E0B),
                                          borderRadius: BorderRadius.circular(10),
                                        ),
                                        child: Text(
                                          '$pending pendiente${pending > 1 ? "s" : ""}',
                                          style: const TextStyle(color: Colors.black, fontSize: 10, fontWeight: FontWeight.bold),
                                        ),
                                      ),
                                    ],
                                  ],
                                ),
                                const SizedBox(height: 4),
                                const Text(
                                  'Aprobación ejecutiva, validación de presupuestos y rechazos',
                                  style: TextStyle(
                                    fontSize: 12,
                                    color: Color(0xFF94A3B8),
                                  ),
                                ),
                              ],
                            ),
                          ),
                          const Icon(
                            Icons.arrow_forward_ios_rounded,
                            size: 18,
                            color: Color(0xFFF59E0B),
                          ),
                        ],
                      ),
                    ),
                  ),
                );
              },
            ),
          ],
        ),
      ),
      floatingActionButton: FloatingActionButton.extended(
        backgroundColor: const Color(0xFF0284C7),
        elevation: 6,
        icon: const Icon(Icons.mic, color: Colors.white),
        label: const Text(
          'Comando de Voz IA',
          style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
        ),
        onPressed: () => VoiceAssistantSheet.show(context, _aiController),
      ),
    );
  }

  Widget _infoRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 6.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(label, style: const TextStyle(color: Color(0xFF94A3B8), fontSize: 12)),
          const SizedBox(height: 2),
          Text(value, style: const TextStyle(color: Colors.white, fontSize: 15, fontWeight: FontWeight.w500)),
        ],
      ),
    );
  }
}
