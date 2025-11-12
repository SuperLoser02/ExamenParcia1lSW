import 'package:flutter/material.dart';
import '../models/producto_model.dart';
import '../services/producto_service.dart';
import '../models/categoria_model.dart';
import '../services/categoria_service.dart';

class ProductoScreen extends StatefulWidget {
  const ProductoScreen({super.key});

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

  void _showFormDialog({Producto? item}) {
    showDialog(
      context: context,
      builder: (context) => ProductoFormDialog(
        item: item,
        onSave: (Producto newItem) async {
          final parentContext = context;
          try {
            if (item == null) {
              await _service.create(newItem);
            } else {
              await _service.update(item.productoid!, newItem);
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

  void _showDetails(Producto item) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Detalles de Producto'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Productoid: ${item.productoid}', style: const TextStyle(fontWeight: FontWeight.bold)),
            const SizedBox(height: 8),
            Text('Nombreproducto: ${item.nombreproducto}'),
            Text('Categoria_categoriaid: ${item.categoria?.toString() ?? "N/A"}'),
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
                          Text('No hay Producto', style: TextStyle(fontSize: 16)),
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
                            title: Text('ID: ${item.productoid}'),
                                subtitle: Text('nombreproducto'),
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

  const ProductoFormDialog({super.key, this.item, required this.onSave});

  @override
  State<ProductoFormDialog> createState() => _ProductoFormDialogState();
}

class _ProductoFormDialogState extends State<ProductoFormDialog> {
  final _formKey = GlobalKey<FormState>();
  late TextEditingController _nombreproductoController;
  List<Categoria> _categoriaList = [];
  Categoria? _selectedCategoria;
  bool _isLoadingData = true;

  @override
  void initState() {
    super.initState();
    _nombreproductoController = TextEditingController(
      text: widget.item != null ? widget.item!.nombreproducto.toString() : ''
    );
    _loadData();
  }

  Future<void> _loadData() async {
    await Future.wait([
    _loadCategoria(),
    ]);
  }

  Future<void> _loadCategoria() async {
    try {
      final service = CategoriaService();
      final items = await service.getAll();
      if (mounted) {
        setState(() {
          _categoriaList = items;
          if (widget.item?.categoria != null) {
             // Buscar el objeto completo basado en el ID
            _selectedCategoria = _categoriaList.firstWhere(
              (cat) => cat.categoriaid == widget.item!.categoria.categoriaid,
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
    _nombreproductoController.dispose();
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
                controller: _nombreproductoController,
                decoration: const InputDecoration(labelText: 'Nombreproducto'),
                validator: (v) => v!.isEmpty ? 'Requerido' : null,
              ),
              const SizedBox(height: 12),
              DropdownButtonFormField<Categoria>(
                value: _selectedCategoria,
                decoration: const InputDecoration(labelText: 'Categoria_categoriaid'),
                items: _categoriaList.map((item) {
                  return DropdownMenuItem(
                    value: item,
                    child: Text('${item.descripcion}'),
                  );
                }).toList(),
                onChanged: (value) {
                  setState(() {
                    _selectedCategoria = value;
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
                nombreproducto: _nombreproductoController.text,
                categoria: _selectedCategoria!,
              ));
            }
          },
          child: const Text('Guardar'),
        ),
      ],
    );
  }
}
