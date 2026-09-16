import 'package:flutter/material.dart';
import '../controllers/transport_controller.dart';
import '../models/transport_model.dart';

class RecordTransportEventView extends StatefulWidget {
  final ShipmentModel envio;
  final TransportController transportController;

  const RecordTransportEventView({
    super.key,
    required this.envio,
    required this.transportController,
  });

  @override
  State<RecordTransportEventView> createState() => _RecordTransportEventViewState();
}

class _RecordTransportEventViewState extends State<RecordTransportEventView> {
  final _formKey = GlobalKey<FormState>();

  String _tipoEvento = 'despacho';
  final TextEditingController _idUbicacionController = TextEditingController(text: '1');
  final TextEditingController _descripcionController = TextEditingController();

  // Telemetría IoT / Ambiental
  final TextEditingController _tempController = TextEditingController();
  final TextEditingController _humController = TextEditingController();
  final TextEditingController _vibracionController = TextEditingController();
  final TextEditingController _presionController = TextEditingController();

  final List<Map<String, String>> _tiposEvento = [
    {'value': 'despacho', 'label': 'Despacho Inicial'},
    {'value': 'transito_aeropuerto', 'label': 'Tránsito Aeropuerto / Hub'},
    {'value': 'control_calidad', 'label': 'Control de Calidad en Ruta'},
    {'value': 'almacenamiento_temporal', 'label': 'Almacenamiento Temporal'},
    {'value': 'inspeccion_aduanera', 'label': 'Inspección Aduanera'},
    {'value': 'entrega_final', 'label': 'Entrega Final en Destino'},
    {'value': 'alerta_temperatura', 'label': 'Alerta de Temperatura Excedida'},
    {'value': 'alerta_humedad', 'label': 'Alerta de Humedad Excedida'},
  ];

