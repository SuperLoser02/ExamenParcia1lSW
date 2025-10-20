package com.example.demo.services;

import com.example.demo.model.*;
import com.example.demo.repository.*;
import org.springframework.beans.BeanUtils;
import org.springframework.stereotype.Service;
import java.util.List;
import java.util.Optional;

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

