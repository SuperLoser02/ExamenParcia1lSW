import 'package:flutter/material.dart';
import '../models/catrgoria_model.dart';
import '../services/catrgoria_service.dart';

class CatrgoriaScreen extends StatefulWidget {
  const CatrgoriaScreen({Key? key}) : super(key: key);

  @override
  State<CatrgoriaScreen> createState() => _CatrgoriaScreenState();
}

class _CatrgoriaScreenState extends State<CatrgoriaScreen> {
  final CatrgoriaService _service = CatrgoriaService();
  List<Catrgoria> _items = [];
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

  void _showFormDialog({Catrgoria? item}) {
    showDialog(
      context: context,
      builder: (context) => CatrgoriaFormDialog(
        item: item,
        onSave: (Catrgoria newItem) async {
          try {
            if (item == null) {
              await _service.create(newItem);
            } else {
              await _service.update(item.categoriaid!, newItem);
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

  void _showDetails(Catrgoria item) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Detalles'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Categoriaid: \${item.categoriaid}'),
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
        title: const Text('Catrgoria'),
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
                            title: Text('ID: \${item.categoriaid}'),
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
                                              _deleteItem(item.categoriaid!);
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

class CatrgoriaFormDialog extends StatefulWidget {
  final Catrgoria? item;
  final Function(Catrgoria) onSave;

  const CatrgoriaFormDialog({Key? key, this.item, required this.onSave}) : super(key: key);

  @override
  State<CatrgoriaFormDialog> createState() => _CatrgoriaFormDialogState();
}

class _CatrgoriaFormDialogState extends State<CatrgoriaFormDialog> {
  final _formKey = GlobalKey<FormState>();

  @override
  void initState() {
    super.initState();
  }

  @override
  void dispose() {
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
              widget.onSave(Catrgoria(
                categoriaid: widget.item?.categoriaid,
              ));
            }
          },
          child: const Text('Guardar'),
        ),
      ],
    );
  }
}
