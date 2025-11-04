package com.example.demo.model;

import jakarta.persistence.*;
import java.time.*;
import java.math.BigDecimal;
import java.io.Serializable;
import java.util.Objects;

@Entity
@Table(name = "orden")
public class Orden implements Serializable{

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "ordenid", nullable = false)
    private Integer ordenid;

    @Column(name = "ordenfecha", nullable = false)
    private LocalDateTime ordenfecha;

    @ManyToOne
    @JoinColumn(name = "cliente_clienteid", referencedColumnName = "clienteid", nullable = false)
    private Cliente cliente;

    public Orden() {}

    public Integer getOrdenid() { return ordenid; }
    public void setOrdenid(Integer ordenid) { this.ordenid = ordenid; }

    public LocalDateTime getOrdenfecha() { return ordenfecha; }
    public void setOrdenfecha(LocalDateTime ordenfecha) { this.ordenfecha = ordenfecha; }

    public Cliente getCliente() { return cliente; }
    public void setCliente(Cliente cliente) { this.cliente = cliente; }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        Orden that = (Orden) o;
        return Objects.equals(ordenid, that.ordenid);
    }

    @Override
    public int hashCode() {
        return Objects.hash(ordenid);
    }
}

