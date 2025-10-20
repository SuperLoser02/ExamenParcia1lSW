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

