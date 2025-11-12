import 'package:flutter/material.dart';
import '../models/orden_detalle_model.dart';
import '../services/orden_detalle_service.dart';
import '../models/orden_model.dart';
import '../services/orden_service.dart';
import '../models/producto_model.dart';
import '../services/producto_service.dart';

class Orden_detalleScreen extends StatefulWidget {
  const Orden_detalleScreen({super.key});

  @override
  State<Orden_detalleScreen> createState() => _Orden_detalleScreenState();
}

class _Orden_detalleScreenState extends State<Orden_detalleScreen> {
  final Orden_detalleService _service = Orden_detalleService();
  List<Orden_detalle> _items = [];
  bool _isLoading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _loadItems();
  }

  Future<void> _loadItems() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });

    try {
      final items = await _service.getAll();
      setState(() {
        _items = items;
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _error = e.toString();
        _isLoading = false;
      });
    }
  }

  Future<void> _deleteItem(int ordenid, int productoid) async {
    try {
      await _service.delete(ordenid, productoid);
      await _loadItems();
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Eliminado correctamente'), backgroundColor: Colors.green),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error: $e'), backgroundColor: Colors.red),
        );
      }
    }
  }

  void _showFormDialog({Orden_detalle? item}) {
    showDialog(
      context: context,
      builder: (context) => Orden_detalleFormDialog(
        item: item,
        onSave: (Orden_detalle newItem) async {
          final parentContext = context;
          try {
            if (item == null) {
              await _service.create(newItem);
            } else {
               if (newItem.ordenid != item.ordenid || newItem.productoid != item.productoid) {
                 await _service.create(newItem);
                 await _service.delete(item.ordenid!, item.productoid!);
               } else {
                 await _service.update(item.ordenid!, item.productoid!, newItem);
               }
            }
            await _loadItems();
            if (mounted) {
              Navigator.pop(parentContext);
              ScaffoldMessenger.of(parentContext).showSnackBar(
                SnackBar(content: Text(item == null ? 'Creado correctamente' : 'Actualizado'),
                backgroundColor: Colors.green
                ),
              );
            }
          } catch (e) {
            if (mounted) {
              ScaffoldMessenger.of(parentContext).showSnackBar(
                SnackBar(content: Text('Error: ${e.toString()}'), backgroundColor: Colors.red, duration: const Duration(seconds: 4)),
              );
            }
          }
        },
      ),
    );
  }

  void _showDetails(Orden_detalle item) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Detalles de Orden_detalle'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Ordenid: ${item.ordenid}', style: const TextStyle(fontWeight: FontWeight.bold)),
            const SizedBox(height: 8),
            Text('Productoid: ${item.productoid}', style: const TextStyle(fontWeight: FontWeight.bold)),
            const SizedBox(height: 8),
            Text('Cantidad: ${item.cantidad}'),
          ],
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(context), child: const Text('Cerrar')),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Orden_detalle'),
        actions: [
          IconButton(icon: const Icon(Icons.refresh), onPressed: _loadItems),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : _error != null
              ? Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      const Icon(Icons.error, color: Colors.red, size: 60),
                      const SizedBox(height: 16),
                      Text(_error!, textAlign: TextAlign.center),
                      const SizedBox(height: 16),
                      ElevatedButton(
                        onPressed: _loadItems,
                        child: const Text('Reintentar'),
                      ),
                    ],
                  ),
                )
              : _items.isEmpty
                  ? const Center(
                      child: Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Icon(Icons.inbox, size: 60, color: Colors.grey),
                          SizedBox(height: 16),
                          Text('No hay Orden_detalle', style: TextStyle(fontSize: 16)),
                        ],
                      ),
                    )
                  : ListView.builder(
                      itemCount: _items.length,
                      itemBuilder: (context, index) {
                        final item = _items[index];
                        return Card(
                          margin: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                          child: ListTile(
                            title: Text('Orden: ${item.ordenid} - Producto: ${item.productoid}'),
                                subtitle: Text('Orden: ${item.ordenid} - Producto: ${item.productoid}'),
                            trailing: Row(
                              mainAxisSize: MainAxisSize.min,
                              children: [
                                IconButton(
                                  icon: const Icon(Icons.visibility, color: Colors.blue),
                                  onPressed: () => _showDetails(item),
                                ),
                                IconButton(
                                  icon: const Icon(Icons.edit, color: Colors.orange),
                                  onPressed: () => _showFormDialog(item: item),
                                ),
                                IconButton(
                                  icon: const Icon(Icons.delete, color: Colors.red),
                                  onPressed: () {
                                    showDialog(
                                      context: context,
                                      builder: (ctx) => AlertDialog(
                                        title: const Text('Confirmar eliminación'),
                                        content: const Text('¿Está seguro de eliminar este elemento?'),
                                        actions: [
                                          TextButton(
                                            onPressed: () => Navigator.pop(ctx),
                                            child: const Text('Cancelar'),
                                          ),
                                          ElevatedButton(
                                            style: ElevatedButton.styleFrom(
                                              backgroundColor: Colors.red,
                                            ),
                                            onPressed: () {
                                              Navigator.pop(ctx);
                                              _deleteItem(item.ordenid!, item.productoid!);
                                            },
                                            child: const Text('Eliminar'),
                                          ),
                                        ],
                                      ),
                                    );
                                  },
                                ),
                              ],
                            ),
                          ),
                        );
                      },
                    ),
      floatingActionButton: FloatingActionButton(
        onPressed: () => _showFormDialog(),
        child: const Icon(Icons.add),
      ),
    );
  }
}

