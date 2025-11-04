import 'catrgoria_model.dart';


class Producto {
  final int? productoid;
  final String productonombre;
  final double precio;
  final Catrgoria catrgoria;

  Producto({
    this.productoid,
    required this.productonombre,
    required this.precio,
    required this.catrgoria,
  });

  factory Producto.fromJson(Map<String, dynamic> json) {
    return Producto(
      productoid: json['productoid'],
      productonombre: json['productonombre'],
      precio: (json['precio'] ?? 0).toDouble(),
      catrgoria: Catrgoria.fromJson(json['catrgoria']),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'productoid': productoid,
      'productonombre': productonombre,
      'precio': precio,
      'catrgoria_categoriaid': catrgoria.categoriaid,
    };
  }
}
