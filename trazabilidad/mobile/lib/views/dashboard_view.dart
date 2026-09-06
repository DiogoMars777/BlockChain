import 'package:flutter/material.dart';
import '../controllers/auth_controller.dart';
import '../controllers/notification_controller.dart';
import 'login_view.dart';
import 'notifications_view.dart';

class DashboardView extends StatefulWidget {
  final AuthController authController;

  const DashboardView({super.key, required this.authController});

  @override
  State<DashboardView> createState() => _DashboardViewState();
}

class _DashboardViewState extends State<DashboardView> {
  late final NotificationController _notificationController;

  @override
  void initState() {
    super.initState();
    _notificationController = NotificationController(authController: widget.authController);
    _notificationController.fetchNotifications().then((_) {
      if (mounted) setState(() {});
    });
  }

  @override
  Widget build(BuildContext context) {
    final user = widget.authController.currentUser;

    return Scaffold(
      backgroundColor: const Color(0xFF0F172A),
      appBar: AppBar(
        backgroundColor: const Color(0xFF1E293B),
        title: const Row(
          children: [
            Icon(Icons.shield, color: Color(0xFF38BDF8)),
            SizedBox(width: 8),
            Text('Trazabilidad Dashboard', style: TextStyle(fontSize: 18, color: Colors.white)),
          ],
        ),
        actions: [
          Stack(
            children: [
              IconButton(
                icon: const Icon(Icons.notifications_outlined, color: Color(0xFF38BDF8)),
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
                  right: 8,
                  top: 8,
                  child: Container(
                    padding: const EdgeInsets.all(4),
                    decoration: const BoxDecoration(
                      color: Colors.red,
                      shape: BoxShape.circle,
                    ),
                    child: Text(
                      '${_notificationController.unreadCount}',
                      style: const TextStyle(color: Colors.white, fontSize: 10, fontWeight: FontWeight.bold),
                    ),
                  ),
                ),
            ],
          ),
          IconButton(
            icon: const Icon(Icons.logout, color: Color(0xFFF87171)),
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
        ],
      ),
      body: Padding(
        padding: const EdgeInsets.all(20.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
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
          ],
        ),
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
