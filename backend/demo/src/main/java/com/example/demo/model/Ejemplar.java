package com.example.demo.model;

import jakarta.persistence.*;
import java.time.*;
import java.math.BigDecimal;
import java.io.Serializable;
import java.util.Objects;

@Entity
@Table(name = "Ejemplar")
public class Ejemplar implements Serializable{

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

