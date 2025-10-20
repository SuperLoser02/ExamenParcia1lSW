from diagrama.models import Diagrama, Tabla, Atributo, TIPOS_MYSQL
from relacion.models import Relacion
from collections import defaultdict
from django.shortcuts import get_object_or_404
from primer_parcial.settings import BASE_DIR
from django.http import HttpResponse
import tempfile
import shutil
import os
import zipfile
import base64
import glob
TIPOS_MYSQL_DICT = dict(TIPOS_MYSQL)

def generar_estructura(diagrama_id):
    diagrama = get_object_or_404(Diagrama, id=diagrama_id)
    tablas_qs = list(Tabla.objects.filter(diagrama_id=diagrama))

    # Inicializar estructura con claves por tabla.id (más seguro que nombre)
    estructura = {}
    for tabla in tablas_qs:
        estructura[tabla.id] = {
            "id": tabla.id,
            "nombre": tabla.nombre,
            "pk": [],         # lista de dicts
            "atributos": [],  # lista de dicts (no PK)
            "fk": []          # lista de dicts que apuntan como FK
        }

    # Cargar atributos (serializados a dicts) — evita devolver objetos Django
    atributos_qs = Atributo.objects.filter(tabla_id__in=tablas_qs)
    for atributo in atributos_qs:
        atr = {
            "id": atributo.id,
            "nombre": atributo.nombre,
            "tipo_dato": atributo.tipo_dato,
            "is_nullable": bool(atributo.is_nullable),
            "rango": atributo.rango,
            "primary_key": bool(atributo.primary_key),
            "auto_increment": bool(atributo.auto_increment),
            "solo_positivo": bool(atributo.solo_positivo),
            "atributo_padre": None,  # para FK, se llena luego
            "tabla_padre": None      # para FK, se llena luego
        }
        tabla_id = atributo.tabla_id.id  # recuerda que el FK se llama tabla_id
        if atributo.primary_key:
            estructura[tabla_id]["pk"].append(atr)
        else:
            estructura[tabla_id]["atributos"].append(atr)

    # Procesar relaciones (y almacenar también una lista de relaciones)
    relaciones_qs = Relacion.objects.filter(tabla_origen__in=tablas_qs)
    for relacion in relaciones_qs:
        tipo = relacion.tipo_relacion.lower()
        origen_id = relacion.tabla_origen.id
        destino_id = relacion.tabla_destino.id

        # Usamos copias de los PKs para evitar aliasing (mutaciones compartidas)
        pks_origen = [pk.copy() for pk in estructura[origen_id]["pk"]]

        if tipo == "herencia":
            for pk in pks_origen:
                pk["atributo_padre"] = pk["nombre"]
                pk["nombre"] = f"{estructura[origen_id]['nombre']}_{pk['nombre']}"
                pk["tabla_padre"] = estructura[origen_id]['nombre']
                if pk not in estructura[destino_id]["pk"]:
                    estructura[destino_id]["pk"].append(pk)
                if pk not in estructura[destino_id]["fk"]:
                    estructura[destino_id]["fk"].append(pk)

        elif tipo in ("agregacion", "composicion"):
            for pk in pks_origen:
                pk["atributo_padre"] = pk["nombre"]
                pk["nombre"] = f"{estructura[origen_id]['nombre']}_{pk['nombre']}"
                pk["tabla_padre"] = estructura[origen_id]['nombre']
                if pk not in estructura[destino_id]["atributos"]:
                    estructura[destino_id]["atributos"].append(pk)
                if pk not in estructura[destino_id]["fk"]:
                    estructura[destino_id]["fk"].append(pk)

        elif tipo == "asociacion":
            rel_ori = relacion.cardinalidad_origen or ""
            rel_dest = relacion.cardinalidad_destino or ""

            if "*" in rel_ori and "*" not in rel_dest:
                for pk in pks_origen:
                    pk["atributo_padre"] = pk["nombre"]
                    pk["nombre"] = f"{estructura[origen_id]['nombre']}_{pk['nombre']}"
                    pk["tabla_padre"] = estructura[origen_id]['nombre']
                    if pk not in estructura[origen_id]["atributos"]:
                        estructura[origen_id]["atributos"].append(pk)
                    if pk not in estructura[origen_id]["fk"]:
                        estructura[origen_id]["fk"].append(pk)

            elif "*" in rel_dest and "*" not in rel_ori:
                for pk in pks_origen:
                    pk["atributo_padre"] = pk["nombre"]
                    pk["nombre"] = f"{estructura[origen_id]['nombre']}_{pk['nombre']}"
                    pk["tabla_padre"] = estructura[origen_id]['nombre']
                    if pk not in estructura[destino_id]["atributos"]:
                        estructura[destino_id]["atributos"].append(pk)
                    if pk not in estructura[destino_id]["fk"]:
                        estructura[destino_id]["fk"].append(pk)

            elif "*" in rel_ori and "*" in rel_dest:
                # asociación muchos-a-muchos -> tabla intermedia (tabla_hijo)
                if not relacion.tabla_hijo:
                    # no hay tabla intermedia definida, se ignora o podrías lanzar excepción
                    continue

                inter_id = relacion.tabla_hijo.id
                # Asegurar que la tabla intermedia exista en la estructura
                if inter_id not in estructura:
                    th = relacion.tabla_hijo
                    estructura[inter_id] = {
                        "id": th.id,
                        "nombre": th.nombre,
                        "pk": [],
                        "atributos": [],
                        "fk": []
                    }

                pks_destino = [pk.copy() for pk in estructura[destino_id]["pk"]]
                for pk in (pks_origen + pks_destino):
                    if pk in pks_origen:
                        pk["atributo_padre"] = pk["nombre"]
                        pk["nombre"] = f"{estructura[origen_id]['nombre']}_{pk['nombre']}"
                        pk["tabla_padre"] = estructura[origen_id]['nombre']
                    else:
                        pk["atributo_padre"] = pk["nombre"]
                        pk["nombre"] = f"{estructura[destino_id]['nombre']}_{pk['nombre']}"
                        pk["tabla_padre"] = estructura[destino_id]['nombre']
                    if pk not in estructura[inter_id]["pk"]:
                        estructura[inter_id]["pk"].append(pk)
                    if pk not in estructura[inter_id]["fk"]:
                        estructura[inter_id]["fk"].append(pk)

    # Resultado: dict serializable
    return {
        "diagrama": {"id": diagrama.id, "nombre": diagrama.nombre},
        "tablas": estructura,
    }

