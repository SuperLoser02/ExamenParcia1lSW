import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/cliente_model.dart';

class ClienteService {
  static const String baseUrl = 'http://10.0.2.2:8080/api/clientes';

  Future<List<Cliente>> getAll() async {
    try {
      final response = await http.get(
        Uri.parse(baseUrl),
        headers: {'Content-Type': 'application/json'},
      );

      if (response.statusCode == 200) {
        List<dynamic> jsonList = json.decode(response.body);
        return jsonList.map((json) => Cliente.fromJson(json)).toList();
      } else {
        throw Exception('Error al cargar datos: \${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Error de conexión: \$e');
    }
  }

  Future<Cliente> getById(int id) async {
    try {
      final response = await http.get(
        Uri.parse('\$baseUrl/\$id'),
        headers: {'Content-Type': 'application/json'},
      );

      if (response.statusCode == 200) {
        return Cliente.fromJson(json.decode(response.body));
      } else {
        throw Exception('Error: \${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Error de conexión: \$e');
    }
  }

  Future<Cliente> create(Cliente cliente) async {
    try {
      final response = await http.post(
        Uri.parse(baseUrl),
        headers: {'Content-Type': 'application/json'},
        body: json.encode(cliente.toJson()),
      );

      if (response.statusCode == 200 || response.statusCode == 201) {
        return Cliente.fromJson(json.decode(response.body));
      } else {
        throw Exception('Error al crear: \${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Error de conexión: \$e');
    }
  }

  Future<Cliente> update(int id, Cliente cliente) async {
    try {
      final response = await http.put(
        Uri.parse('\$baseUrl/\$id'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode(cliente.toJson()),
      );

      if (response.statusCode == 200) {
        return Cliente.fromJson(json.decode(response.body));
      } else {
        throw Exception('Error al actualizar: \${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Error de conexión: \$e');
    }
  }

  Future<void> delete(int id) async {
    try {
      final response = await http.delete(
        Uri.parse('\$baseUrl/\$id'),
        headers: {'Content-Type': 'application/json'},
      );

      if (response.statusCode != 204 && response.statusCode != 200) {
        throw Exception('Error al eliminar: \${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Error de conexión: \$e');
    }
  }
}