  @override
  void dispose() {
    _idUbicacionController.dispose();
    _descripcionController.dispose();
    _tempController.dispose();
    _humController.dispose();
    _vibracionController.dispose();
    _presionController.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    if (!_formKey.currentState!.validate()) return;

    final idUbicacion = int.tryParse(_idUbicacionController.text.trim()) ?? 1;

    // Construir condiciones si al menos un campo numérico tiene valor
    TransportConditionModel? condiciones;
    final temp = double.tryParse(_tempController.text.trim());
    final hum = double.tryParse(_humController.text.trim());
    final vib = double.tryParse(_vibracionController.text.trim());
    final pres = double.tryParse(_presionController.text.trim());

    if (temp != null || hum != null || vib != null || pres != null) {
      condiciones = TransportConditionModel(
        temperatura: temp,
        humedad: hum,
        nivelvibracion: vib,
        presion: pres,
        fuentedatos: 'App Móvil Operador',
      );
    }

    final success = await widget.transportController.recordEvent(
      idenvio: widget.envio.idenvio,
      tipoevento: _tipoEvento,
      idubicacion: idUbicacion,
      descripcion: _descripcionController.text.trim().isEmpty ? null : _descripcionController.text.trim(),
      condiciones: condiciones,
    );

    if (mounted) {
      if (success) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            backgroundColor: Color(0xFF059669),
            content: Text('Evento y condiciones de transporte registrados exitosamente.'),
          ),
        );
        Navigator.pop(context);
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            backgroundColor: const Color(0xFFDC2626),
            content: Text(widget.transportController.errorMessage ?? 'Error al registrar evento.'),
          ),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0F172A),
      appBar: AppBar(
        backgroundColor: const Color(0xFF1E293B),
        title: Text(
          'Registrar Evento: ${widget.envio.codigoenvio}',
          style: const TextStyle(color: Colors.white, fontSize: 16),
        ),
        iconTheme: const IconThemeData(color: Colors.white),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(20.0),
        child: Form(
          key: _formKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              // Info del Envío
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: const Color(0xFF1E293B),
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: const Color(0xFF334155)),
                ),
                child: Row(
                  children: [
                    const Icon(Icons.local_shipping, color: Color(0xFF38BDF8), size: 28),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            widget.envio.codigoenvio,
                            style: const TextStyle(
                              color: Colors.white,
                              fontWeight: FontWeight.bold,
                              fontSize: 15,
                            ),
                          ),
                          Text(
                            '${widget.envio.actorOrigenNombre ?? "Origen"} → ${widget.envio.actorDestinoNombre ?? "Destino"}',
                            style: const TextStyle(color: Color(0xFF94A3B8), fontSize: 12),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 20),

              // Tipo de Evento
              const Text(
                'Tipo de Evento Logístico',
                style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 14),
              ),
              const SizedBox(height: 8),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 14),
                decoration: BoxDecoration(
                  color: const Color(0xFF1E293B),
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: const Color(0xFF334155)),
                ),
                child: DropdownButtonHideUnderline(
                  child: DropdownButton<String>(
                    value: _tipoEvento,
                    dropdownColor: const Color(0xFF1E293B),
                    isExpanded: true,
                    items: _tiposEvento.map((item) {
                      return DropdownMenuItem(
                        value: item['value']!,
                        child: Text(
                          item['label']!,
                          style: const TextStyle(color: Colors.white, fontSize: 14),
                        ),
                      );
                    }).toList(),
                    onChanged: (val) {
                      if (val != null) setState(() => _tipoEvento = val);
                    },
                  ),
                ),
              ),
              const SizedBox(height: 16),

              // ID Ubicación
              const Text(
                'ID Ubicación Geográfica',
                style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 14),
              ),
              const SizedBox(height: 8),
              TextFormField(
                controller: _idUbicacionController,
                keyboardType: TextInputType.number,
                style: const TextStyle(color: Colors.white),
                decoration: InputDecoration(
                  hintText: 'Ej. 1',
                  hintStyle: const TextStyle(color: Color(0xFF64748B)),
                  filled: true,
                  fillColor: const Color(0xFF1E293B),
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(12),
                    borderSide: const BorderSide(color: Color(0xFF334155)),
                  ),
                  enabledBorder: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(12),
                    borderSide: const BorderSide(color: Color(0xFF334155)),
                  ),
                ),
                validator: (v) {
                  if (v == null || v.trim().isEmpty) return 'Ingrese el ID de ubicación';
                  if (int.tryParse(v.trim()) == null) return 'Debe ser un número entero';
                  return null;
                },
              ),
              const SizedBox(height: 16),

              // Descripción / Notas
              const Text(
                'Descripción / Observaciones',
                style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 14),
              ),
              const SizedBox(height: 8),
              TextFormField(
                controller: _descripcionController,
                maxLines: 3,
                style: const TextStyle(color: Colors.white),
                decoration: InputDecoration(
                  hintText: 'Detalles sobre la inspección, estado del vehículo o carga...',
                  hintStyle: const TextStyle(color: Color(0xFF64748B), fontSize: 13),
                  filled: true,
                  fillColor: const Color(0xFF1E293B),
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(12),
                    borderSide: const BorderSide(color: Color(0xFF334155)),
                  ),
                  enabledBorder: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(12),
                    borderSide: const BorderSide(color: Color(0xFF334155)),
                  ),
                ),
              ),
              const SizedBox(height: 24),

              // Telemetría IoT y Condiciones de Transporte
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: const Color(0xFF1E293B),
                  borderRadius: BorderRadius.circular(16),
                  border: Border.all(color: const Color(0xFF0284C7).withValues(alpha: 0.4)),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Row(
                      children: [
                        Icon(Icons.sensors, color: Color(0xFF38BDF8), size: 20),
                        SizedBox(width: 8),
                        Text(
                          'Condiciones Ambientales / Sensores IoT',
                          style: TextStyle(
                            color: Color(0xFF38BDF8),
                            fontWeight: FontWeight.bold,
                            fontSize: 14,
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 4),
                    const Text(
                      'Valores opcionales capturados por sensores de cadena de frío o vibración.',
                      style: TextStyle(color: Color(0xFF94A3B8), fontSize: 11),
                    ),
                    const SizedBox(height: 16),
                    Row(
                      children: [
                        Expanded(
                          child: _numericField(
                            controller: _tempController,
                            label: 'Temperatura (°C)',
                            hint: 'Ej. 4.5',
                            icon: Icons.thermostat,
                          ),
                        ),
                        const SizedBox(width: 12),
                        Expanded(
                          child: _numericField(
                            controller: _humController,
                            label: 'Humedad (%)',
                            hint: 'Ej. 45.0',
                            icon: Icons.water_drop,
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 12),
                    Row(
                      children: [
                        Expanded(
                          child: _numericField(
                            controller: _vibracionController,
                            label: 'Vibración (g)',
                            hint: 'Ej. 0.05',
                            icon: Icons.vibration,
                          ),
                        ),
                        const SizedBox(width: 12),
                        Expanded(
                          child: _numericField(
                            controller: _presionController,
                            label: 'Presión (hPa)',
                            hint: 'Ej. 1013.2',
                            icon: Icons.speed,
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 24),

              // Botón Guardar
              ElevatedButton(
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFF0284C7),
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(vertical: 16),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                ),
                onPressed: widget.transportController.isLoading ? null : _submit,
                child: widget.transportController.isLoading
                    ? const SizedBox(
                        height: 20,
                        width: 20,
                        child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2),
                      )
                    : const Text(
                        'Registrar Evento de Trazabilidad',
                        style: TextStyle(fontSize: 15, fontWeight: FontWeight.bold),
                      ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _numericField({
    required TextEditingController controller,
    required String label,
    required String hint,
    required IconData icon,
  }) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Icon(icon, size: 14, color: const Color(0xFF94A3B8)),
            const SizedBox(width: 4),
            Text(label, style: const TextStyle(color: Color(0xFF94A3B8), fontSize: 11)),
          ],
        ),
        const SizedBox(height: 6),
        TextFormField(
          controller: controller,
          keyboardType: const TextInputType.numberWithOptions(decimal: true),
          style: const TextStyle(color: Colors.white, fontSize: 13),
          decoration: InputDecoration(
            hintText: hint,
            hintStyle: const TextStyle(color: Color(0xFF64748B), fontSize: 12),
            filled: true,
            fillColor: const Color(0xFF0F172A),
            contentPadding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(10),
              borderSide: const BorderSide(color: Color(0xFF334155)),
            ),
            enabledBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(10),
              borderSide: const BorderSide(color: Color(0xFF334155)),
            ),
          ),
        ),
      ],
    );
  }
}
