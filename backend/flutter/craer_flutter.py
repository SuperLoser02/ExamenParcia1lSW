import os
import glob
import shutil
import zipfile
import tempfile
import base64
from primer_parcial.settings import BASE_DIR
from script.generar_script import generar_estructura

# Mapeo de tipos SQL/Java a Dart
tipo_a_dart = {
    "integer": "int",
    "smallint": "int",
    "bigint": "int",
    "float": "double",
    "decimal": "double",
    "char": "String",
    "text": "String",
    "boolean": "bool",
    "date": "DateTime",
    "datetime": "DateTime",
    "time": "String",
    "json": "String"
}

def flutter(diagrama_id):
    """
    Genera el frontend Flutter completo basado en la estructura del diagrama.
    """
    # Rutas base
    base_flutter = os.path.join(BASE_DIR, 'flutter_application/lib')
    base_models = os.path.join(base_flutter, 'models')
    base_services = os.path.join(base_flutter, 'services')
    base_screens = os.path.join(base_flutter, 'screens')

    # Limpiar archivos anteriores
    for carpeta in [base_models, base_services, base_screens]:
        if os.path.exists(carpeta):
            for archivo in glob.glob(os.path.join(carpeta, "*.dart")):
                os.remove(archivo)
    
    # Obtener estructura
    estructura = generar_estructura(diagrama_id)
    
    # Asegurar que las carpetas existen
    os.makedirs(base_models, exist_ok=True)
    os.makedirs(base_services, exist_ok=True)
    os.makedirs(base_screens, exist_ok=True)
    
    # Generar archivos por cada tabla
    for _, tabla in estructura['tablas'].items():
        
        # ==================== MODELO ====================
        generar_modelo_dart(tabla, base_models)
        
        # ==================== SERVICE ====================
        generar_service_dart(tabla, base_services)
        
        # ==================== SCREEN ====================
        generar_screen_dart(tabla, base_screens, estructura['tablas'])
    
    # ==================== MAIN.DART ====================
    generar_main_dart(estructura, base_flutter)
    
    # ==================== CREAR ZIP ====================
    return crear_zip_flutter(estructura)


def generar_modelo_dart(tabla, base_models):
    """Genera el archivo modelo Dart para una tabla."""
    nombre_clase = tabla['nombre'].capitalize()
    nombre_archivo = f"{nombre_clase.lower()}_model.dart"
    archivo = os.path.join(base_models, nombre_archivo)
    
    tiene_pk_compuesta = len(tabla['pk']) > 1
    
    with open(archivo, "w", encoding="utf-8") as f:
        for fk in tabla["fk"]:
            import_clase = fk["tabla_padre"]
            f.write(f"import '{import_clase}_model.dart';\n")
        f.write("\n\n")        
        f.write(f"class {nombre_clase} {{\n")
        
        # ===== ATRIBUTOS =====
        # PKs
        if tiene_pk_compuesta:
            for pk in tabla['pk']:
                tipo_dart = tipo_a_dart.get(pk['tipo_dato'], 'String')
                f.write(f"  final {tipo_dart}? {pk['atributo_padre'].lower()};\n")
        else:
            if tabla['pk']:
                pk = tabla['pk'][0]
                tipo_dart = tipo_a_dart.get(pk['tipo_dato'], 'int')
                f.write(f"  final {tipo_dart}? {pk['nombre'].lower()};\n")
        
        # Atributos normales
        for atributo in tabla['atributos']:
            es_fk = atributo.get('tabla_padre') is not None
            
            if es_fk:
                # FK - objeto completo
                tabla_padre_nombre = atributo['tabla_padre'].capitalize()
                nullable = "?" if atributo.get('is_nullable', False) else ""
                f.write(f"  final {tabla_padre_nombre}{nullable} {atributo['tabla_padre'].lower()};\n")
            else:
                # Atributo normal
                tipo_dart = tipo_a_dart.get(atributo['tipo_dato'], 'String')
                nullable = "?" if atributo.get('is_nullable', False) else ""
                f.write(f"  final {tipo_dart}{nullable} {atributo['nombre'].lower()};\n")
        
        f.write("\n")
        
        # ===== CONSTRUCTOR =====
        f.write(f"  {nombre_clase}({{\n")
        
        if tiene_pk_compuesta:
            for pk in tabla['pk']:
                f.write(f"    this.{pk['atributo_padre'].lower()},\n")
        else:
            if tabla['pk']:
                pk = tabla['pk'][0]
                f.write(f"    this.{pk['nombre'].lower()},\n")
        
        for atributo in tabla['atributos']:
            es_fk = atributo.get('tabla_padre') is not None
            if es_fk:
                required = "required " if not atributo.get('is_nullable', False) else ""
                f.write(f"    {required}this.{atributo['tabla_padre'].lower()},\n")
            else:
                required = "required " if not atributo.get('is_nullable', False) else ""
                f.write(f"    {required}this.{atributo['nombre'].lower()},\n")
        
        f.write("  });\n\n")
        
        # ===== FROM JSON =====
        f.write(f"  factory {nombre_clase}.fromJson(Map<String, dynamic> json) {{\n")
        f.write(f"    return {nombre_clase}(\n")
        
        if tiene_pk_compuesta:
            for pk in tabla['pk']:
                f.write(f"      {pk['atributo_padre'].lower()}: json['id']?['{pk['atributo_padre'].lower()}'],\n")
        else:
            if tabla['pk']:
                pk = tabla['pk'][0]
                f.write(f"      {pk['nombre'].lower()}: json['{pk['nombre'].lower()}'],\n")
        
        for atributo in tabla['atributos']:
            es_fk = atributo.get('tabla_padre') is not None
            if es_fk:
                tabla_padre_nombre = atributo['tabla_padre'].capitalize()
                if atributo.get('is_nullable', False):
                    f.write(f"      {atributo['tabla_padre'].lower()}: json['{atributo['tabla_padre'].lower()}'] != null\n")
                    f.write(f"          ? {tabla_padre_nombre}.fromJson(json['{atributo['tabla_padre'].lower()}'])\n")
                    f.write(f"          : null,\n")
                else:
                    f.write(f"      {atributo['tabla_padre'].lower()}: {tabla_padre_nombre}.fromJson(json['{atributo['tabla_padre'].lower()}']),\n")
            else:
                nombre_campo = atributo['nombre'].lower()
                if atributo.get('is_nullable', False):
                    if atributo['tipo_dato'] in ['date', 'datetime']:
                        f.write(f"      {nombre_campo}: json['{nombre_campo}'] != null\n")
                        f.write(f"          ? DateTime.parse(json['{nombre_campo}'])\n")
                        f.write(f"          : null,\n")
                    elif atributo['tipo_dato'] in ['decimal', 'float']:
                        f.write(f"      {nombre_campo}: json['{nombre_campo}'] != null\n")
                        f.write(f"          ? (json['{nombre_campo}']).toDouble()\n")
                        f.write(f"          : null,\n")
                    else:
                        f.write(f"      {nombre_campo}: json['{nombre_campo}'],\n")
                else:
                    if atributo['tipo_dato'] in ['date', 'datetime']:
                        f.write(f"      {nombre_campo}: DateTime.parse(json['{nombre_campo}']),\n")
                    elif atributo['tipo_dato'] in ['decimal', 'float']:
                        f.write(f"      {nombre_campo}: (json['{nombre_campo}'] ?? 0).toDouble(),\n")
                    else:
                        f.write(f"      {atributo['nombre'].lower()}: json['{atributo['nombre'].lower()}'],\n")
                    
        f.write("    );\n")
        f.write("  }\n\n")
        
        # ===== TO JSON =====
        f.write("  Map<String, dynamic> toJson() {\n")
        f.write("    return {\n")
        
        if tiene_pk_compuesta:
            f.write("      'id': {\n")
            for pk in tabla['pk']:
                f.write(f"        '{pk['atributo_padre'].lower()}': {pk['atributo_padre'].lower()},\n")
            f.write("      },\n")
            for pk in tabla['pk']:
                if pk.get('tabla_padre'):
                    atributo = pk['atributo_padre']
                    if pk['is_nullable']:
                        f.write(f"      '{pk.get('tabla_padre')}: {{\n")
                        f.write(f"        '{atributo}': {atributo} != null {atributo} : null,\n")
                        f.write("      },\n")
                        #f.write(f"      '{atributo}': {atributo} != null ? {atributo} : null,\n")
                    else:
                        f.write(f"      '{pk.get('tabla_padre')}': {{\n")
                        f.write(f"        '{atributo}': {atributo},\n")
                        f.write("      },\n")
        else:
            if tabla['pk']:
                pk = tabla['pk'][0]
                f.write(f"      '{pk['nombre'].lower()}': {pk['nombre'].lower()},\n")
        
        for atributo in tabla['atributos']:
            es_fk = atributo.get('tabla_padre') is not None
            nombre_campo = atributo['nombre'].lower()
            
            if es_fk:
                # Para FKs, enviamos solo el ID
                f.write(f"      '{pk['nombre'].lower()}' : {{\n")
                if atributo.get('is_nullable', False):
                    f.write(f"        '{atributo['tabla_padre'].lower()}': {atributo['tabla_padre'].lower()}?.{atributo['atributo_padre'].lower()},\n")
                else:
                    f.write(f"        '{atributo['tabla_padre'].lower()}': {atributo['tabla_padre'].lower()}.{atributo['atributo_padre'].lower()},\n")
                f.write("      },\n")
            elif atributo['tipo_dato'] in ['date', 'datetime']:
                if atributo.get('is_nullable', False):
                    f.write(f"      '{nombre_campo}': {nombre_campo}?.toIso8601String(),\n")
                else:
                    f.write(f"      '{nombre_campo}': {nombre_campo}.toIso8601String(),\n")
            else:
                if atributo.get('is_nullable', False):
                    f.write(f"      '{nombre_campo}': {nombre_campo},\n")
                else:
                    f.write(f"      '{nombre_campo}': {nombre_campo},\n")

        f.write("    };\n")
        f.write("  }\n")
        f.write("}\n") 
        
