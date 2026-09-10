import 'package:flutter/material.dart';
import '../controllers/notification_controller.dart';
import '../models/notification_model.dart';

class NotificationsView extends StatefulWidget {
  final NotificationController notificationController;

  const NotificationsView({super.key, required this.notificationController});

  @override
  State<NotificationsView> createState() => _NotificationsViewState();
}

class _NotificationsViewState extends State<NotificationsView> {
  @override
  void initState() {
    super.initState();
    _loadData();
  }

  Future<void> _loadData() async {
    await widget.notificationController.fetchNotifications();
    if (mounted) setState(() {});
  }

  @override
  Widget build(BuildContext context) {
    final controller = widget.notificationController;

    return Scaffold(
      appBar: AppBar(
        title: const Text('Notificaciones'),
        backgroundColor: const Color(0xFF1E293B),
      ),
      body: controller.isLoading
          ? const Center(child: CircularProgressIndicator())
          : RefreshIndicator(
              onRefresh: _loadData,
              child: controller.notifications.isEmpty
                  ? const Center(
                      child: Text(
                        'No tienes notificaciones pendientes',
                        style: TextStyle(color: Colors.white70),
                      ),
                    )
                  : ListView.builder(
                      padding: const EdgeInsets.all(16.0),
                      itemCount: controller.notifications.length,
                      itemBuilder: (context, index) {
                        final notif = controller.notifications[index];
                        return _buildNotificationCard(notif);
                      },
                    ),
            ),
    );
  }

  Widget _buildNotificationCard(NotificationModel notif) {
    return Card(
      color: notif.leida ? const Color(0xFF1E293B) : const Color(0xFF0F2942),
      margin: const EdgeInsets.only(bottom: 12.0),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
        side: BorderSide(
          color: notif.leida ? const Color(0xFF334155) : const Color(0xFF38BDF8),
          width: notif.leida ? 1 : 1.5,
        ),
      ),
      child: ListTile(
        contentPadding: const EdgeInsets.all(16.0),
        leading: CircleAvatar(
          backgroundColor: notif.leida ? Colors.grey.shade800 : Colors.blue.shade900,
          child: Icon(
            notif.leida ? Icons.notifications_none : Icons.notifications_active,
            color: notif.leida ? Colors.grey : Colors.lightBlueAccent,
          ),
        ),
        title: Text(
          notif.titulo,
          style: TextStyle(
            fontWeight: notif.leida ? FontWeight.normal : FontWeight.bold,
            color: Colors.white,
          ),
        ),
        subtitle: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const SizedBox(height: 6),
            Text(
              notif.contenido,
              style: const TextStyle(color: Colors.white70, fontSize: 13),
            ),
            const SizedBox(height: 8),
            Text(
              notif.fechaenvio,
              style: const TextStyle(color: Colors.white38, fontSize: 11),
            ),
          ],
        ),
        trailing: !notif.leida
            ? IconButton(
                icon: const Icon(Icons.check_circle_outline, color: Colors.lightBlueAccent),
                onPressed: () async {
                  await widget.notificationController.markAsRead(notif.idnotificacion);
                  if (mounted) setState(() {});
                },
                tooltip: 'Marcar como leída',
              )
            : null,
      ),
    );
  }
}
