import 'cliente_model.dart';


class Orden {
  final int? ordenid;
  final DateTime ordenfecha;
  final Cliente cliente;

  Orden({
    this.ordenid,
    required this.ordenfecha,
    required this.cliente,
  });

  factory Orden.fromJson(Map<String, dynamic> json) {
    return Orden(
      ordenid: json['ordenid'],
      ordenfecha: DateTime.parse(json['ordenfecha']),
      cliente: Cliente.fromJson(json['cliente']),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'ordenid': ordenid,
      'ordenfecha': ordenfecha.toIso8601String().split('T')[0],
      'cliente' : {
        'clienteid': cliente.clienteid,
      },
    };
  }
}