def generar_main_dart(estructura, base_flutter):
    """Genera el archivo main.dart con navegación a todas las pantallas."""
    archivo = os.path.join(base_flutter, 'main.dart')
    
    with open(archivo, "w", encoding="utf-8") as f:
        f.write("import 'package:flutter/material.dart';\n")
        
        # Importar todas las screens
        for tabla_id, tabla in estructura['tablas'].items():
            nombre_clase = tabla['nombre'].capitalize()
            f.write(f"import 'screens/{nombre_clase.lower()}_screen.dart';\n")
        
        f.write("\n")
        f.write("void main() {\n")
        f.write("  runApp(const MyApp());\n")
        f.write("}\n\n")
        
        f.write("class MyApp extends StatelessWidget {\n")
        f.write("  const MyApp({Key? key}) : super(key: key);\n\n")
        f.write("  @override\n")
        f.write("  Widget build(BuildContext context) {\n")
        f.write("    return MaterialApp(\n")
        f.write("      title: 'App Generada',\n")
        f.write("      debugShowCheckedModeBanner: false,\n")
        f.write("      theme: ThemeData(\n")
        f.write("        primarySwatch: Colors.blue,\n")
        f.write("        useMaterial3: true,\n")
        f.write("      ),\n")
        f.write("      home: const HomePage(),\n")
        f.write("    );\n")
        f.write("  }\n")
        f.write("}\n\n")
        
        f.write("class HomePage extends StatelessWidget {\n")
        f.write("  const HomePage({Key? key}) : super(key: key);\n\n")
        f.write("  @override\n")
        f.write("  Widget build(BuildContext context) {\n")
        f.write("    return Scaffold(\n")
        f.write("      appBar: AppBar(\n")
        f.write("        title: const Text('Inicio'),\n")
        f.write("        centerTitle: true,\n")
        f.write("      ),\n")
        f.write("      body: Center(\n")
        f.write("        child: SingleChildScrollView(\n")
        f.write("          padding: const EdgeInsets.all(20),\n")
        f.write("          child: Column(\n")
        f.write("            mainAxisAlignment: MainAxisAlignment.center,\n")
        f.write("            children: [\n")
        f.write("              const Icon(Icons.home, size: 80, color: Colors.blue),\n")
        f.write("              const SizedBox(height: 20),\n")
        f.write("              const Text(\n")
        f.write("                'Bienvenido',\n")
        f.write("                style: TextStyle(fontSize: 28, fontWeight: FontWeight.bold),\n")
        f.write("              ),\n")
        f.write("              const SizedBox(height: 10),\n")
        f.write("              const Text(\n")
        f.write("                'Selecciona una opción',\n")
        f.write("                style: TextStyle(fontSize: 16, color: Colors.grey),\n")
        f.write("              ),\n")
        f.write("              const SizedBox(height: 40),\n")
        
        # Botones para cada tabla
        for _, tabla in estructura['tablas'].items():
            nombre_clase = tabla['nombre'].capitalize()
            f.write("              ElevatedButton.icon(\n")
            f.write("                onPressed: () {\n")
            f.write("                  Navigator.push(\n")
            f.write("                    context,\n")
            f.write(f"                    MaterialPageRoute(builder: (context) => const {nombre_clase}Screen()),\n")
            f.write("                  );\n")
            f.write("                },\n")
            f.write("                icon: const Icon(Icons.table_chart),\n")
            f.write(f"                label: Text('Gestionar {nombre_clase}'),\n")
            f.write("                style: ElevatedButton.styleFrom(\n")
            f.write("                  padding: const EdgeInsets.symmetric(horizontal: 30, vertical: 15),\n")
            f.write("                  textStyle: const TextStyle(fontSize: 16),\n")
            f.write("                ),\n")
            f.write("              ),\n")
            f.write("              const SizedBox(height: 15),\n")
        
        f.write("            ],\n")
        f.write("          ),\n")
        f.write("        ),\n")
        f.write("      ),\n")
        f.write("    );\n")
        f.write("  }\n")
        f.write("}\n")


def crear_zip_flutter(estructura):
    """Crea un ZIP con el proyecto Flutter completo."""
    flutter_original = os.path.join(BASE_DIR, 'flutter_application')
    temp_dir = tempfile.mkdtemp()
    flutter_copy = os.path.join(temp_dir, 'flutter_application')
    
    try:
        # Copiar proyecto
        shutil.copytree(flutter_original, flutter_copy)
        
        # Crear ZIP
        zip_filename = f"{estructura['diagrama']['nombre']}_flutter.zip"
        zip_path = os.path.join(temp_dir, zip_filename)
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(flutter_copy):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, temp_dir)
                    zipf.write(file_path, arcname)
        
        # Leer y codificar en base64
        with open(zip_path, 'rb') as f:
            zip_bytes = f.read()
        
        return base64.b64encode(zip_bytes).decode('utf-8')
    
    finally:
        # Limpiar temporales
        shutil.rmtree(temp_dir)


