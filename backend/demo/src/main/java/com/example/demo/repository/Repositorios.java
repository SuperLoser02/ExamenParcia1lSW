package com.example.demo.repository;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;
import com.example.demo.model.*;

@Repository
public interface AutorRepository extends JpaRepository<Autor, Integer> {
}

@Repository
public interface LibroRepository extends JpaRepository<Libro, String> {
}

@Repository
public interface EjemplarRepository extends JpaRepository<Ejemplar, Integer> {
}

