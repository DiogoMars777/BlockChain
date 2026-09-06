import 'package:flutter/material.dart';
import 'controllers/auth_controller.dart';
import 'views/login_view.dart';

void main() {
  runApp(const MultiTenantApp());
}

class MultiTenantApp extends StatefulWidget {
  const MultiTenantApp({super.key});

  @override
  State<MultiTenantApp> createState() => _MultiTenantAppState();
}

class _MultiTenantAppState extends State<MultiTenantApp> {
  final AuthController _authController = AuthController();

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Trazabilidad Multi-Tenant',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        brightness: Brightness.dark,
        primarySwatch: Colors.blue,
        scaffoldBackgroundColor: const Color(0xFF0F172A),
      ),
      home: LoginView(authController: _authController),
    );
  }
}