def generar_service_dart(tabla, base_services):
    """Genera el archivo service Dart para una tabla."""
    nombre_clase = tabla['nombre'].capitalize()
    nombre_var = tabla['nombre'].lower()
    nombre_archivo = f"{nombre_clase.lower()}_service.dart"
    archivo = os.path.join(base_services, nombre_archivo)
    
    tiene_pk_compuesta = len(tabla['pk']) > 1
    
    with open(archivo, "w", encoding="utf-8") as f:
        f.write("import 'dart:convert';\n")
        f.write("import 'package:http/http.dart' as http;\n")
        f.write(f"import '../models/{nombre_clase.lower()}_model.dart';\n\n")
        
        f.write(f"class {nombre_clase}Service {{\n")
        f.write(f"  static const String baseUrl = 'http://10.0.2.2:8080/api/{nombre_var}s';\n\n")
        
        # GET ALL
        f.write(f"  Future<List<{nombre_clase}>> getAll() async {{\n")
        f.write("    try {\n")
        f.write("      final response = await http.get(\n")
        f.write("        Uri.parse(baseUrl),\n")
        f.write("        headers: {'Content-Type': 'application/json'},\n")
        f.write("      );\n\n")
        f.write("      if (response.statusCode == 200) {\n")
        f.write("        List<dynamic> jsonList = json.decode(response.body);\n")
        f.write(f"        return jsonList.map((json) => {nombre_clase}.fromJson(json)).toList();\n")
        f.write("      } else {\n")
        f.write("        throw Exception('Error al cargar datos: ${response.statusCode}');\n")
        f.write("      }\n")
        f.write("    } catch (e) {\n")
        f.write("      throw Exception('Error de conexión: $e');\n")
        f.write("    }\n")
        f.write("  }\n\n")
        
        # GET BY ID
        if tiene_pk_compuesta:
            # Construir parámetros
            params = ', '.join([f"{tipo_a_dart.get(pk['tipo_dato'], 'int')} {pk['atributo_padre'].lower()}" for pk in tabla['pk']])
            path_params = '/'.join([f"${{{pk['atributo_padre'].lower()}}}" for pk in tabla['pk']])
            
            f.write(f"  Future<{nombre_clase}> getById({params}) async {{\n")
            f.write("    try {\n")
            f.write(f"      final response = await http.get(\n")
            f.write(f"        Uri.parse('$baseUrl/{path_params}'),\n")
        else:
            pk = tabla['pk'][0] if tabla['pk'] else None
            tipo_id = tipo_a_dart.get(pk['tipo_dato'], 'int') if pk else 'int'
            
            f.write(f"  Future<{nombre_clase}> getById({tipo_id} id) async {{\n")
            f.write("    try {\n")
            f.write("      final response = await http.get(\n")
            f.write("        Uri.parse('$baseUrl/$id'),\n")
        
        f.write("        headers: {'Content-Type': 'application/json'},\n")
        f.write("      );\n\n")
        f.write("      if (response.statusCode == 200) {\n")
        f.write(f"        return {nombre_clase}.fromJson(json.decode(response.body));\n")
        f.write("      } else {\n")
        f.write("        throw Exception('Error: ${response.statusCode}');\n")
        f.write("      }\n")
        f.write("    } catch (e) {\n")
        f.write("      throw Exception('Error de conexión: $e');\n")
        f.write("    }\n")
        f.write("  }\n\n")
        
        # CREATE
        f.write(f"  Future<{nombre_clase}> create({nombre_clase} {nombre_var}) async {{\n")
        f.write("    try {\n")
        f.write("      final response = await http.post(\n")
        f.write("        Uri.parse(baseUrl),\n")
        f.write("        headers: {'Content-Type': 'application/json'},\n")
        f.write(f"        body: json.encode({nombre_var}.toJson()),\n")
        f.write("      );\n\n")
        f.write("      if (response.statusCode == 200 || response.statusCode == 201) {\n")
        f.write(f"        return {nombre_clase}.fromJson(json.decode(response.body));\n")
        f.write("      } else {\n")
        f.write("        throw Exception('Error al crear: ${response.statusCode}');\n")
        f.write("      }\n")
        f.write("    } catch (e) {\n")
        f.write("      throw Exception('Error de conexión: $e');\n")
        f.write("    }\n")
        f.write("  }\n\n")
        
        # UPDATE
        if tiene_pk_compuesta:
            params = ', '.join([f"{tipo_a_dart.get(pk['tipo_dato'], 'int')} {pk['atributo_padre'].lower()}" for pk in tabla['pk']])
            path_params = '/'.join([f"${{{pk['atributo_padre'].lower()}}}" for pk in tabla['pk']])
            
            f.write(f"  Future<{nombre_clase}> update({params}, {nombre_clase} {nombre_var}) async {{\n")
            f.write("    try {\n")
            f.write("      final response = await http.put(\n")
            f.write(f"        Uri.parse('$baseUrl/{path_params}'),\n")
        else:
            tipo_id = tipo_a_dart.get(tabla['pk'][0]['tipo_dato'], 'int') if tabla['pk'] else 'int'
            f.write(f"  Future<{nombre_clase}> update({tipo_id} id, {nombre_clase} {nombre_var}) async {{\n")
            f.write("    try {\n")
            f.write("      final response = await http.put(\n")
            f.write("        Uri.parse('$baseUrl/$id'),\n")
        
        f.write("        headers: {'Content-Type': 'application/json'},\n")
        f.write(f"        body: json.encode({nombre_var}.toJson()),\n")
        f.write("      );\n\n")
        f.write("      if (response.statusCode == 200) {\n")
        f.write(f"        return {nombre_clase}.fromJson(json.decode(response.body));\n")
        f.write("      } else {\n")
        f.write("        throw Exception('Error al actualizar: ${response.statusCode}');\n")
        f.write("      }\n")
        f.write("    } catch (e) {\n")
        f.write("      throw Exception('Error de conexión: $e');\n")
        f.write("    }\n")
        f.write("  }\n\n")
        
        # DELETE
        if tiene_pk_compuesta:
            params = ', '.join([f"{tipo_a_dart.get(pk['tipo_dato'], 'int')} {pk['atributo_padre'].lower()}" for pk in tabla['pk']])
            path_params = '/'.join([f"${{{pk['atributo_padre'].lower()}}}" for pk in tabla['pk']])
            
            f.write(f"  Future<void> delete({params}) async {{\n")
            f.write("    try {\n")
            f.write("      final response = await http.delete(\n")
            f.write(f"        Uri.parse('$baseUrl/{path_params}'),\n")
        else:
            tipo_id = tipo_a_dart.get(tabla['pk'][0]['tipo_dato'], 'int') if tabla['pk'] else 'int'
            f.write(f"  Future<void> delete({tipo_id} id) async {{\n")
            f.write("    try {\n")
            f.write("      final response = await http.delete(\n")
            f.write("        Uri.parse('$baseUrl/$id'),\n")
        
        f.write("        headers: {'Content-Type': 'application/json'},\n")
        f.write("      );\n\n")
        f.write("      if (response.statusCode != 204 && response.statusCode != 200) {\n")
        f.write("        throw Exception('Error al eliminar: ${response.statusCode}');\n")
        f.write("      }\n")
        f.write("    } catch (e) {\n")
        f.write("      throw Exception('Error de conexión: $e');\n")
        f.write("    }\n")
        f.write("  }\n")
        
        f.write("}\n")

