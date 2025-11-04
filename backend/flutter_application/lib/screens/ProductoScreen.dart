import 'package:flutter/material.dart';
import '../models/producto_model.dart';
import '../services/producto_service.dart';
import '../models/catrgoria_model.dart';
import '../services/catrgoria_service.dart';

class ProductoScreen extends StatefulWidget {
  const ProductoScreen({Key? key}) : super(key: key);

  @override
  State<ProductoScreen> createState() => _ProductoScreenState();
}

class _ProductoScreenState extends State<ProductoScreen> {
  final ProductoService _service = ProductoService();
  List<Producto> _items = [];
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

  Future<void> _deleteItem(int id) async {
    try {
      await _service.delete(id);
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

  void _showFormDialog({Producto? item}) {
    showDialog(
      context: context,
      builder: (context) => ProductoFormDialog(
        item: item,
        onSave: (Producto newItem) async {
          try {
            if (item == null) {
              await _service.create(newItem);
            } else {
              await _service.update(item.productoid!, newItem);
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

  void _showDetails(Producto item) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Detalles'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Productoid: \${item.productoid}'),
            Text('Productonombre: \${item.productonombre}'),
            Text('Precio: \${item.precio}'),
            Text('Catrgoria_categoriaid: \${item.catrgoria?.toString() ?? "N/A"}'),
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
        title: const Text('Producto'),
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
                            title: Text('\${item.productonombre}'),
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
                                              _deleteItem(item.productoid!);
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

class ProductoFormDialog extends StatefulWidget {
  final Producto? item;
  final Function(Producto) onSave;

  const ProductoFormDialog({Key? key, this.item, required this.onSave}) : super(key: key);

  @override
  State<ProductoFormDialog> createState() => _ProductoFormDialogState();
}

class _ProductoFormDialogState extends State<ProductoFormDialog> {
  final _formKey = GlobalKey<FormState>();
  late TextEditingController _productonombreController;
  late TextEditingController _precioController;
  List<Catrgoria> _catrgoriaList = [];
  Catrgoria? _selectedCatrgoria;

  @override
  void initState() {
    super.initState();
    _productonombreController = TextEditingController(text: widget.item?.productonombre?.toString() ?? '');
    _precioController = TextEditingController(text: widget.item?.precio?.toString() ?? '');
    _loadCatrgoria();
  }

  Future<void> _loadCatrgoria() async {
    try {
      final service = CatrgoriaService();
      final items = await service.getAll();
      setState(() {
        _catrgoriaList = items;
        if (widget.item?.catrgoria != null) {
          _selectedCatrgoria = widget.item!.catrgoria;
        }
      });
    } catch (e) {
      print('Error loading catrgoria: \$e');
    }
  }

  @override
  void dispose() {
    _productonombreController.dispose();
    _precioController.dispose();
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
                controller: _productonombreController,
                decoration: InputDecoration(labelText: 'Productonombre'),
                validator: (v) => v!.isEmpty ? 'Requerido' : null,
              ),
              const SizedBox(height: 12),
              TextFormField(
                controller: _precioController,
                decoration: InputDecoration(labelText: 'Precio'),
                keyboardType: TextInputType.number,
                validator: (v) => v!.isEmpty ? 'Requerido' : null,
              ),
              const SizedBox(height: 12),
              DropdownButtonFormField<Catrgoria>(
                value: _selectedCatrgoria,
                decoration: InputDecoration(labelText: 'Catrgoria_categoriaid'),
                items: _catrgoriaList.map((item) {
                  return DropdownMenuItem(
                    value: item,
                    child: Text('ID: \${item.categoriaid}'),
                  );
                }).toList(),
                onChanged: (value) {
                  setState(() {
                    _selectedCatrgoria = value;
                  });
                },
                validator: (v) => v == null ? 'Requerido' : null,
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
              widget.onSave(Producto(
                productoid: widget.item?.productoid,
                productonombre: _productonombreController.text,
                precio: double.tryParse(_precioController.text),
                catrgoria: _selectedCatrgoria,
              ));
            }
          },
          child: const Text('Guardar'),
        ),
      ],
    );
  }
}
