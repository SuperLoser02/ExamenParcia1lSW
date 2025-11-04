import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/orden_detalle_model.dart';

class Orden_detalleService {
  static const String baseUrl = 'http://10.0.2.2:8080/api/orden_detalles';

  Future<List<Orden_detalle>> getAll() async {
    try {
      final response = await http.get(
        Uri.parse(baseUrl),
        headers: {'Content-Type': 'application/json'},
      );

      if (response.statusCode == 200) {
        List<dynamic> jsonList = json.decode(response.body);
        return jsonList.map((json) => Orden_detalle.fromJson(json)).toList();
      } else {
        throw Exception('Error al cargar datos: \${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Error de conexión: \$e');
    }
  }

  Future<Orden_detalle> getById(int ordenid, int productoid) async {
    try {
      final response = await http.get(
        Uri.parse('\$baseUrl/\${ordenid}/\${productoid}'),
        headers: {'Content-Type': 'application/json'},
      );

      if (response.statusCode == 200) {
        return Orden_detalle.fromJson(json.decode(response.body));
      } else {
        throw Exception('Error: \${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Error de conexión: \$e');
    }
  }

  Future<Orden_detalle> create(Orden_detalle orden_detalle) async {
    try {
      final response = await http.post(
        Uri.parse(baseUrl),
        headers: {'Content-Type': 'application/json'},
        body: json.encode(orden_detalle.toJson()),
      );

      if (response.statusCode == 200 || response.statusCode == 201) {
        return Orden_detalle.fromJson(json.decode(response.body));
      } else {
        throw Exception('Error al crear: \${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Error de conexión: \$e');
    }
  }

  Future<Orden_detalle> update(int ordenid, int productoid, Orden_detalle orden_detalle) async {
    try {
      final response = await http.put(
        Uri.parse('\$baseUrl/\${ordenid}/\${productoid}'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode(orden_detalle.toJson()),
      );

      if (response.statusCode == 200) {
        return Orden_detalle.fromJson(json.decode(response.body));
      } else {
        throw Exception('Error al actualizar: \${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Error de conexión: \$e');
    }
  }

  Future<void> delete(int ordenid, int productoid) async {
    try {
      final response = await http.delete(
        Uri.parse('\$baseUrl/\${ordenid}/\${productoid}'),
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
