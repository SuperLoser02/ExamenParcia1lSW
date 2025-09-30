package com.example.demo.model;

import javax.persistence.*;
import java.time.*;
import java.math.BigDecimal;
import java.io.Serializable;
import java.util.Objects;

@Entity
@Table(name = "Autor")
public class Autor implements Serializable {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "id_autor", nullable = false)
    private Integer id_autor;

    @Column(name = "nombre", nullable = false, length = 100)
    private String nombre;

    @Column(name = "nacionalidad", nullable = false, length = 50)
    private String nacionalidad;

    @Column(name = "fecha_nacimiento", nullable = true)
    private LocalDate fecha_nacimiento;

    public Autor() {}

    public Integer getId_autor() { return id_autor; }
    public void setId_autor(Integer id_autor) { this.id_autor = id_autor; }

    public String getNombre() { return nombre; }
    public void setNombre(String nombre) { this.nombre = nombre; }

    public String getNacionalidad() { return nacionalidad; }
    public void setNacionalidad(String nacionalidad) { this.nacionalidad = nacionalidad; }

    public LocalDate getFecha_nacimiento() { return fecha_nacimiento; }
    public void setFecha_nacimiento(LocalDate fecha_nacimiento) { this.fecha_nacimiento = fecha_nacimiento; }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        Autor that = (Autor) o;
        return Objects.equals(id_autor, that.id_autor);
    }

    @Override
    public int hashCode() {
        return Objects.hash(id_autor);
    }
}

@Entity
@Table(name = "Libro")
public class Libro implements Serializable {

    @Id
    @Column(name = "isbn", nullable = false)
    private String isbn;

    @Column(name = "titulo", nullable = false, length = 200)
    private String titulo;

    @Column(name = "anio_publicacion", nullable = false)
    private Integer anio_publicacion;

    @Column(name = "precio", nullable = false, precision = 10, scale = 2)
    private BigDecimal precio;

    @ManyToOne
    @JoinColumn(name = "Autor_id_autor", referencedColumnName = "id_autor", nullable = false)
    private Autor autoridautor;

    public Libro() {}

    public String getIsbn() { return isbn; }
    public void setIsbn(String isbn) { this.isbn = isbn; }

    public String getTitulo() { return titulo; }
    public void setTitulo(String titulo) { this.titulo = titulo; }

    public Integer getAnio_publicacion() { return anio_publicacion; }
    public void setAnio_publicacion(Integer anio_publicacion) { this.anio_publicacion = anio_publicacion; }

    public BigDecimal getPrecio() { return precio; }
    public void setPrecio(BigDecimal precio) { this.precio = precio; }

    public Autor getAutoridautor() { return autoridautor; }
    public void setAutoridautor(Autor autoridautor) { this.autoridautor = autoridautor; }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        Libro that = (Libro) o;
        return Objects.equals(isbn, that.isbn);
    }

    @Override
    public int hashCode() {
        return Objects.hash(isbn);
    }
}

@Entity
@Table(name = "Ejemplar")
public class Ejemplar implements Serializable {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "id_ejemplar", nullable = false)
    private Integer id_ejemplar;

    @Column(name = "estado", nullable = false)
    private Boolean estado;

    @Column(name = "fecha_adquisicion", nullable = false)
    private LocalDate fecha_adquisicion;

    @ManyToOne
    @JoinColumn(name = "Libro_isbn", referencedColumnName = "isbn", nullable = false)
    private Libro libroisbn;

    public Ejemplar() {}

    public Integer getId_ejemplar() { return id_ejemplar; }
    public void setId_ejemplar(Integer id_ejemplar) { this.id_ejemplar = id_ejemplar; }

    public Boolean getEstado() { return estado; }
    public void setEstado(Boolean estado) { this.estado = estado; }

    public LocalDate getFecha_adquisicion() { return fecha_adquisicion; }
    public void setFecha_adquisicion(LocalDate fecha_adquisicion) { this.fecha_adquisicion = fecha_adquisicion; }

    public Libro getLibroisbn() { return libroisbn; }
    public void setLibroisbn(Libro libroisbn) { this.libroisbn = libroisbn; }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        Ejemplar that = (Ejemplar) o;
        return Objects.equals(id_ejemplar, that.id_ejemplar);
    }

    @Override
    public int hashCode() {
        return Objects.hash(id_ejemplar);
    }
}

