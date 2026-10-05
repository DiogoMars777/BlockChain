import 'package:flutter/material.dart';
import '../controllers/purchase_controller.dart';
import '../models/purchase_model.dart';

class PurchaseCreateView extends StatefulWidget {
  final PurchaseController controller;

  const PurchaseCreateView({super.key, required this.controller});

  @override
  State<PurchaseCreateView> createState() => _PurchaseCreateViewState();
}

class _PurchaseCreateViewState extends State<PurchaseCreateView> {
  final _formKey = GlobalKey<FormState>();
  final TextEditingController _orderNumberController = TextEditingController();
  final TextEditingController _dateController = TextEditingController();

  int? _selectedProveedorId;
  DateTime _selectedDate = DateTime.now();
  final List<CompraDetalleCreateModel> _detalles = [];

  @override
  void initState() {
    super.initState();
    _initDefaults();
    widget.controller.loadFormData();
  }

  void _initDefaults() {
    final now = DateTime.now();
    _orderNumberController.text = 'OC-${now.year}-${(now.millisecondsSinceEpoch ~/ 1000) % 90000 + 10000}';
    _dateController.text = '${now.year}-${now.month.toString().padLeft(2, '0')}-${now.day.toString().padLeft(2, '0')}';
  }

  @override
  void dispose() {
    _orderNumberController.dispose();
    _dateController.dispose();
    super.dispose();
  }

  double get _totalOrden => _detalles.fold(0.0, (sum, d) => sum + d.subtotal);

  Future<void> _selectDate() async {
    final picked = await showDatePicker(
      context: context,
      initialDate: _selectedDate,
      firstDate: DateTime(2020),
      lastDate: DateTime(2035),
      builder: (context, child) {
        return Theme(
          data: ThemeData.dark().copyWith(
            colorScheme: const ColorScheme.dark(
              primary: Color(0xFF0EA5E9),
              surface: Color(0xFF1E293B),
            ),
          ),
          child: child!,
        );
      },
    );
    if (picked != null) {
      setState(() {
        _selectedDate = picked;
        _dateController.text = '${picked.year}-${picked.month.toString().padLeft(2, '0')}-${picked.day.toString().padLeft(2, '0')}';
      });
    }
  }