def sql(diagrama_id):
    estructura = generar_estructura(diagrama_id)
    sql_script = f"-- Script SQL para el diagrama: {estructura['diagrama']['nombre']}\n\n"
    sql_script += f"CREATE DATABASE IF NOT EXISTS `{estructura['diagrama']['nombre']}`;\n"
    sql_script += f"USE `{estructura['diagrama']['nombre']}`;\n\n"
    
    for tabla_id, tabla in estructura['tablas'].items():
        sql_script += f"CREATE TABLE `{tabla['nombre']}` (\n"
        columnas = []
        
        # Procesar PKs y atributos (sin declarar PRIMARY KEY aún)
        for atributo in tabla['pk'] + tabla['atributos']:
            tipo = TIPOS_MYSQL_DICT.get(atributo['tipo_dato'], "TEXT")
            col = f"  `{atributo['nombre']}` {tipo}"
            
            # Rango
            if atributo.get('rango') and tipo in ['VARCHAR', 'DECIMAL', 'TINYINT']:
                col += f"({atributo['rango']})"
            
            # Unsigned
            if atributo.get('solo_positivo') and tipo in ['INT', 'SMALLINT', 'BIGINT', 'FLOAT', 'DECIMAL']:
                col += " UNSIGNED"
            
            # Nullable
            col += " NULL" if atributo.get('is_nullable') else " NOT NULL"
            
            # Auto increment (solo para PKs enteros)
            if atributo.get('auto_increment') and tipo in ['INT', 'SMALLINT', 'BIGINT']:
                col += " AUTO_INCREMENT"
            
            columnas.append(col)
        
        # Declarar PRIMARY KEY una sola vez
        if tabla['pk']:
            pk_names = ', '.join([f"`{pk['nombre']}`" for pk in tabla['pk']])
            columnas.append(f"  PRIMARY KEY ({pk_names})")
        
        # Declarar FOREIGN KEYs
        for fk in tabla['fk']:
            columnas.append(
                f"  FOREIGN KEY (`{fk['nombre']}`) REFERENCES "
                f"`{fk['tabla_padre']}`(`{fk['atributo_padre']}`)"
            )
        
        sql_script += ',\n'.join(columnas)
        sql_script += "\n);\n\n"
    
    return sql_script

