import 'package:flutter/material.dart';
import '../models/cliente_model.dart';
import '../services/cliente_service.dart';

class ClienteScreen extends StatefulWidget {
  const ClienteScreen({super.key});

  @override
  State<ClienteScreen> createState() => _ClienteScreenState();
}

class _ClienteScreenState extends State<ClienteScreen> {
  final ClienteService _service = ClienteService();
  List<Cliente> _items = [];
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

  void _showFormDialog({Cliente? item}) {
    showDialog(
      context: context,
      builder: (context) => ClienteFormDialog(
        item: item,
        onSave: (Cliente newItem) async {
          final parentContext = context;
          try {
            if (item == null) {
              await _service.create(newItem);
            } else {
              await _service.update(item.clienteid!, newItem);
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

  void _showDetails(Cliente item) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Detalles de Cliente'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Clienteid: ${item.clienteid}', style: const TextStyle(fontWeight: FontWeight.bold)),
            const SizedBox(height: 8),
            Text('Nombre: ${item.nombre}'),
            Text('Apellido: ${item.apellido}'),
            Text('Email: ${item.email}'),
            Text('Email2: ${item.email2}'),
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
        title: const Text('Cliente'),
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
                          Text('No hay Cliente', style: TextStyle(fontSize: 16)),
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
                            title: Text('ID: ${item.clienteid}'),
                                subtitle: Text('nombre'),
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
                                              _deleteItem(item.clienteid!);
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

class ClienteFormDialog extends StatefulWidget {
  final Cliente? item;
  final Function(Cliente) onSave;

  const ClienteFormDialog({super.key, this.item, required this.onSave});

  @override
  State<ClienteFormDialog> createState() => _ClienteFormDialogState();
}

class _ClienteFormDialogState extends State<ClienteFormDialog> {
  final _formKey = GlobalKey<FormState>();
  late TextEditingController _nombreController;
  late TextEditingController _apellidoController;
  late TextEditingController _emailController;
  late TextEditingController _email2Controller;
  bool _isLoadingData = true;

  @override
  void initState() {
    super.initState();
    _nombreController = TextEditingController(
      text: widget.item != null ? widget.item!.nombre.toString() : ''
    );
    _apellidoController = TextEditingController(
      text: widget.item != null ? widget.item!.apellido.toString() : ''
    );
    _emailController = TextEditingController(
      text: widget.item != null ? widget.item!.email.toString() : ''
    );
    _email2Controller = TextEditingController(
      text: widget.item?.email2 != null ? widget.item!.email2.toString() : ''
    );
    _loadData();
  }

  Future<void> _loadData() async {
    await Future.wait([
    ]);
  }

  @override
  void dispose() {
    _nombreController.dispose();
    _apellidoController.dispose();
    _emailController.dispose();
    _email2Controller.dispose();
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
                controller: _nombreController,
                decoration: const InputDecoration(labelText: 'Nombre'),
                validator: (v) => v!.isEmpty ? 'Requerido' : null,
              ),
              const SizedBox(height: 12),
              TextFormField(
                controller: _apellidoController,
                decoration: const InputDecoration(labelText: 'Apellido'),
                validator: (v) => v!.isEmpty ? 'Requerido' : null,
              ),
              const SizedBox(height: 12),
              TextFormField(
                controller: _emailController,
                decoration: const InputDecoration(labelText: 'Email'),
                validator: (v) => v!.isEmpty ? 'Requerido' : null,
              ),
              const SizedBox(height: 12),
              TextFormField(
                controller: _email2Controller,
                decoration: const InputDecoration(labelText: 'Email2'),
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
              widget.onSave(Cliente(
                clienteid: widget.item?.clienteid,
                nombre: _nombreController.text,
                apellido: _apellidoController.text,
                email: _emailController.text,
                email2: _email2Controller.text.isEmpty ? null : _email2Controller.text,
              ));
            }
          },
          child: const Text('Guardar'),
        ),
      ],
    );
  }
}
