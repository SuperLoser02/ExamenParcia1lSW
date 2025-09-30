package com.example.demo.services;

import com.example.demo.model.*;
import com.example.demo.repository.*;
import org.springframework.beans.BeanUtils;
import org.springframework.stereotype.Service;
import java.util.List;
import java.util.Optional;

@Service
public class AutorService {

    private final AutorRepository autorRepository;

    public AutorService(AutorRepository autorRepository) {
        this.autorRepository = autorRepository;
    }

    public List<Autor> getAllAutor() {
        return autorRepository.findAll();
    }

    public Optional<Autor> getAutorById(Integer id) {
        return autorRepository.findById(id);
    }

    public Autor createAutor(Autor autor) {
        return autorRepository.save(autor);
    }

    public void deleteAutor(Integer id) {
        autorRepository.deleteById(id);
    }

    public Optional<Autor> updateAutor(Integer id, Autor autor) {
        return autorRepository.findById(id)
            .map(existing -> {
                BeanUtils.copyProperties(autor, existing, "id");
                return autorRepository.save(existing);
            });
    }
}

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

@Service
public class EjemplarService {

    private final EjemplarRepository ejemplarRepository;

    public EjemplarService(EjemplarRepository ejemplarRepository) {
        this.ejemplarRepository = ejemplarRepository;
    }

    public List<Ejemplar> getAllEjemplar() {
        return ejemplarRepository.findAll();
    }

    public Optional<Ejemplar> getEjemplarById(Integer id) {
        return ejemplarRepository.findById(id);
    }

    public Ejemplar createEjemplar(Ejemplar ejemplar) {
        return ejemplarRepository.save(ejemplar);
    }

    public void deleteEjemplar(Integer id) {
        ejemplarRepository.deleteById(id);
    }

    public Optional<Ejemplar> updateEjemplar(Integer id, Ejemplar ejemplar) {
        return ejemplarRepository.findById(id)
            .map(existing -> {
                BeanUtils.copyProperties(ejemplar, existing, "id");
                return ejemplarRepository.save(existing);
            });
    }
}

