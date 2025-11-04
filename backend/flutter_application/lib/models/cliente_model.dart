

class Cliente {
  final int? clienteid;
  final String nombre;
  final String apellido;
  final String email;
  final String? email2;

  Cliente({
    this.clienteid,
    required this.nombre,
    required this.apellido,
    required this.email,
    this.email2,
  });

  factory Cliente.fromJson(Map<String, dynamic> json) {
    return Cliente(
      clienteid: json['clienteid'],
      nombre: json['nombre'],
      apellido: json['apellido'],
      email: json['email'],
      email2: json['email2'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'clienteid': clienteid,
      'nombre': nombre,
      'apellido': apellido,
      'email': email,
      'email2': email2,
    };
  }
}
