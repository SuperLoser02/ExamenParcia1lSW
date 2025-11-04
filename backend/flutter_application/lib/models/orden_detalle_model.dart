import 'orden_model.dart';
import 'producto_model.dart';


class Orden_detalle {
  final int? ordenid;
  final int? productoid;
  final int cantidad;

  Orden_detalle({
    this.ordenid,
    this.productoid,
    required this.cantidad,
  });

  factory Orden_detalle.fromJson(Map<String, dynamic> json) {
    return Orden_detalle(
      ordenid: json['id']?['ordenid'],
      productoid: json['id']?['productoid'],
      cantidad: json['cantidad'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': {
        'ordenid': ordenid,
        'productoid': productoid,
      },
      'cantidad': cantidad,
    };
  }
}
