import 'package:flutter/material.dart';
import '../models/orden_model.dart';
import '../services/orden_service.dart';
import '../models/cliente_model.dart';
import '../services/cliente_service.dart';

class OrdenScreen extends StatefulWidget {
  const OrdenScreen({Key? key}) : super(key: key);

  @override
  State<OrdenScreen> createState() => _OrdenScreenState();
}

class _OrdenScreenState extends State<OrdenScreen> {
  final OrdenService _service = OrdenService();
  List<Orden> _items = [];
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

  void _showFormDialog({Orden? item}) {
    showDialog(
      context: context,
      builder: (context) => OrdenFormDialog(
        item: item,
        onSave: (Orden newItem) async {
          try {
            if (item == null) {
              await _service.create(newItem);
            } else {
              await _service.update(item.ordenid!, newItem);
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

  void _showDetails(Orden item) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Detalles'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Ordenid: \${item.ordenid}'),
            Text('Ordenfecha: \${item.ordenfecha}'),
            Text('Cliente_clienteid: \${item.cliente?.toString() ?? "N/A"}'),
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
        title: const Text('Orden'),
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
                            title: Text('\${item.ordenfecha}'),
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
                                              _deleteItem(item.ordenid!);
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

class OrdenFormDialog extends StatefulWidget {
  final Orden? item;
  final Function(Orden) onSave;

  const OrdenFormDialog({Key? key, this.item, required this.onSave}) : super(key: key);

  @override
  State<OrdenFormDialog> createState() => _OrdenFormDialogState();
}

class _OrdenFormDialogState extends State<OrdenFormDialog> {
  final _formKey = GlobalKey<FormState>();
  late TextEditingController _ordenfechaController;
  List<Cliente> _clienteList = [];
  Cliente? _selectedCliente;

  @override
  void initState() {
    super.initState();
    _ordenfechaController = TextEditingController(text: widget.item?.ordenfecha?.toString() ?? '');
    _loadCliente();
  }

  Future<void> _loadCliente() async {
    try {
      final service = ClienteService();
      final items = await service.getAll();
      setState(() {
        _clienteList = items;
        if (widget.item?.cliente != null) {
          _selectedCliente = widget.item!.cliente;
        }
      });
    } catch (e) {
      print('Error loading cliente: \$e');
    }
  }

  @override
  void dispose() {
    _ordenfechaController.dispose();
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
                controller: _ordenfechaController,
                decoration: InputDecoration(labelText: 'Ordenfecha'),
                keyboardType: TextInputType.datetime,
                validator: (v) => v!.isEmpty ? 'Requerido' : null,
              ),
              const SizedBox(height: 12),
              DropdownButtonFormField<Cliente>(
                value: _selectedCliente,
                decoration: InputDecoration(labelText: 'Cliente_clienteid'),
                items: _clienteList.map((item) {
                  return DropdownMenuItem(
                    value: item,
                    child: Text('\${item.nombre}'),
                  );
                }).toList(),
                onChanged: (value) {
                  setState(() {
                    _selectedCliente = value;
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
              widget.onSave(Orden(
                ordenid: widget.item?.ordenid,
                ordenfecha: _ordenfechaController.text,
                cliente: _selectedCliente,
              ));
            }
          },
          child: const Text('Guardar'),
        ),
      ],
    );
  }
}
