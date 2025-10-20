package com.example.demo.model;

import jakarta.persistence.*;
import java.time.*;
import java.math.BigDecimal;
import java.io.Serializable;
import java.util.Objects;

@Entity
@Table(name = "Autor")
public class Autor implements Serializable{

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

