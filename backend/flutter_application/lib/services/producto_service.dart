import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/producto_model.dart';

class ProductoService {
  static const String baseUrl = 'http://10.0.2.2:8080/api/productos';

  Future<List<Producto>> getAll() async {
    try {
      final response = await http.get(
        Uri.parse(baseUrl),
        headers: {'Content-Type': 'application/json'},
      );

      if (response.statusCode == 200) {
        List<dynamic> jsonList = json.decode(response.body);
        return jsonList.map((json) => Producto.fromJson(json)).toList();
      } else {
        throw Exception('Error al cargar datos: \${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Error de conexión: \$e');
    }
  }

  Future<Producto> getById(int id) async {
    try {
      final response = await http.get(
        Uri.parse('\$baseUrl/\$id'),
        headers: {'Content-Type': 'application/json'},
      );

      if (response.statusCode == 200) {
        return Producto.fromJson(json.decode(response.body));
      } else {
        throw Exception('Error: \${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Error de conexión: \$e');
    }
  }

  Future<Producto> create(Producto producto) async {
    try {
      final response = await http.post(
        Uri.parse(baseUrl),
        headers: {'Content-Type': 'application/json'},
        body: json.encode(producto.toJson()),
      );

      if (response.statusCode == 200 || response.statusCode == 201) {
        return Producto.fromJson(json.decode(response.body));
      } else {
        throw Exception('Error al crear: \${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Error de conexión: \$e');
    }
  }

  Future<Producto> update(int id, Producto producto) async {
    try {
      final response = await http.put(
        Uri.parse('\$baseUrl/\$id'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode(producto.toJson()),
      );

      if (response.statusCode == 200) {
        return Producto.fromJson(json.decode(response.body));
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
