package com.example.demo.services;

import com.example.demo.model.*;
import com.example.demo.repository.*;
import org.springframework.beans.BeanUtils;
import org.springframework.stereotype.Service;
import java.util.List;
import java.util.Optional;

@Service
public class CategoriaService {

    private final CategoriaRepository categoriaRepository;

    public CategoriaService(CategoriaRepository categoriaRepository) {
        this.categoriaRepository = categoriaRepository;
    }

    public List<Categoria> getAllCategoria() {
        return categoriaRepository.findAll();
    }

    public Optional<Categoria> getCategoriaById(Integer id) {
        return categoriaRepository.findById(id);
    }

    public Categoria createCategoria(Categoria categoria) {
        return categoriaRepository.save(categoria);
    }

    public void deleteCategoria(Integer id) {
        categoriaRepository.deleteById(id);
    }

    public Optional<Categoria> updateCategoria(Integer id, Categoria categoria) {
        return categoriaRepository.findById(id)
            .map(existing -> {
                BeanUtils.copyProperties(categoria, existing, "id");
                return categoriaRepository.save(existing);
            });
    }
}

