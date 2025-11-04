

class Catrgoria {
  final int? categoriaid;

  Catrgoria({
    this.categoriaid,
  });

  factory Catrgoria.fromJson(Map<String, dynamic> json) {
    return Catrgoria(
      categoriaid: json['categoriaid'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'categoriaid': categoriaid,
    };
  }
}