  void _openAddVariantDialog() {
    if (widget.controller.catalogItems.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('No hay variantes disponibles en el catálogo de la empresa.'),
          backgroundColor: Colors.amber,
        ),
      );
      return;
    }

    CatalogItemModel? selectedVariant = widget.controller.catalogItems.first;
    final qtyController = TextEditingController(text: '10');
    final costController = TextEditingController(
      text: selectedVariant.costopromedio > 0
          ? selectedVariant.costopromedio.toStringAsFixed(2)
          : selectedVariant.precioventa.toStringAsFixed(2),
    );

    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: const Color(0xFF1E293B),
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (ctx) {
        return StatefulBuilder(
          builder: (context, setModalState) {
            return Padding(
              padding: EdgeInsets.only(
                left: 20,
                right: 20,
                top: 20,
                bottom: MediaQuery.of(context).viewInsets.bottom + 24,
              ),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      const Text(
                        'Agregar Variante a la Orden',
                        style: TextStyle(color: Colors.white, fontSize: 18, fontWeight: FontWeight.bold),
                      ),
                      IconButton(
                        icon: const Icon(Icons.close, color: Colors.white70),
                        onPressed: () => Navigator.pop(ctx),
                      ),
                    ],
                  ),
                  const SizedBox(height: 14),

                  // Selector de variante
                  const Text('Variante de Producto:', style: TextStyle(color: Color(0xFF94A3B8), fontSize: 13)),
                  const SizedBox(height: 6),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 12),
                    decoration: BoxDecoration(
                      color: const Color(0xFF0F172A),
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: DropdownButtonHideUnderline(
                      child: DropdownButton<CatalogItemModel>(
                        value: selectedVariant,
                        dropdownColor: const Color(0xFF0F172A),
                        isExpanded: true,
                        icon: const Icon(Icons.arrow_drop_down, color: Color(0xFF38BDF8)),
                        items: widget.controller.catalogItems.map((item) {
                          return DropdownMenuItem<CatalogItemModel>(
                            value: item,
                            child: Text(
                              '${item.productoNombre} - ${item.displayName}',
                              style: const TextStyle(color: Colors.white, fontSize: 13),
                              overflow: TextOverflow.ellipsis,
                            ),
                          );
                        }).toList(),
                        onChanged: (val) {
                          if (val != null) {
                            setModalState(() {
                              selectedVariant = val;
                              final defCost = val.costopromedio > 0 ? val.costopromedio : val.precioventa;
                              costController.text = defCost.toStringAsFixed(2);
                            });
                          }
                        },
                      ),
                    ),
                  ),
                  const SizedBox(height: 14),

                  // Cantidad y Costo Unitario
                  Row(
                    children: [
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            const Text('Cantidad:', style: TextStyle(color: Color(0xFF94A3B8), fontSize: 13)),
                            const SizedBox(height: 6),
                            TextField(
                              controller: qtyController,
                              keyboardType: TextInputType.number,
                              style: const TextStyle(color: Colors.white),
                              decoration: InputDecoration(
                                filled: true,
                                fillColor: const Color(0xFF0F172A),
                                border: OutlineInputBorder(borderRadius: BorderRadius.circular(8)),
                              ),
                            ),
                          ],
                        ),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            const Text('Costo Unit. (USD):', style: TextStyle(color: Color(0xFF94A3B8), fontSize: 13)),
                            const SizedBox(height: 6),
                            TextField(
                              controller: costController,
                              keyboardType: const TextInputType.numberWithOptions(decimal: true),
                              style: const TextStyle(color: Colors.white),
                              decoration: InputDecoration(
                                filled: true,
                                fillColor: const Color(0xFF0F172A),
                                border: OutlineInputBorder(borderRadius: BorderRadius.circular(8)),
                                prefixText: '\$ ',
                                prefixStyle: const TextStyle(color: Color(0xFF38BDF8)),
                              ),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 20),

                  ElevatedButton(
                    style: ElevatedButton.styleFrom(
                      backgroundColor: const Color(0xFF0EA5E9),
                      padding: const EdgeInsets.symmetric(vertical: 14),
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                    ),
                    onPressed: () {
                      final qty = int.tryParse(qtyController.text.trim()) ?? 0;
                      final cost = double.tryParse(costController.text.trim()) ?? 0.0;
                      if (qty <= 0 || cost <= 0) {
                        ScaffoldMessenger.of(context).showSnackBar(
                          const SnackBar(content: Text('Cantidad y costo deben ser mayores a 0.'), backgroundColor: Colors.redAccent),
                        );
                        return;
                      }

                      // Verificar que no esté repetido
                      if (_detalles.any((d) => d.idvariante == selectedVariant!.idvariante)) {
                        ScaffoldMessenger.of(context).showSnackBar(
                          const SnackBar(content: Text('Esta variante ya está agregada en la orden.'), backgroundColor: Colors.amber),
                        );
                        return;
                      }

                      setState(() {
                        _detalles.add(
                          CompraDetalleCreateModel(
                            idvariante: selectedVariant!.idvariante,
                            nombreProducto: selectedVariant!.productoNombre,
                            sku: selectedVariant!.displayName,
                            cantidad: qty,
                            costounitariousd: cost,
                          ),
                        );
                      });
                      Navigator.pop(ctx);
                    },
                    child: const Text('Agregar a la Orden', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
                  ),
                ],
              ),
            );
          },
        );
      },
    );
  }

  void _submitOrder() async {
    if (!_formKey.currentState!.validate()) return;
    if (_selectedProveedorId == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Selecciona un proveedor.'), backgroundColor: Colors.amber),
      );
      return;
    }
    if (_detalles.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Agrega al menos una línea de producto a la orden.'), backgroundColor: Colors.amber),
      );
      return;
    }

    final req = CompraCreateModel(
      idproveedor: _selectedProveedorId!,
      numeroorden: _orderNumberController.text.trim(),
      fechacompra: _dateController.text.trim(),
      detalles: _detalles,
    );

    final success = await widget.controller.create(req);
    if (success && mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(widget.controller.successMessage ?? 'Orden de compra creada exitosamente.'),
          backgroundColor: const Color(0xFF059669),
        ),
      );
      Navigator.pop(context);
    } else if (mounted && widget.controller.errorMessage != null) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(widget.controller.errorMessage!),
          backgroundColor: const Color(0xFFDC2626),
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final provs = widget.controller.proveedores;

    return Scaffold(
      backgroundColor: const Color(0xFF0F172A),
      appBar: AppBar(
        backgroundColor: const Color(0xFF1E293B),
        title: const Text('Nueva Orden de Compra (CU-010)', style: TextStyle(color: Colors.white, fontSize: 18)),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Form(
          key: _formKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              // Cabecera de la Orden
              Card(
                color: const Color(0xFF1E293B),
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text('Datos del Proveedor y Orden', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 16)),
                      const Divider(color: Color(0xFF334155), height: 20),

                      // Proveedor
                      const Text('Proveedor:', style: TextStyle(color: Color(0xFF94A3B8), fontSize: 13)),
                      const SizedBox(height: 6),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 12),
                        decoration: BoxDecoration(
                          color: const Color(0xFF0F172A),
                          borderRadius: BorderRadius.circular(8),
                        ),
                        child: DropdownButtonHideUnderline(
                          child: DropdownButton<int>(
                            value: _selectedProveedorId,
                            hint: const Text('Seleccionar Proveedor', style: TextStyle(color: Color(0xFF64748B), fontSize: 13)),
                            dropdownColor: const Color(0xFF0F172A),
                            isExpanded: true,
                            items: provs.map((p) {
                              return DropdownMenuItem<int>(
                                value: p.idactor,
                                child: Text(p.displayName, style: const TextStyle(color: Colors.white, fontSize: 13)),
                              );
                            }).toList(),
                            onChanged: (val) {
                              setState(() => _selectedProveedorId = val);
                            },
                          ),
                        ),
                      ),
                      const SizedBox(height: 14),

                      // Número de Orden
                      const Text('Número de Orden:', style: TextStyle(color: Color(0xFF94A3B8), fontSize: 13)),
                      const SizedBox(height: 6),
                      TextFormField(
                        controller: _orderNumberController,
                        style: const TextStyle(color: Colors.white),
                        decoration: InputDecoration(
                          filled: true,
                          fillColor: const Color(0xFF0F172A),
                          border: OutlineInputBorder(borderRadius: BorderRadius.circular(8)),
                          suffixIcon: IconButton(
                            icon: const Icon(Icons.refresh, color: Color(0xFF38BDF8)),
                            tooltip: 'Generar nuevo número',
                            onPressed: _initDefaults,
                          ),
                        ),
                        validator: (v) => v == null || v.trim().isEmpty ? 'Requerido' : null,
                      ),
                      const SizedBox(height: 14),

                      // Fecha de Compra
                      const Text('Fecha de Emisión:', style: TextStyle(color: Color(0xFF94A3B8), fontSize: 13)),
                      const SizedBox(height: 6),
                      TextFormField(
                        controller: _dateController,
                        readOnly: true,
                        onTap: _selectDate,
                        style: const TextStyle(color: Colors.white),
                        decoration: InputDecoration(
                          filled: true,
                          fillColor: const Color(0xFF0F172A),
                          border: OutlineInputBorder(borderRadius: BorderRadius.circular(8)),
                          suffixIcon: const Icon(Icons.calendar_month, color: Color(0xFF38BDF8)),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 18),

              // Sección de Ítems
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  const Text('Líneas de la Orden', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 16)),
                  ElevatedButton.icon(
                    style: ElevatedButton.styleFrom(
                      backgroundColor: const Color(0xFF0284C7),
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                    ),
                    icon: const Icon(Icons.add, color: Colors.white, size: 16),
                    label: const Text('Agregar Ítem', style: TextStyle(color: Colors.white, fontSize: 12, fontWeight: FontWeight.bold)),
                    onPressed: _openAddVariantDialog,
                  ),
                ],
              ),
              const SizedBox(height: 10),

              if (_detalles.isEmpty)
                Container(
                  padding: const EdgeInsets.all(24),
                  decoration: BoxDecoration(
                    color: const Color(0xFF1E293B),
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(color: const Color(0xFF334155), style: BorderStyle.solid),
                  ),
                  child: const Center(
                    child: Column(
                      children: [
                        Icon(Icons.inventory_2_outlined, color: Color(0xFF64748B), size: 40),
                        SizedBox(height: 8),
                        Text('Sin productos agregados aún.', style: TextStyle(color: Color(0xFF94A3B8), fontWeight: FontWeight.bold)),
                        Text('Toca "+ Agregar Ítem" para añadir variantes de iPhone.', style: TextStyle(color: Color(0xFF64748B), fontSize: 12)),
                      ],
                    ),
                  ),
                )
              else
                ListView.separated(
                  shrinkWrap: true,
                  physics: const NeverScrollableScrollPhysics(),
                  itemCount: _detalles.length,
                  separatorBuilder: (_, __) => const SizedBox(height: 8),
                  itemBuilder: (ctx, index) {
                    final d = _detalles[index];
                    return Container(
                      padding: const EdgeInsets.all(12),
                      decoration: BoxDecoration(
                        color: const Color(0xFF1E293B),
                        borderRadius: BorderRadius.circular(10),
                        border: Border.all(color: const Color(0xFF334155)),
                      ),
                      child: Row(
                        children: [
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(d.nombreProducto, style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 14)),
                                Text(d.sku, style: const TextStyle(color: Color(0xFF38BDF8), fontSize: 12)),
                                const SizedBox(height: 4),
                                Text(
                                  '${d.cantidad} un. × \$${d.costounitariousd.toStringAsFixed(2)} = \$${d.subtotal.toStringAsFixed(2)} USD',
                                  style: const TextStyle(color: Color(0xFF94A3B8), fontSize: 12),
                                ),
                              ],
                            ),
                          ),
                          IconButton(
                            icon: const Icon(Icons.delete_outline, color: Color(0xFFEF4444)),
                            onPressed: () {
                              setState(() => _detalles.removeAt(index));
                            },
                          ),
                        ],
                      ),
                    );
                  },
                ),
            ],
          ),
        ),
      ),
      bottomNavigationBar: Container(
        padding: const EdgeInsets.all(16),
        decoration: const BoxDecoration(
          color: Color(0xFF1E293B),
          border: Border(top: BorderSide(color: Color(0xFF334155))),
        ),
        child: Row(
          children: [
            Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text('Total Estimado:', style: TextStyle(color: Color(0xFF94A3B8), fontSize: 11)),
                Text(
                  '\$${_totalOrden.toStringAsFixed(2)} USD',
                  style: const TextStyle(color: Color(0xFF38BDF8), fontWeight: FontWeight.bold, fontSize: 18),
                ),
              ],
            ),
            const SizedBox(width: 16),
            Expanded(
              child: ElevatedButton.icon(
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFF0EA5E9),
                  padding: const EdgeInsets.symmetric(vertical: 14),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                ),
                icon: const Icon(Icons.save_outlined, color: Colors.white, size: 20),
                label: widget.controller.isLoading
                    ? const SizedBox(
                        height: 18,
                        width: 18,
                        child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2),
                      )
                    : const Text('Registrar Orden', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 15)),
                onPressed: widget.controller.isLoading ? null : _submitOrder,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