def generar_screen_dart(tabla, base_screens, todas_tablas):
    """Genera el archivo screen Dart para una tabla."""
    nombre_clase = tabla['nombre'].capitalize()
    nombre_archivo = f"{nombre_clase.lower()}_screen.dart"
    archivo = os.path.join(base_screens, nombre_archivo)
    
    tiene_pk_compuesta = len(tabla['pk']) > 1
    
    with open(archivo, "w", encoding="utf-8") as f:
        f.write("import 'package:flutter/material.dart';\n")
        f.write(f"import '../models/{nombre_clase.lower()}_model.dart';\n")
        f.write(f"import '../services/{nombre_clase.lower()}_service.dart';\n")
        
        for pk in tabla['pk']:
            if pk.get('tabla_padre'):
                tabla_padre_cap = pk['tabla_padre']
                f.write(f"import '../models/{tabla_padre_cap}_model.dart';\n")
                f.write(f"import '../services/{tabla_padre_cap}_service.dart';\n")
        
        # Importar modelos de tablas relacionadas (FKs)
        for atributo in tabla['atributos']:
            if atributo.get('tabla_padre'):
                tabla_padre_cap = atributo['tabla_padre']
                f.write(f"import '../models/{tabla_padre_cap}_model.dart';\n")
                f.write(f"import '../services/{tabla_padre_cap}_service.dart';\n")
        
        f.write("\n")
        
        # ===== CLASE PRINCIPAL =====
        f.write(f"class {nombre_clase}Screen extends StatefulWidget {{\n")
        f.write(f"  const {nombre_clase}Screen({{super.key}});\n\n")
        f.write("  @override\n")
        f.write(f"  State<{nombre_clase}Screen> createState() => _{nombre_clase}ScreenState();\n")
        f.write("}\n\n")
        
        f.write(f"class _{nombre_clase}ScreenState extends State<{nombre_clase}Screen> {{\n")
        f.write(f"  final {nombre_clase}Service _service = {nombre_clase}Service();\n")
        f.write(f"  List<{nombre_clase}> _items = [];\n")
        f.write("  bool _isLoading = true;\n")
        f.write("  String? _error;\n\n")
        
        f.write("  @override\n")
        f.write("  void initState() {\n")
        f.write("    super.initState();\n")
        f.write("    _loadItems();\n")
        f.write("  }\n\n")
        
        # LOAD ITEMS
        f.write("  Future<void> _loadItems() async {\n")
        f.write("    setState(() {\n")
        f.write("      _isLoading = true;\n")
        f.write("      _error = null;\n")
        f.write("    });\n\n")
        f.write("    try {\n")
        f.write("      final items = await _service.getAll();\n")
        f.write("      setState(() {\n")
        f.write("        _items = items;\n")
        f.write("        _isLoading = false;\n")
        f.write("      });\n")
        f.write("    } catch (e) {\n")
        f.write("      setState(() {\n")
        f.write("        _error = e.toString();\n")
        f.write("        _isLoading = false;\n")
        f.write("      });\n")
        f.write("    }\n")
        f.write("  }\n\n")
        
        # DELETE ITEM
        if tiene_pk_compuesta:
            params = ', '.join([f"{tipo_a_dart.get(pk['tipo_dato'], 'int')} {pk['atributo_padre'].lower()}" for pk in tabla['pk']])
            args = ', '.join([pk['atributo_padre'].lower() for pk in tabla['pk']])
            f.write(f"  Future<void> _deleteItem({params}) async {{\n")
        else:
            pk = tabla['pk'][0] if tabla['pk'] else None
            tipo_id = tipo_a_dart.get(pk['tipo_dato'], 'int') if pk else 'int'
            f.write(f"  Future<void> _deleteItem({tipo_id} id) async {{\n")
            args = "id"
        
        f.write("    try {\n")
        f.write(f"      await _service.delete({args});\n")
        f.write("      await _loadItems();\n")
        f.write("      if (mounted) {\n")
        f.write("        ScaffoldMessenger.of(context).showSnackBar(\n")
        f.write("          const SnackBar(content: Text('Eliminado correctamente'), backgroundColor: Colors.green),\n")
        f.write("        );\n")
        f.write("      }\n")
        f.write("    } catch (e) {\n")
        f.write("      if (mounted) {\n")
        f.write("        ScaffoldMessenger.of(context).showSnackBar(\n")
        f.write("          SnackBar(content: Text('Error: $e'), backgroundColor: Colors.red),\n")
        f.write("        );\n")
        f.write("      }\n")
        f.write("    }\n")
        f.write("  }\n\n")
        
        # SHOW FORM DIALOG
        f.write(f"  void _showFormDialog({{{nombre_clase}? item}}) {{\n")
        f.write("    showDialog(\n")
        f.write("      context: context,\n")
        f.write(f"      builder: (context) => {nombre_clase}FormDialog(\n")
        f.write("        item: item,\n")
        f.write(f"        onSave: ({nombre_clase} newItem) async {{\n")
        f.write("          final parentContext = context;\n")
        f.write("          try {\n")
        f.write("            if (item == null) {\n")
        f.write("              await _service.create(newItem);\n")
        f.write("            } else {\n")
        
        if tiene_pk_compuesta:
            update_args = ' || '.join([f"newItem.{pk['atributo_padre'].lower()} != item.{pk['atributo_padre'].lower()}" for pk in tabla['pk']])
            f.write(f"               if ({update_args}) {{\n")
            args = ', '.join([f"item.{pk['atributo_padre'].lower()}!" for pk in tabla['pk']])
            f.write(f"                 await _service.create(newItem);\n")
            f.write(f"                 await _service.delete({args});\n")
            f.write("               } else {\n") 
            f.write(f"                 await _service.update({args}, newItem);\n")
            f.write("               }\n")
        else:
            pk = tabla['pk'][0] if tabla['pk'] else None
            pk_name = pk['nombre'].lower() if pk else 'id'
            f.write(f"              await _service.update(item.{pk_name}!, newItem);\n")
        
        f.write("            }\n")
        f.write("            await _loadItems();\n")
        f.write("            if (mounted) {\n")
        f.write("              Navigator.pop(parentContext);\n")
        f.write("              ScaffoldMessenger.of(parentContext).showSnackBar(\n")
        f.write("                SnackBar(content: Text(item == null ? 'Creado correctamente' : 'Actualizado'),\n")
        f.write("                backgroundColor: Colors.green\n")
        f.write("                ),\n")
        f.write("              );\n")
        f.write("            }\n")
        f.write("          } catch (e) {\n")
        f.write("            if (mounted) {\n")
        f.write("              ScaffoldMessenger.of(parentContext).showSnackBar(\n")
        f.write("                SnackBar(content: Text('Error: ${e.toString()}'), backgroundColor: Colors.red, duration: const Duration(seconds: 4)),\n")
        f.write("              );\n")
        f.write("            }\n")
        f.write("          }\n")
        f.write("        },\n")
        f.write("      ),\n")
        f.write("    );\n")
        f.write("  }\n\n")
        
        # SHOW DETAILS - ✅ CORREGIDO: Parámetro posicional
        f.write(f"  void _showDetails({nombre_clase} item) {{\n")  # ← SIN llaves, parámetro posicional
        f.write("    showDialog(\n")
        f.write("      context: context,\n")
        f.write("      builder: (context) => AlertDialog(\n")
        f.write(f"        title: const Text('Detalles de {nombre_clase}'),\n")
        f.write("        content: Column(\n")
        f.write("          mainAxisSize: MainAxisSize.min,\n")
        f.write("          crossAxisAlignment: CrossAxisAlignment.start,\n")
        f.write("          children: [\n")
        
        # Mostrar PKs - ✅ CORREGIDO: Sin \\ en $
        if tiene_pk_compuesta:
            for pk in tabla['pk']:
                label = pk['atributo_padre'].capitalize()
                f.write(f"            Text('{label}: ${{item.{pk['atributo_padre'].lower()}}}', style: const TextStyle(fontWeight: FontWeight.bold)),\n")
                f.write("            const SizedBox(height: 8),\n")
        else:
            if tabla['pk']:
                pk = tabla['pk'][0]
                label = pk['nombre'].capitalize()
                f.write(f"            Text('{label}: ${{item.{pk['nombre'].lower()}}}', style: const TextStyle(fontWeight: FontWeight.bold)),\n")
                f.write("            const SizedBox(height: 8),\n")
        # children: [
        #     Text('Ordenid: ${item.ordenid}'),
        #     /*Text('Orden ID: ${item.ordenid}', style: const TextStyle(fontWeight: FontWeight.bold)),
        #     const SizedBox(height: 8), */
        #     Text('Productoid: ${item.productoid}'),
        #     /**
        #     Text('Producto ID: ${item.productoid}', style: const TextStyle(fontWeight: FontWeight.bold)),
        #     const SizedBox(height: 8), 
        #      */
        #     Text('Cantidad: ${item.cantidad}'),
        
        # Mostrar atributos - ✅ CORREGIDO: Sin \\ en $
        for atributo in tabla['atributos']:
            es_fk = atributo.get('tabla_padre') is not None
            label = atributo['nombre'].capitalize()
            
            if es_fk:
                f.write(f"            Text('{label}: ${{item.{atributo['tabla_padre'].lower()}?.toString() ?? \"N/A\"}}'),\n")
            else:
                f.write(f"            Text('{label}: ${{item.{atributo['nombre'].lower()}}}'),\n")
        
        f.write("          ],\n")
        f.write("        ),\n")
        f.write("        actions: [\n")
        f.write("          TextButton(onPressed: () => Navigator.pop(context), child: const Text('Cerrar')),\n")
        f.write("        ],\n")
        f.write("      ),\n")
        f.write("    );\n")
        f.write("  }\n\n")
        
        # BUILD
        f.write("  @override\n")
        f.write("  Widget build(BuildContext context) {\n")
        f.write("    return Scaffold(\n")
        f.write("      appBar: AppBar(\n")
        f.write(f"        title: const Text('{nombre_clase}'),\n")
        f.write("        actions: [\n")
        f.write("          IconButton(icon: const Icon(Icons.refresh), onPressed: _loadItems),\n")
        f.write("        ],\n")
        f.write("      ),\n")
        f.write("      body: _isLoading\n")
        f.write("          ? const Center(child: CircularProgressIndicator())\n")
        f.write("          : _error != null\n")
        f.write("              ? Center(\n")
        f.write("                  child: Column(\n")
        f.write("                    mainAxisAlignment: MainAxisAlignment.center,\n")
        f.write("                    children: [\n")
        f.write("                      const Icon(Icons.error, color: Colors.red, size: 60),\n")
        f.write("                      const SizedBox(height: 16),\n")
        f.write("                      Text(_error!, textAlign: TextAlign.center),\n")
        f.write("                      const SizedBox(height: 16),\n")
        f.write("                      ElevatedButton(\n")
        f.write("                        onPressed: _loadItems,\n")
        f.write("                        child: const Text('Reintentar'),\n")
        f.write("                      ),\n")
        f.write("                    ],\n")
        f.write("                  ),\n")
        f.write("                )\n")
        f.write("              : _items.isEmpty\n")
        f.write("                  ? const Center(\n")
        f.write("                      child: Column(\n")
        f.write("                        mainAxisAlignment: MainAxisAlignment.center,\n")
        f.write("                        children: [\n")
        f.write("                          Icon(Icons.inbox, size: 60, color: Colors.grey),\n")
        f.write("                          SizedBox(height: 16),\n")
        f.write(f"                          Text('No hay {nombre_clase}', style: TextStyle(fontSize: 16)),\n")
        f.write("                        ],\n")
        f.write("                      ),\n")
        f.write("                    )\n")
        f.write("                  : ListView.builder(\n")
        f.write("                      itemCount: _items.length,\n")
        f.write("                      itemBuilder: (context, index) {\n")
        f.write("                        final item = _items[index];\n")
        f.write("                        return Card(\n")
        f.write("                          margin: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),\n")
        f.write("                          child: ListTile(\n")
        
        # Título del ListTile - ✅ CORREGIDO: Sin \\ en $
        primer_atributo = None
        for atr in tabla['atributos']:
            if not atr.get('tabla_padre'):
                primer_atributo = atr['nombre'].lower()
            break
        if tiene_pk_compuesta:
            primer_atributo = ' - '.join([f"{pk['tabla_padre'].capitalize()}: ${{item.{pk['atributo_padre'].lower()}}}" for pk in tabla['pk']])
            f.write(f"                            title: Text('{primer_atributo}'),\n")
        elif tabla['pk'][0] is not None:
            f.write(f"                            title: Text('ID: ${{item.{tabla['pk'][0]['nombre'].lower()}}}'),\n")
        else:
            if primer_atributo:
                f.write(f"                            title: Text('{primer_atributo}'),\n")
        if primer_atributo:
            f.write(f"                                subtitle: Text('{primer_atributo}'),\n")
        
        # if primer_atributo:
        #     f.write(f"                            title: Text('${{item.{primer_atributo}}}'),\n")
        # else:
        #     if tiene_pk_compuesta:
        #         #f.write(f"                            title: Text('ID: ${{item.{tabla['pk'][0]['atributo_padre'].lower()}}}'),\n")
        #         primeros_pk = ' - '.join([f"{pk['tabla_padre'].capitalize()}: ${{item.{pk['atributo_padre'].lower()}}}" for pk in tabla['pk']])
        #         f.write(f"                            title: Text('{primeros_pk}'),\n")
        #     else:
        #         f.write(f"                            title: Text('ID: ${{item.{tabla['pk'][0]['nombre'].lower()}}}'),\n")
        
        f.write("                            trailing: Row(\n")
        f.write("                              mainAxisSize: MainAxisSize.min,\n")
        f.write("                              children: [\n")
        f.write("                                IconButton(\n")
        f.write("                                  icon: const Icon(Icons.visibility, color: Colors.blue),\n")
        f.write("                                  onPressed: () => _showDetails(item),\n")  # ← Sin llaves
        f.write("                                ),\n")
        f.write("                                IconButton(\n")
        f.write("                                  icon: const Icon(Icons.edit, color: Colors.orange),\n")
        f.write("                                  onPressed: () => _showFormDialog(item: item),\n")
        f.write("                                ),\n")
        f.write("                                IconButton(\n")
        f.write("                                  icon: const Icon(Icons.delete, color: Colors.red),\n")
        f.write("                                  onPressed: () {\n")
        f.write("                                    showDialog(\n")
        f.write("                                      context: context,\n")
        f.write("                                      builder: (ctx) => AlertDialog(\n")
        f.write("                                        title: const Text('Confirmar eliminación'),\n")
        f.write("                                        content: const Text('¿Está seguro de eliminar este elemento?'),\n")
        f.write("                                        actions: [\n")
        f.write("                                          TextButton(\n")
        f.write("                                            onPressed: () => Navigator.pop(ctx),\n")
        f.write("                                            child: const Text('Cancelar'),\n")
        f.write("                                          ),\n")
        f.write("                                          ElevatedButton(\n")
        f.write("                                            style: ElevatedButton.styleFrom(\n")
        f.write("                                              backgroundColor: Colors.red,\n")
        f.write("                                            ),\n")
        f.write("                                            onPressed: () {\n")
        f.write("                                              Navigator.pop(ctx);\n")
        
        if tiene_pk_compuesta:
            delete_args = ', '.join([f"item.{pk['atributo_padre'].lower()}!" for pk in tabla['pk']])
            f.write(f"                                              _deleteItem({delete_args});\n")
        else:
            pk = tabla['pk'][0] if tabla['pk'] else None
            pk_name = pk['nombre'].lower() if pk else 'id'
            f.write(f"                                              _deleteItem(item.{pk_name}!);\n")
        
        f.write("                                            },\n")
        f.write("                                            child: const Text('Eliminar'),\n")
        f.write("                                          ),\n")
        f.write("                                        ],\n")
        f.write("                                      ),\n")
        f.write("                                    );\n")
        f.write("                                  },\n")
        f.write("                                ),\n")
        f.write("                              ],\n")
        f.write("                            ),\n")
        f.write("                          ),\n")
        f.write("                        );\n")
        f.write("                      },\n")
        f.write("                    ),\n")
        f.write("      floatingActionButton: FloatingActionButton(\n")
        f.write("        onPressed: () => _showFormDialog(),\n")
        f.write("        child: const Icon(Icons.add),\n")
        f.write("      ),\n")
        f.write("    );\n")
        f.write("  }\n")
        f.write("}\n\n")
        
        # ===== FORMULARIO =====
        generar_formulario_dart(f, tabla, nombre_clase, todas_tablas)