tipo_de_dato_en_java = {
    "integer": "Integer",
    "smallint": "Short",
    "bigint": "Long",
    "float": "Float",
    "decimal": "BigDecimal",
    "char": "String",
    "text": "String",
    "boolean": "Boolean",
    "date": "LocalDate",
    "datetime": "LocalDateTime",
    "time": "LocalTime",
    "json": "String"
}

def spring_boot(diagrama_id):
    base_model = os.path.join(BASE_DIR, "demo/src/main/java/com/example/demo/model")
    base_repo = os.path.join(BASE_DIR, "demo/src/main/java/com/example/demo/repository")
    base_service = os.path.join(BASE_DIR, "demo/src/main/java/com/example/demo/services")
    base_controller = os.path.join(BASE_DIR, "demo/src/main/java/com/example/demo/controller")
    
    for carpeta in [base_model, base_repo, base_service, base_controller]:
        if os.path.exists(carpeta):
            for archivo_java in glob.glob(os.path.join(carpeta, "*.java")):
                os.remove(archivo_java)

    estructura = generar_estructura(diagrama_id)
    
    os.makedirs(base_model, exist_ok=True)
    os.makedirs(base_repo, exist_ok=True)
    os.makedirs(base_service, exist_ok=True)
    os.makedirs(base_controller, exist_ok=True)

    for tabla_id, tabla in estructura['tablas'].items():
        nombre_clase = tabla['nombre'].capitalize()
        archivo = os.path.join(base_model, f"{nombre_clase}.java")
        
    # ==================== MODELOS ====================
        with open(archivo, "w", encoding="utf-8") as f:
            f.write("package com.example.demo.model;\n\n")
            f.write("import jakarta.persistence.*;\n") #Este se modifico
            f.write("import java.time.*;\n")
            f.write("import java.math.BigDecimal;\n")
            f.write("import java.io.Serializable;\n")
            f.write("import java.util.Objects;\n\n")
            
            
            f.write(f"@Entity\n")
            f.write(f"@Table(name = \"{tabla['nombre']}\")\n")
            f.write(f"public class {nombre_clase} implements Serializable" + "{\n\n")
            # Variables para manejar PKs compuestas
            tiene_pk_compuesta = len(tabla['pk']) > 1
            tiene_pk_simple = len(tabla['pk']) == 1
            tiene_auto_increment = any(pk.get('auto_increment') for pk in tabla['pk'])

            # ==== CASO 1: PK Compuesta ====
            if tiene_pk_compuesta:
                f.write("    @EmbeddedId\n")
                f.write(f"    private {nombre_clase}Id id;\n\n")
                
                # Generar clase interna para PK compuesta
                f.write("    @Embeddable\n")
                f.write(f"    public static class {nombre_clase}Id implements Serializable " + "{\n")
                for pk in tabla['pk']:
                    tipo_java = tipo_de_dato_en_java.get(pk['tipo_dato'], 'String')
                    f.write(f"        @Column(name = \"{pk['nombre']}\")\n")
                    f.write(f"        private {tipo_java} {pk['nombre'].lower()};\n\n")
                
                # Constructor vacío
                f.write(f"        public {nombre_clase}Id() " + "{}\n\n")
                
                # Constructor con parámetros
                params = ', '.join([f"{tipo_de_dato_en_java.get(pk['tipo_dato'], 'String')} {pk['nombre'].lower()}" for pk in tabla['pk']])
                f.write(f"        public {nombre_clase}Id({params}) " + "{\n")
                for pk in tabla['pk']:
                    f.write(f"            this.{pk['nombre'].lower()} = {pk['nombre'].lower()};\n")
                f.write("        }\n\n")
                
                # Getters y setters para PK compuesta
                for pk in tabla['pk']:
                    tipo_java = tipo_de_dato_en_java.get(pk['tipo_dato'], 'String')
                    nombre_campo = pk['nombre'].lower()
                    nombre_metodo = nombre_campo.capitalize()
                    f.write(f"        public {tipo_java} get{nombre_metodo}() {{ return {nombre_campo}; }}\n")
                    f.write(f"        public void set{nombre_metodo}({tipo_java} {nombre_campo}) {{ this.{nombre_campo} = {nombre_campo}; }}\n\n")
                
                # equals y hashCode
                f.write("        @Override\n")
                f.write("        public boolean equals(Object o) {\n")
                f.write(f"            if (this == o) return true;\n")
                f.write(f"            if (o == null || getClass() != o.getClass()) return false;\n")
                f.write(f"            {nombre_clase}Id that = ({nombre_clase}Id) o;\n")
                equals_conditions = ' && '.join([f"Objects.equals({pk['nombre'].lower()}, that.{pk['nombre'].lower()})" for pk in tabla['pk']])
                f.write(f"            return {equals_conditions};\n")
                f.write("        }\n\n")
                
                f.write("        @Override\n")
                f.write("        public int hashCode() {\n")
                hash_fields = ', '.join([pk['nombre'].lower() for pk in tabla['pk']])
                f.write(f"            return Objects.hash({hash_fields});\n")
                f.write("        }\n")
                f.write("    }\n\n")

            # ==== CASO 2: PK Simple ====
            elif tiene_pk_simple:
                pk = tabla['pk'][0]
                tipo_java = tipo_de_dato_en_java.get(pk['tipo_dato'], 'Integer')
                
                f.write("    @Id\n")
                if pk.get('auto_increment'):
                    f.write("    @GeneratedValue(strategy = GenerationType.IDENTITY)\n")
                f.write(f"    @Column(name = \"{pk['nombre']}\", nullable = false)\n")
                f.write(f"    private {tipo_java} {pk['nombre'].lower()};\n\n")

            # ==== CASO 3: Sin PK (tabla intermedia sin PK explícita) ====
            else:
                f.write("    @Id\n")
                f.write("    @GeneratedValue(strategy = GenerationType.IDENTITY)\n")
                f.write("    private Long id;\n\n")

            # ==== ATRIBUTOS NO-PK ====
            for atributo in tabla['atributos']:
                es_fk = atributo.get('tabla_padre') is not None
                tipo_java = tipo_de_dato_en_java.get(atributo['tipo_dato'], 'String')

                if es_fk:
                    # Es una FK - relación ManyToOne
                    tabla_padre_nombre = atributo['tabla_padre'].capitalize()
                    f.write("    @ManyToOne\n")
                    f.write(f"    @JoinColumn(name = \"{atributo['nombre']}\", ")
                    f.write(f"referencedColumnName = \"{atributo['atributo_padre']}\", ")
                    f.write(f"nullable = {str(atributo.get('is_nullable', False)).lower()})\n")
                    f.write(f"    private {tabla_padre_nombre} {atributo['nombre'].lower().replace('_', '')};\n\n")
                else:
                    # Columna normal
                    columnas = [f"name = \"{atributo['nombre']}\""]
                    columnas.append(f"nullable = {str(atributo.get('is_nullable', False)).lower()}")
                    
                    if tipo_java == "String" and atributo.get('rango'):
                        columnas.append(f"length = {atributo['rango']}")
                    
                    if tipo_java == "BigDecimal" and atributo.get('rango'):
                        try:
                            precision, scale = atributo['rango'].split(',')
                            columnas.append(f"precision = {precision.strip()}, scale = {scale.strip()}")
                        except:
                            pass
                    
                    f.write(f"    @Column({', '.join(columnas)})\n")
                    f.write(f"    private {tipo_java} {atributo['nombre'].lower()};\n\n")

            # ==== CONSTRUCTOR VACÍO ====
            f.write(f"    public {nombre_clase}() " + "{}\n\n")

            # ==== GETTERS Y SETTERS ====
            # Para PK
            if tiene_pk_compuesta:
                f.write(f"    public {nombre_clase}Id getId() {{ return id; }}\n")
                f.write(f"    public void setId({nombre_clase}Id id) {{ this.id = id; }}\n\n")
            elif tiene_pk_simple:
                pk = tabla['pk'][0]
                tipo_java = tipo_de_dato_en_java.get(pk['tipo_dato'], 'Integer')
                nombre_campo = pk['nombre'].lower()
                nombre_metodo = nombre_campo.capitalize()
                f.write(f"    public {tipo_java} get{nombre_metodo}() {{ return {nombre_campo}; }}\n")
                f.write(f"    public void set{nombre_metodo}({tipo_java} {nombre_campo}) {{ this.{nombre_campo} = {nombre_campo}; }}\n\n")
            else:
                f.write("    public Long getId() { return id; }\n")
                f.write("    public void setId(Long id) { this.id = id; }\n\n")

            # Para atributos
            for atributo in tabla['atributos']:
                es_fk = atributo.get('tabla_padre') is not None
                
                if es_fk:
                    tabla_padre_nombre = atributo['tabla_padre'].capitalize()
                    nombre_campo = atributo['nombre'].lower().replace('_', '')
                    nombre_metodo = nombre_campo.capitalize()
                    f.write(f"    public {tabla_padre_nombre} get{nombre_metodo}() {{ return {nombre_campo}; }}\n")
                    f.write(f"    public void set{nombre_metodo}({tabla_padre_nombre} {nombre_campo}) {{ this.{nombre_campo} = {nombre_campo}; }}\n\n")
                else:
                    tipo_java = tipo_de_dato_en_java.get(atributo['tipo_dato'], 'String')
                    nombre_campo = atributo['nombre'].lower()
                    nombre_metodo = nombre_campo.capitalize()
                    f.write(f"    public {tipo_java} get{nombre_metodo}() {{ return {nombre_campo}; }}\n")
                    f.write(f"    public void set{nombre_metodo}({tipo_java} {nombre_campo}) {{ this.{nombre_campo} = {nombre_campo}; }}\n\n")

            # ==== EQUALS Y HASHCODE ====
            f.write("    @Override\n")
            f.write("    public boolean equals(Object o) {\n")
            f.write("        if (this == o) return true;\n")
            f.write("        if (o == null || getClass() != o.getClass()) return false;\n")
            f.write(f"        {nombre_clase} that = ({nombre_clase}) o;\n")
            
            if tiene_pk_compuesta:
                f.write("        return Objects.equals(id, that.id);\n")
            elif tiene_pk_simple:
                pk_nombre = tabla['pk'][0]['nombre'].lower()
                f.write(f"        return Objects.equals({pk_nombre}, that.{pk_nombre});\n")
            else:
                f.write("        return Objects.equals(id, that.id);\n")
            
            f.write("    }\n\n")
            
            f.write("    @Override\n")
            f.write("    public int hashCode() {\n")
            if tiene_pk_compuesta:
                f.write("        return Objects.hash(id);\n")
            elif tiene_pk_simple:
                pk_nombre = tabla['pk'][0]['nombre'].lower()
                f.write(f"        return Objects.hash({pk_nombre});\n")
            else:
                f.write("        return Objects.hash(id);\n")
            f.write("    }\n")
            
            f.write("}\n\n")

    # ==================== REPOSITORIOS ====================
    for tabla_id, tabla in estructura['tablas'].items():
        nombre_clase = tabla['nombre'].capitalize()
        archivo = os.path.join(base_repo, f"{nombre_clase}Repository.java")    
        with open(archivo, "w", encoding="utf-8") as f:
            f.write("package com.example.demo.repository;\n\n")
            f.write("import org.springframework.data.jpa.repository.JpaRepository;\n")
            f.write("import org.springframework.stereotype.Repository;\n")
            f.write("import com.example.demo.model.*;\n\n")
            
            # Determinar tipo de ID
            if len(tabla['pk']) > 1:
                tipo_id = f"{nombre_clase}Id"
            elif len(tabla['pk']) == 1:
                tipo_id = tipo_de_dato_en_java.get(tabla['pk'][0]['tipo_dato'], 'Integer')
            else:
                tipo_id = "Long"
            
            f.write("@Repository\n")
            f.write(f"public interface {nombre_clase}Repository extends JpaRepository<{nombre_clase}, {tipo_id}> " + "{\n")
            f.write("}\n\n")

    # ==================== SERVICIOS ====================
    for tabla_id, tabla in estructura['tablas'].items():
        nombre_clase = tabla['nombre'].capitalize()
        archivo = os.path.join(base_service, f"{nombre_clase}Service.java")
        nombre_var = nombre_clase.lower()
        with open(archivo, "w", encoding="utf-8") as f:
            f.write("package com.example.demo.services;\n\n")
            f.write("import com.example.demo.model.*;\n")
            f.write("import com.example.demo.repository.*;\n")
            f.write("import org.springframework.beans.BeanUtils;\n")
            f.write("import org.springframework.stereotype.Service;\n")
            f.write("import java.util.List;\n")
            f.write("import java.util.Optional;\n\n")
            
            # Determinar tipo de ID
            if len(tabla['pk']) > 1:
                tipo_id = f"{nombre_clase}.{nombre_clase}Id"
            elif len(tabla['pk']) == 1:
                tipo_id = tipo_de_dato_en_java.get(tabla['pk'][0]['tipo_dato'], 'Integer')
            else:
                tipo_id = "Long"
            
            f.write("@Service\n")
            f.write(f"public class {nombre_clase}Service " + "{\n\n")
            f.write(f"    private final {nombre_clase}Repository {nombre_var}Repository;\n\n")
            f.write(f"    public {nombre_clase}Service({nombre_clase}Repository {nombre_var}Repository) " + "{\n")
            f.write(f"        this.{nombre_var}Repository = {nombre_var}Repository;\n")
            f.write("    }\n\n")
            
            # GetAll
            f.write(f"    public List<{nombre_clase}> getAll{nombre_clase}() " + "{\n")
            f.write(f"        return {nombre_var}Repository.findAll();\n")
            f.write("    }\n\n")
            
            # GetById
            f.write(f"    public Optional<{nombre_clase}> get{nombre_clase}ById({tipo_id} id) " + "{\n")
            f.write(f"        return {nombre_var}Repository.findById(id);\n")
            f.write("    }\n\n")
            
            # Create
            f.write(f"    public {nombre_clase} create{nombre_clase}({nombre_clase} {nombre_var}) " + "{\n")
            f.write(f"        return {nombre_var}Repository.save({nombre_var});\n")
            f.write("    }\n\n")
            
            # Delete
            f.write(f"    public void delete{nombre_clase}({tipo_id} id) " + "{\n")
            f.write(f"        {nombre_var}Repository.deleteById(id);\n")
            f.write("    }\n\n")
            
            # Update
            f.write(f"    public Optional<{nombre_clase}> update{nombre_clase}({tipo_id} id, {nombre_clase} {nombre_var}) " + "{\n")
            f.write(f"        return {nombre_var}Repository.findById(id)\n")
            f.write("            .map(existing -> {\n")
            f.write(f"                BeanUtils.copyProperties({nombre_var}, existing, \"id\");\n")
            f.write(f"                return {nombre_var}Repository.save(existing);\n")
            f.write("            });\n")
            f.write("    }\n")
            f.write("}\n\n")

    # ==================== CONTROLADORES ====================
    for tabla_id, tabla in estructura['tablas'].items():
        nombre_clase = tabla['nombre'].capitalize()
        nombre_var = nombre_clase.lower()
        archivo = os.path.join(base_controller, f"{nombre_clase}Controller.java")
        with open(archivo, "w", encoding="utf-8") as f:
            f.write("package com.example.demo.controller;\n\n")
            f.write("import com.example.demo.model.*;\n")
            f.write("import com.example.demo.services.*;\n")
            f.write("import org.springframework.http.ResponseEntity;\n")
            f.write("import org.springframework.web.bind.annotation.*;\n")
            f.write("import java.util.List;\n")
            f.write("import java.util.Optional;\n\n")
            
            # Determinar tipo de ID
            if len(tabla['pk']) > 1:
                tipo_id = f"{nombre_clase}.{nombre_clase}Id"
            elif len(tabla['pk']) == 1:
                tipo_id = tipo_de_dato_en_java.get(tabla['pk'][0]['tipo_dato'], 'Integer')
            else:
                tipo_id = "Long"
            
            f.write("@RestController\n")
            f.write(f"@RequestMapping(\"/api/{nombre_var}s\")\n")
            f.write(f"@CrossOrigin(origins = \"*\")\n")
            f.write(f"public class {nombre_clase}Controller " + "{\n\n")
            f.write(f"    private final {nombre_clase}Service {nombre_var}Service;\n\n")
            f.write(f"    public {nombre_clase}Controller({nombre_clase}Service {nombre_var}Service) " + "{\n")
            f.write(f"        this.{nombre_var}Service = {nombre_var}Service;\n")
            f.write("    }\n\n")

            # GET all
            f.write("    @GetMapping\n")
            f.write(f"    public List<{nombre_clase}> getAll{nombre_clase}() " + "{\n")
            f.write(f"        return {nombre_var}Service.getAll{nombre_clase}();\n")
            f.write("    }\n\n")
            
            # GET by ID
            f.write("    @GetMapping(\"/{id}\")\n")
            f.write(f"    public ResponseEntity<{nombre_clase}> get{nombre_clase}ById(@PathVariable {tipo_id} id) " + "{\n")
            f.write(f"        Optional<{nombre_clase}> {nombre_var} = {nombre_var}Service.get{nombre_clase}ById(id);\n")
            f.write(f"        return {nombre_var}.map(ResponseEntity::ok)\n")
            f.write("                .orElseGet(() -> ResponseEntity.notFound().build());\n")
            f.write("    }\n\n")
            
            # POST create
            f.write("    @PostMapping\n")
            f.write(f"    public {nombre_clase} create{nombre_clase}(@RequestBody {nombre_clase} {nombre_var}) " + "{\n")
            f.write(f"        return {nombre_var}Service.create{nombre_clase}({nombre_var});\n")
            f.write("    }\n\n")
            
            # DELETE by ID
            f.write("    @DeleteMapping(\"/{id}\")\n")
            f.write(f"    public ResponseEntity<Void> delete{nombre_clase}(@PathVariable {tipo_id} id) " + "{\n")
            f.write(f"        {nombre_var}Service.delete{nombre_clase}(id);\n")
            f.write("        return ResponseEntity.noContent().build();\n")
            f.write("    }\n\n")

            # PUT update
            f.write("    @PutMapping(\"/{id}\")\n")
            f.write(f"    public ResponseEntity<{nombre_clase}> update{nombre_clase}(\n")
            f.write(f"            @PathVariable {tipo_id} id,\n")
            f.write(f"            @RequestBody {nombre_clase} {nombre_var}) " + "{\n")
            f.write(f"        Optional<{nombre_clase}> updated{nombre_clase} = {nombre_var}Service.update{nombre_clase}(id, {nombre_var});\n")
            f.write(f"        return updated{nombre_clase}.map(ResponseEntity::ok)\n")
            f.write("                .orElseGet(() -> ResponseEntity.notFound().build());\n")
            f.write("    }\n")
            f.write("}\n\n")
    f.close()
    
 # ==================== CREAR ZIP ====================
    # Ruta a tu carpeta demo original (la que descargaste de Spring Initializr)
    DEMO_ORIGINAL = os.path.join(BASE_DIR, "demo")
    
    # Crear directorio temporal
    temp_dir = tempfile.mkdtemp()
    demo_copy = os.path.join(temp_dir, "demo")
    
    try:
        # Copiar proyecto
        shutil.copytree(DEMO_ORIGINAL, demo_copy)
        
        # Crear ZIP
        zip_filename = f"{estructura['diagrama']['nombre']}_springboot.zip"
        zip_path = os.path.join(temp_dir, zip_filename)
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(demo_copy):
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