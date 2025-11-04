package com.example.demo.model;

import jakarta.persistence.*;
import java.time.*;
import java.math.BigDecimal;
import java.io.Serializable;
import java.util.Objects;

@Entity
@Table(name = "orden_detalle")
public class Orden_detalle implements Serializable{

    @EmbeddedId
    private Orden_detalleId id;

    @ManyToOne
    @MapsId("ordenid")  // Mapea a la PK compuesta
    @JoinColumn(name = "orden_ordenid", referencedColumnName = "ordenid", nullable = false)
    private Orden orden;

    @ManyToOne
    @MapsId("productoid")  // Mapea a la PK compuesta
    @JoinColumn(name = "producto_productoid", referencedColumnName = "productoid", nullable = false)
    private Producto producto;

    @Embeddable
    public static class Orden_detalleId implements Serializable {
        @Column(name = "orden_ordenid")
        private Integer ordenid;

        @Column(name = "producto_productoid")
        private Integer productoid;

        public Orden_detalleId() {}

        public Orden_detalleId(Integer ordenid, Integer productoid) {
            this.ordenid = ordenid;
            this.productoid = productoid;
        }

        public Integer getOrdenid() { return ordenid; }
        public void setOrdenid(Integer ordenid) { this.ordenid = ordenid; }

        public Integer getProductoid() { return productoid; }
        public void setProductoid(Integer productoid) { this.productoid = productoid; }

        @Override
        public boolean equals(Object o) {
            if (this == o) return true;
            if (o == null || getClass() != o.getClass()) return false;
            Orden_detalleId that = (Orden_detalleId) o;
            return Objects.equals(ordenid, that.ordenid) && Objects.equals(productoid, that.productoid);
        }

        @Override
        public int hashCode() {
            return Objects.hash(ordenid, productoid);
        }
    }

    @Column(name = "cantidad", nullable = false)
    private Integer cantidad;

    public Orden_detalle() {}

    public Orden_detalleId getId() { return id; }
    public void setId(Orden_detalleId id) { this.id = id; }

    public Orden getOrden() { return orden; }
    public void setOrden(Orden orden) { this.orden = orden; }

    public Producto getProducto() { return producto; }
    public void setProducto(Producto producto) { this.producto = producto; }

    public Integer getCantidad() { return cantidad; }
    public void setCantidad(Integer cantidad) { this.cantidad = cantidad; }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        Orden_detalle that = (Orden_detalle) o;
        return Objects.equals(id, that.id);
    }

    @Override
    public int hashCode() {
        return Objects.hash(id);
    }
}

