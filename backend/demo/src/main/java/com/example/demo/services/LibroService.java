package com.example.demo.services;

import com.example.demo.model.*;
import com.example.demo.repository.*;
import org.springframework.beans.BeanUtils;
import org.springframework.stereotype.Service;
import java.util.List;
import java.util.Optional;

@Service
public class LibroService {

    private final LibroRepository libroRepository;

    public LibroService(LibroRepository libroRepository) {
        this.libroRepository = libroRepository;
    }

    public List<Libro> getAllLibro() {
        return libroRepository.findAll();
    }

    public Optional<Libro> getLibroById(String id) {
        return libroRepository.findById(id);
    }

    public Libro createLibro(Libro libro) {
        return libroRepository.save(libro);
    }

    public void deleteLibro(String id) {
        libroRepository.deleteById(id);
    }

    public Optional<Libro> updateLibro(String id, Libro libro) {
        return libroRepository.findById(id)
            .map(existing -> {
                BeanUtils.copyProperties(libro, existing, "id");
                return libroRepository.save(existing);
            });
    }
}

