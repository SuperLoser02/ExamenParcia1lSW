

class Categoria {
  final int? categoriaid;
  final String? descripcion;

  Categoria({
    this.categoriaid,
    this.descripcion,
  });

  factory Categoria.fromJson(Map<String, dynamic> json) {
    return Categoria(
      categoriaid: json['categoriaid'],
      descripcion: json['descripcion'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'categoriaid': categoriaid,
      'descripcion': descripcion,
    };
  }
}