def generar_formulario_dart(f, tabla, nombre_clase, todas_tablas):
    """Genera el diálogo de formulario dentro del mismo archivo."""
    nombre_var = tabla['nombre'].lower()
    tiene_pk_compuesta = len(tabla['pk']) > 1
    
    f.write(f"class {nombre_clase}FormDialog extends StatefulWidget {{\n")
    f.write(f"  final {nombre_clase}? item;\n")
    f.write(f"  final Function({nombre_clase}) onSave;\n\n")
    f.write(f"  const {nombre_clase}FormDialog({{super.key, this.item, required this.onSave}});\n\n")
    f.write("  @override\n")
    f.write(f"  State<{nombre_clase}FormDialog> createState() => _{nombre_clase}FormDialogState();\n")
    f.write("}\n\n")
    
    f.write(f"class _{nombre_clase}FormDialogState extends State<{nombre_clase}FormDialog> {{\n")
    f.write("  final _formKey = GlobalKey<FormState>();\n")    
    if tiene_pk_compuesta:
        for pk in tabla['pk']:
            if pk.get('tabla_padre'):
                f.write(f"  final {pk['tabla_padre'].capitalize()}Service _{pk['tabla_padre'].lower()}Service = {pk['tabla_padre'].capitalize()}Service();\n")
                
        for pk in tabla['pk']:
            if pk.get('tabla_padre'):
                f.write(f"  List<{pk['tabla_padre'].capitalize()}> _{pk['tabla_padre'].lower()}List = [];\n")
                f.write(f"  {pk['tabla_padre'].capitalize()}? _selected{pk['tabla_padre'].capitalize()};\n")

    # Controllers para cada campo (excepto PKs auto_increment y FKs)
    for atributo in tabla['atributos']:
        es_fk = atributo.get('tabla_padre') is not None
        if not es_fk:
            f.write(f"  late TextEditingController _{atributo['nombre'].lower()}Controller;\n")
    
    # Variables para dropdowns de FKs
    for atributo in tabla['atributos']:
        if atributo.get('tabla_padre'):
            tabla_padre_cap = atributo['tabla_padre'].capitalize()
            f.write(f"  List<{tabla_padre_cap}> _{atributo['tabla_padre'].lower()}List = [];\n")
            f.write(f"  {tabla_padre_cap}? _selected{tabla_padre_cap};\n")
    f.write("  bool _isLoadingData = true;\n")
    
    f.write("\n  @override\n")
    f.write("  void initState() {\n")
    f.write("    super.initState();\n")
    
    
    # Inicializar controllers
    for atributo in tabla['atributos']:
        es_fk = atributo.get('tabla_padre') is not None
        if not es_fk:
            nombre_campo = atributo['nombre'].lower()
            tipo_dato = atributo['tipo_dato']
            is_nullable = atributo.get('is_nullable', False)
            
            # Para DateTime, convertir a formato string
            if tipo_dato in ['date', 'datetime']:
                if is_nullable:
                    f.write(f"    _{nombre_campo}Controller = TextEditingController(\n")
                    f.write(f"      text: widget.item?.{nombre_campo} != null\n")
                    f.write(f"          ? widget.item!.{nombre_campo}!.toIso8601String().split('T')[0]\n")
                    f.write(f"          : ''\n")
                    f.write(f"    );\n")
                else:
                    f.write(f"    _{nombre_campo}Controller = TextEditingController(\n")
                    f.write(f"      text: widget.item != null\n")
                    f.write(f"          ? widget.item!.{nombre_campo}.toIso8601String().split('T')[0]\n")
                    f.write(f"          : ''\n")
                    f.write(f"    );\n")
            else:
                if is_nullable:
                    f.write(f"    _{nombre_campo}Controller = TextEditingController(\n")
                    f.write(f"      text: widget.item?.{nombre_campo} != null ? widget.item!.{nombre_campo}.toString() : ''\n")
                    f.write(f"    );\n")
                else:
                    f.write(f"    _{nombre_campo}Controller = TextEditingController(\n")
                    f.write(f"      text: widget.item != null ? widget.item!.{nombre_campo}.toString() : ''\n")
                    f.write(f"    );\n")
    
    f.write("    _loadData();\n")
    f.write("  }\n\n")
    f.write("  Future<void> _loadData() async {\n")
    f.write("    await Future.wait([\n")
    for atributo in tabla['fk']:
        tabla_padre_cap = atributo['tabla_padre'].capitalize()
        f.write(f"    _load{tabla_padre_cap}();\n")
    f.write("    ]);\n")
    f.write("  }\n\n")
    
    # Métodos para cargar FKs - ✅ CORREGIDO: Sin print, con mounted
    if tiene_pk_compuesta:
        for pk in tabla['pk']:
            tabla_padre_cap = pk['tabla_padre'].capitalize()
            tabla_padre_lower = pk['tabla_padre'].lower()
            
            f.write(f"  Future<void> _load{tabla_padre_cap}() async {{\n")
            f.write("    try {\n")
            f.write(f"      final service = {tabla_padre_cap}Service();\n")
            f.write(f"      final items = await service.getAll();\n")
            f.write("      if (mounted) {\n")
            f.write("        setState(() {\n")
            f.write(f"          _{tabla_padre_lower}List = items;\n")
            f.write(f"          if (widget.item?.{pk['atributo_padre'].lower()} != null) {{\n")
            f.write(f"            // Buscar el objeto completo basado en el ID\n")
            f.write(f"            _selected{tabla_padre_cap} = items.firstWhere(\n")
            f.write(f"              (cat) => cat.{pk['atributo_padre'].lower()} == widget.item!.{pk['atributo_padre'].lower()},\n")
            f.write(f"              orElse: () => items.first,\n")
            f.write(f"            );\n")
            f.write("          }\n")
            f.write("          _isLoadingData = false;\n")
            f.write("        });\n")
            f.write("      }\n")
            f.write("    } catch (e) {\n")
            f.write("      if (mounted) {\n")
            f.write("        setState(() {\n")
            f.write("          _isLoadingData = false;\n")
            f.write("        });\n")
            f.write("      }\n")
            f.write("    }\n")
            f.write("  }\n\n")
    elif tabla['pk'][0]['tabla_padre'] is not None:
        atributo = tabla['pk'][0]
        print(atributo)
        tabla_padre_cap = atributo['tabla_padre'].capitalize()
        tabla_padre_lower = atributo['tabla_padre'].lower()
        
        f.write(f"  Future<void> _load{tabla_padre_cap}() async {{\n")
        f.write("    try {\n")
        f.write(f"      final service = {tabla_padre_cap}Service();\n")
        f.write(f"      final items = await service.getAll();\n")
        f.write("      if (mounted) {\n")
        f.write("        setState(() {\n")
        f.write(f"          _{tabla_padre_lower}List = items;\n")
        f.write(f"          if (widget.item?.{tabla_padre_lower} != null) {{\n")
        f.write(f"            _selected{tabla_padre_cap} = widget.item!.{tabla_padre_lower};\n")
        f.write("          }\n")
        f.write("        });\n")
        f.write("      }\n")
        f.write("    } catch (e) {\n")
        f.write("      if (mounted) {\n")
        f.write("        setState(() {\n")
        f.write("          _isLoadingData = false;\n")
        f.write("        });\n")
        f.write("      }\n")
        f.write("    }\n")
        f.write("  }\n\n")
        
    for atributo in tabla['atributos']:
        if atributo.get('tabla_padre'):
            tabla_padre_cap = atributo['tabla_padre'].capitalize()
            tabla_padre_lower = atributo['tabla_padre'].lower()
            
            f.write(f"  Future<void> _load{tabla_padre_cap}() async {{\n")
            f.write("    try {\n")
            f.write(f"      final service = {tabla_padre_cap}Service();\n")
            f.write(f"      final items = await service.getAll();\n")
            f.write("      if (mounted) {\n")
            f.write("        setState(() {\n")
            f.write(f"          _{tabla_padre_lower}List = items;\n")
            f.write(f"          if (widget.item?.{tabla_padre_lower} != null) {{\n")
            f.write("             // Buscar el objeto completo basado en el ID\n")
            f.write(f"            _selected{tabla_padre_cap} = _{tabla_padre_lower}List.firstWhere(\n")
            f.write(f"              (cat) => cat.{atributo['atributo_padre'].lower()} == widget.item!.{tabla_padre_lower}.{pk['atributo_padre'].lower()},\n")
            f.write(f"              orElse: () => items.first,\n")
            f.write(f"            );\n")
            f.write("          }\n")
            f.write("          _isLodingData = false;\n")
            f.write("        });\n")
            f.write("      }\n")
            f.write("    } catch (e) {\n")
            f.write("      if (mounted) {\n")
            f.write("        setState(() {\n")
            f.write("          _isLoadingData = false;\n")
            f.write("        });\n")
            f.write("      }\n")
            f.write("    }\n")
            f.write("  }\n\n")

    # Dispose
    f.write("  @override\n")
    f.write("  void dispose() {\n")
    for atributo in tabla['atributos']:
        if not atributo.get('tabla_padre'):
            f.write(f"    _{atributo['nombre'].lower()}Controller.dispose();\n")
    f.write("    super.dispose();\n")
    f.write("  }\n\n")
    
    # Build
    f.write("  @override\n")
    f.write("  Widget build(BuildContext context) {\n")
    f.write("    return AlertDialog(\n")
    f.write(f"      title: Text(widget.item == null ? 'Crear' : 'Editar'),\n")
    f.write("      content: Form(\n")
    f.write("        key: _formKey,\n")
    f.write("        child: SingleChildScrollView(\n")
    f.write("          child: Column(\n")
    f.write("            mainAxisSize: MainAxisSize.min,\n")
    f.write("            children: [\n")
    
    # ✅ AGREGAR ESTO PRIMERO: Dropdowns para PKs que son FK
    if tiene_pk_compuesta:
        for pk in tabla['pk']:
            if pk.get('tabla_padre'):  # Es FK dentro de PK
                tabla_padre_cap = pk['tabla_padre'].capitalize()
                tabla_padre_lower = pk['tabla_padre'].lower()
                label = pk['nombre'].capitalize()
                
                f.write(f"              DropdownButtonFormField<{tabla_padre_cap}>(\n")
                f.write(f"                value: _selected{tabla_padre_cap},\n")
                f.write(f"                decoration: const InputDecoration(labelText: '{label}'),\n")
                f.write(f"                items: _{tabla_padre_lower}List.map((item) {{\n")
                f.write("                  return DropdownMenuItem(\n")
                f.write("                    value: item,\n")
                
                # Buscar campo para mostrar
                tabla_relacionada = None
                for _, t in todas_tablas.items():
                    if t['nombre'] == pk['tabla_padre']:
                        tabla_relacionada = t
                        break
                
                campo_display = None
                if tabla_relacionada:
                    for atr in tabla_relacionada['atributos']:
                        if atr['tipo_dato'] in ['char', 'text']:
                            campo_display = atr['nombre'].lower()
                            break
                
                if campo_display:
                    f.write(f"                    child: Text('${{item.{campo_display}}}'),\n")
                else:
                    if tabla_relacionada and tabla_relacionada['pk']:
                        pk_display = tabla_relacionada['pk'][0]['nombre'].lower()
                        f.write(f"                    child: Text('ID: ${{item.{pk_display}}}'),\n")
                    else:
                        f.write("                    child: Text(item.toString()),\n")
                
                f.write("                  );\n")
                f.write("                }).toList(),\n")
                f.write("                onChanged: (value) {\n")
                f.write("                  setState(() {\n")
                f.write(f"                    _selected{tabla_padre_cap} = value;\n")
                f.write("                  });\n")
                f.write("                },\n")
                f.write("                validator: (v) => v == null ? 'Requerido' : null,\n")
                f.write("              ),\n")
                f.write("              const SizedBox(height: 12),\n")
    # Campos del formulario
    for atributo in tabla['atributos']:
        es_fk = atributo.get('tabla_padre') is not None
        nombre_campo = atributo['nombre'].lower()
        label = atributo['nombre'].capitalize()
        tipo_dato = atributo['tipo_dato']
        
        if es_fk:
            # Dropdown para FK - ✅ CORREGIDO: value en lugar de initialValue
            tabla_padre_cap = atributo['tabla_padre'].capitalize()
            tabla_padre_lower = atributo['tabla_padre'].lower()
            
            f.write(f"              DropdownButtonFormField<{tabla_padre_cap}>(\n")
            f.write(f"                value: _selected{tabla_padre_cap},\n")
            f.write(f"                decoration: const InputDecoration(labelText: '{label}'),\n")
            f.write(f"                items: _{tabla_padre_lower}List.map((item) {{\n")
            f.write("                  return DropdownMenuItem(\n")
            f.write("                    value: item,\n")
            
            # Buscar primer atributo de texto para mostrar
            tabla_relacionada = None
            for _, t in todas_tablas.items():
                if t['nombre'] == atributo['tabla_padre']:
                    tabla_relacionada = t
                    break
            
            campo_display = None
            if tabla_relacionada:
                for atr in tabla_relacionada['atributos']:
                    if atr['tipo_dato'] in ['char', 'text']:
                        campo_display = atr['nombre'].lower()
                        break
            
            # ✅ CORREGIDO: Sin \\ en $
            if campo_display:
                f.write(f"                    child: Text('${{item.{campo_display}}}'),\n")
            else:
                # Mostrar PK si no hay campo de texto
                if tabla_relacionada and tabla_relacionada['pk']:
                    pk_display = tabla_relacionada['pk'][0]['nombre'].lower()
                    f.write(f"                    child: Text('ID: ${{item.{pk_display}}}'),\n")
                else:
                    f.write("                    child: Text(item.toString()),\n")
            
            f.write("                  );\n")
            f.write("                }).toList(),\n")
            f.write("                onChanged: (value) {\n")
            f.write("                  setState(() {\n")
            f.write(f"                    _selected{tabla_padre_cap} = value;\n")
            f.write("                  });\n")
            f.write("                },\n")
            
            if not atributo.get('is_nullable', False):
                f.write("                validator: (v) => v == null ? 'Requerido' : null,\n")
            
            f.write("              ),\n")
            f.write("              const SizedBox(height: 12),\n")
            
        elif tipo_dato in ['date', 'datetime']:
            # Campo de fecha con DatePicker
            f.write(f"              TextFormField(\n")
            f.write(f"                controller: _{nombre_campo}Controller,\n")
            f.write(f"                decoration: InputDecoration(\n")
            f.write(f"                  labelText: '{label}',\n")
            f.write(f"                  suffixIcon: IconButton(\n")
            f.write(f"                    icon: const Icon(Icons.calendar_today),\n")
            f.write(f"                    onPressed: () async {{\n")
            f.write(f"                      final date = await showDatePicker(\n")
            f.write(f"                        context: context,\n")
            f.write(f"                        initialDate: DateTime.now(),\n")
            f.write(f"                        firstDate: DateTime(2000),\n")
            f.write(f"                        lastDate: DateTime(2100),\n")
            f.write(f"                      );\n")
            f.write(f"                      if (date != null) {{\n")
            f.write(f"                        setState(() {{\n")
            f.write(f"                          _{nombre_campo}Controller.text = date.toIso8601String().split('T')[0];\n")
            f.write(f"                        }});\n")
            f.write(f"                      }}\n")
            f.write(f"                    }},\n")
            f.write(f"                  ),\n")
            f.write(f"                ),\n")
            f.write(f"                readOnly: true,\n")
            
            if not atributo.get('is_nullable', False):
                f.write("                validator: (v) => v!.isEmpty ? 'Requerido' : null,\n")
            
            f.write("              ),\n")
            f.write("              const SizedBox(height: 12),\n")
            
        else:
            # Campo de texto normal
            f.write(f"              TextFormField(\n")
            f.write(f"                controller: _{nombre_campo}Controller,\n")
            f.write(f"                decoration: const InputDecoration(labelText: '{label}'),\n")
            
            if tipo_dato in ['integer', 'smallint', 'bigint', 'float', 'decimal']:
                f.write("                keyboardType: TextInputType.number,\n")
            
            # Validaciones
            if not atributo.get('is_nullable', False):
                f.write("                validator: (v) => v!.isEmpty ? 'Requerido' : null,\n")
            
            f.write("              ),\n")
            f.write("              const SizedBox(height: 12),\n")
    
    f.write("            ],\n")
    f.write("          ),\n")
    f.write("        ),\n")
    f.write("      ),\n")
    f.write("      actions: [\n")
    f.write("        TextButton(\n")
    f.write("          onPressed: () => Navigator.pop(context),\n")
    f.write("          child: const Text('Cancelar'),\n")
    f.write("        ),\n")
    f.write("        ElevatedButton(\n")
    f.write("          onPressed: () {\n")
    f.write("            if (_formKey.currentState!.validate()) {\n")
    f.write(f"              widget.onSave({nombre_clase}(\n")
    
    # Pasar valores al constructor
    if tiene_pk_compuesta:
        for pk in tabla['pk']:
            if pk.get('tabla_padre'):
                tabla_padre_cap = pk['tabla_padre'].capitalize()
                f.write(f"                {pk['atributo_padre'].lower()}: _selected{tabla_padre_cap}?.{pk['atributo_padre'].lower()},\n")
            else:
                f.write(f"                {pk['atributo_padre'].lower()}: widget.item?.{pk['atributo_padre'].lower()},\n")
    else:
        if tabla['pk']:
            pk = tabla['pk'][0]
            f.write(f"                {pk['nombre'].lower()}: widget.item?.{pk['nombre'].lower()},\n")
    
    for atributo in tabla['atributos']:
        es_fk = atributo.get('tabla_padre') is not None
        nombre_campo = atributo['nombre'].lower()
        is_nullable = atributo.get('is_nullable', False)
        tipo_dato = atributo['tipo_dato']
        
        if es_fk:
            tabla_padre_cap = atributo['tabla_padre'].capitalize()
            # Si no es nullable, agregar !
            if not is_nullable:
                f.write(f"                {atributo['tabla_padre'].lower()}: _selected{tabla_padre_cap}!,\n")
            else:
                f.write(f"                {atributo['tabla_padre'].lower()}: _selected{tabla_padre_cap},\n")
        else:
            if tipo_dato in ['integer', 'smallint', 'bigint']:
                if not is_nullable:
                    f.write(f"                {nombre_campo}: int.parse(_{nombre_campo}Controller.text),\n")
                else:
                    f.write(f"                {nombre_campo}: _{nombre_campo}Controller.text.isEmpty ? null : int.tryParse(_{nombre_campo}Controller.text),\n")
                    
            elif tipo_dato in ['float', 'decimal']:
                # ✅ CORREGIDO: replaceAll(',', '.')
                if not is_nullable:
                    f.write(f"                {nombre_campo}: double.parse(_{nombre_campo}Controller.text.replaceAll(',', '.')),\n")
                else:
                    f.write(f"                {nombre_campo}: _{nombre_campo}Controller.text.isEmpty ? null : double.tryParse(_{nombre_campo}Controller.text.replaceAll(',', '.')),\n")
                    
            elif tipo_dato == 'boolean':
                if not is_nullable:
                    f.write(f"                {nombre_campo}: _{nombre_campo}Controller.text.toLowerCase() == 'true',\n")
                else:
                    f.write(f"                {nombre_campo}: _{nombre_campo}Controller.text.isEmpty ? null : _{nombre_campo}Controller.text.toLowerCase() == 'true',\n")
                    
            elif tipo_dato in ['date', 'datetime']:
                if not is_nullable:
                    f.write(f"                {nombre_campo}: DateTime.parse(_{nombre_campo}Controller.text),\n")
                else:
                    f.write(f"                {nombre_campo}: _{nombre_campo}Controller.text.isEmpty ? null : DateTime.parse(_{nombre_campo}Controller.text),\n")
                    
            else:
                # String
                if not is_nullable:
                    f.write(f"                {nombre_campo}: _{nombre_campo}Controller.text,\n")
                else:
                    f.write(f"                {nombre_campo}: _{nombre_campo}Controller.text.isEmpty ? null : _{nombre_campo}Controller.text,\n")
    
    f.write("              ));\n")
    f.write("            }\n")
    f.write("          },\n")
    f.write("          child: const Text('Guardar'),\n")
    f.write("        ),\n")
    f.write("      ],\n")
    f.write("    );\n")
    f.write("  }\n")
    f.write("}\n")