class Orden_detalleFormDialog extends StatefulWidget {
  final Orden_detalle? item;
  final Function(Orden_detalle) onSave;

  const Orden_detalleFormDialog({super.key, this.item, required this.onSave});

  @override
  State<Orden_detalleFormDialog> createState() => _Orden_detalleFormDialogState();
}

class _Orden_detalleFormDialogState extends State<Orden_detalleFormDialog> {
  final _formKey = GlobalKey<FormState>();
  final OrdenService _ordenService = OrdenService();
  final ProductoService _productoService = ProductoService();
  List<Orden> _ordenList = [];
  Orden? _selectedOrden;
  List<Producto> _productoList = [];
  Producto? _selectedProducto;
  late TextEditingController _cantidadController;
  bool _isLoadingData = true;

  @override
  void initState() {
    super.initState();
    _cantidadController = TextEditingController(
      text: widget.item != null ? widget.item!.cantidad.toString() : ''
    );
    _loadData();
  }

  Future<void> _loadData() async {
    await Future.wait([
    _loadOrden(),
    _loadProducto(),
    ]);
  }

  Future<void> _loadOrden() async {
    try {
      final service = OrdenService();
      final items = await service.getAll();
      if (mounted) {
        setState(() {
          _ordenList = items;
          if (widget.item?.ordenid != null) {
            // Buscar el objeto completo basado en el ID
            _selectedOrden = items.firstWhere(
              (cat) => cat.ordenid == widget.item!.ordenid,
              orElse: () => items.first,
            );
          }
          _isLoadingData = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _isLoadingData = false;
        });
      }
    }
  }

  Future<void> _loadProducto() async {
    try {
      final service = ProductoService();
      final items = await service.getAll();
      if (mounted) {
        setState(() {
          _productoList = items;
          if (widget.item?.productoid != null) {
            // Buscar el objeto completo basado en el ID
            _selectedProducto = items.firstWhere(
              (cat) => cat.productoid == widget.item!.productoid,
              orElse: () => items.first,
            );
          }
          _isLoadingData = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _isLoadingData = false;
        });
      }
    }
  }

  @override
  void dispose() {
    _cantidadController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: Text(widget.item == null ? 'Crear' : 'Editar'),
      content: Form(
        key: _formKey,
        child: SingleChildScrollView(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              DropdownButtonFormField<Orden>(
                value: _selectedOrden,
                decoration: const InputDecoration(labelText: 'Orden_ordenid'),
                items: _ordenList.map((item) {
                  return DropdownMenuItem(
                    value: item,
                    child: Text('ID: ${item.ordenid}'),
                  );
                }).toList(),
                onChanged: (value) {
                  setState(() {
                    _selectedOrden = value;
                  });
                },
                validator: (v) => v == null ? 'Requerido' : null,
              ),
              const SizedBox(height: 12),
              DropdownButtonFormField<Producto>(
                value: _selectedProducto,
                decoration: const InputDecoration(labelText: 'Producto_productoid'),
                items: _productoList.map((item) {
                  return DropdownMenuItem(
                    value: item,
                    child: Text('${item.nombreproducto}'),
                  );
                }).toList(),
                onChanged: (value) {
                  setState(() {
                    _selectedProducto = value;
                  });
                },
                validator: (v) => v == null ? 'Requerido' : null,
              ),
              const SizedBox(height: 12),
              TextFormField(
                controller: _cantidadController,
                decoration: const InputDecoration(labelText: 'Cantidad'),
                keyboardType: TextInputType.number,
                validator: (v) => v!.isEmpty ? 'Requerido' : null,
              ),
              const SizedBox(height: 12),
            ],
          ),
        ),
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.pop(context),
          child: const Text('Cancelar'),
        ),
        ElevatedButton(
          onPressed: () {
            if (_formKey.currentState!.validate()) {
              widget.onSave(Orden_detalle(
                ordenid: _selectedOrden?.ordenid,
                productoid: _selectedProducto?.productoid,
                cantidad: int.parse(_cantidadController.text),
              ));
            }
          },
          child: const Text('Guardar'),
        ),
      ],
    );
  }
}
