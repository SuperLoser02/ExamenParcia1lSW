package com.example.demo.model;

import jakarta.persistence.*;
import java.time.*;
import java.math.BigDecimal;
import java.io.Serializable;
import java.util.Objects;

@Entity
@Table(name = "producto")
public class Producto implements Serializable{

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "productoid", nullable = false)
    private Integer productoid;

    @Column(name = "nombreproducto", nullable = false, length = 100)
    private String nombreproducto;

    @ManyToOne
    @JoinColumn(name = "categoria_categoriaid", referencedColumnName = "categoriaid", nullable = false)
    private Categoria categoria;

    public Producto() {}

    public Integer getProductoid() { return productoid; }
    public void setProductoid(Integer productoid) { this.productoid = productoid; }

    public String getNombreproducto() { return nombreproducto; }
    public void setNombreproducto(String nombreproducto) { this.nombreproducto = nombreproducto; }

    public Categoria getCategoria() { return categoria; }
    public void setCategoria(Categoria categoria) { this.categoria = categoria; }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        Producto that = (Producto) o;
        return Objects.equals(productoid, that.productoid);
    }

    @Override
    public int hashCode() {
        return Objects.hash(productoid);
    }
}

