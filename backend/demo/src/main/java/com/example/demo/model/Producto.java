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

    @Column(name = "productonombre", nullable = false, length = 100)
    private String productonombre;

    @Column(name = "precio", nullable = false, precision = 10, scale = 2)
    private BigDecimal precio;

    @ManyToOne
    @JoinColumn(name = "catrgoria_categoriaid", referencedColumnName = "categoriaid", nullable = false)
    private Catrgoria catrgoria;

    public Producto() {}

    public Integer getProductoid() { return productoid; }
    public void setProductoid(Integer productoid) { this.productoid = productoid; }

    public String getProductonombre() { return productonombre; }
    public void setProductonombre(String productonombre) { this.productonombre = productonombre; }

    public BigDecimal getPrecio() { return precio; }
    public void setPrecio(BigDecimal precio) { this.precio = precio; }

    public Catrgoria getCatrgoria() { return catrgoria; }
    public void setCatrgoria(Catrgoria catrgoria) { this.catrgoria = catrgoria; }

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

