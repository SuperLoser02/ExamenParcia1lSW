package com.example.demo.services;

import com.example.demo.model.*;
import com.example.demo.repository.*;
import org.springframework.beans.BeanUtils;
import org.springframework.stereotype.Service;
import java.util.List;
import java.util.Optional;

@Service
public class OrdenService {

    private final OrdenRepository ordenRepository;

    public OrdenService(OrdenRepository ordenRepository) {
        this.ordenRepository = ordenRepository;
    }

    public List<Orden> getAllOrden() {
        return ordenRepository.findAll();
    }

    public Optional<Orden> getOrdenById(Integer id) {
        return ordenRepository.findById(id);
    }

    public Orden createOrden(Orden orden) {
        return ordenRepository.save(orden);
    }

    public void deleteOrden(Integer id) {
        ordenRepository.deleteById(id);
    }

    public Optional<Orden> updateOrden(Integer id, Orden orden) {
        return ordenRepository.findById(id)
            .map(existing -> {
                BeanUtils.copyProperties(orden, existing, "id");
                return ordenRepository.save(existing);
            });
    }
}

