package com.example.demo.model;

import jakarta.persistence.*;
import java.time.*;
import java.math.BigDecimal;
import java.io.Serializable;
import java.util.Objects;

@Entity
@Table(name = "catrgoria")
public class Catrgoria implements Serializable{

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "categoriaid", nullable = false)
    private Integer categoriaid;

    public Catrgoria() {}

    public Integer getCategoriaid() { return categoriaid; }
    public void setCategoriaid(Integer categoriaid) { this.categoriaid = categoriaid; }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        Catrgoria that = (Catrgoria) o;
        return Objects.equals(categoriaid, that.categoriaid);
    }

    @Override
    public int hashCode() {
        return Objects.hash(categoriaid);
    }
}

