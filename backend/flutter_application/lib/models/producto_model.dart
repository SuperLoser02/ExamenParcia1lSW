import 'categoria_model.dart';


class Producto {
  final int? productoid;
  final String nombreproducto;
  final Categoria categoria;

  Producto({
    this.productoid,
    required this.nombreproducto,
    required this.categoria,
  });

  factory Producto.fromJson(Map<String, dynamic> json) {
    return Producto(
      productoid: json['productoid'],
      nombreproducto: json['nombreproducto'],
      categoria: Categoria.fromJson(json['categoria']),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'productoid': productoid,
      'nombreproducto': nombreproducto,
      'categoria' : {
        'categoriaid': categoria.categoriaid,
      },
    };
  }
}
