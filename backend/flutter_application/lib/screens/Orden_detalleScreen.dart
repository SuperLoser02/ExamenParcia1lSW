import 'package:flutter/material.dart';
import '../models/orden_detalle_model.dart';
import '../services/orden_detalle_service.dart';

class Orden_detalleScreen extends StatefulWidget {
  const Orden_detalleScreen({Key? key}) : super(key: key);

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
      _loadItems();
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Eliminado correctamente'), backgroundColor: Colors.green),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error: \$e'), backgroundColor: Colors.red),
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
          try {
            if (item == null) {
              await _service.create(newItem);
            } else {
              await _service.update(item.ordenid!, item.productoid!, newItem);
            }
            _loadItems();
            if (mounted) {
              Navigator.pop(context);
              ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(content: Text(item == null ? 'Creado' : 'Actualizado')),
              );
            }
          } catch (e) {
            if (mounted) {
              ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(content: Text('Error: \$e'), backgroundColor: Colors.red),
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
        title: const Text('Detalles'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Ordenid: \${item.ordenid}'),
            Text('Productoid: \${item.productoid}'),
            Text('Cantidad: \${item.cantidad}'),
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
              ? Center(child: Text(_error!))
              : _items.isEmpty
                  ? const Center(child: Text('No hay datos'))
                  : ListView.builder(
                      itemCount: _items.length,
                      itemBuilder: (context, index) {
                        final item = _items[index];
                        return Card(
                          child: ListTile(
                            title: Text('\${item.cantidad}'),
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
                                        title: const Text('Confirmar'),
                                        content: const Text('¿Eliminar?'),
                                        actions: [
                                          TextButton(
                                            onPressed: () => Navigator.pop(ctx),
                                            child: const Text('Cancelar'),
                                          ),
                                          TextButton(
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

  const Orden_detalleFormDialog({Key? key, this.item, required this.onSave}) : super(key: key);

  @override
  State<Orden_detalleFormDialog> createState() => _Orden_detalleFormDialogState();
}

class _Orden_detalleFormDialogState extends State<Orden_detalleFormDialog> {
  final _formKey = GlobalKey<FormState>();
  late TextEditingController _cantidadController;

  @override
  void initState() {
    super.initState();
    _cantidadController = TextEditingController(text: widget.item?.cantidad?.toString() ?? '');
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
              TextFormField(
                controller: _cantidadController,
                decoration: InputDecoration(labelText: 'Cantidad'),
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
                ordenid: widget.item?.ordenid,
                productoid: widget.item?.productoid,
                cantidad: int.tryParse(_cantidadController.text),
              ));
            }
          },
          child: const Text('Guardar'),
        ),
      ],
    );
  }
}
