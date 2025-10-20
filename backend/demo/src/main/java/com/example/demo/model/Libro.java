package com.example.demo.model;

import jakarta.persistence.*;
import java.time.*;
import java.math.BigDecimal;
import java.io.Serializable;
import java.util.Objects;

@Entity
@Table(name = "Libro")
public class Libro implements Serializable{

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

