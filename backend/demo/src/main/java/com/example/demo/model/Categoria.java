package com.example.demo.model;

import jakarta.persistence.*;
import java.time.*;
import java.math.BigDecimal;
import java.io.Serializable;
import java.util.Objects;

@Entity
@Table(name = "categoria")
public class Categoria implements Serializable{

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "categoriaid", nullable = false)
    private Integer categoriaid;

    @Column(name = "descripcion", nullable = true, length = 255)
    private String descripcion;

    public Categoria() {}

    public Integer getCategoriaid() { return categoriaid; }
    public void setCategoriaid(Integer categoriaid) { this.categoriaid = categoriaid; }

    public String getDescripcion() { return descripcion; }
    public void setDescripcion(String descripcion) { this.descripcion = descripcion; }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        Categoria that = (Categoria) o;
        return Objects.equals(categoriaid, that.categoriaid);
    }

    @Override
    public int hashCode() {
        return Objects.hash(categoriaid);
    }
}

