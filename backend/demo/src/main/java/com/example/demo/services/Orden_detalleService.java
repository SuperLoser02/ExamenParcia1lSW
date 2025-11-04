package com.example.demo.services;

import com.example.demo.model.*;
import com.example.demo.repository.*;
import org.springframework.beans.BeanUtils;
import org.springframework.stereotype.Service;
import java.util.List;
import java.util.Optional;

@Service
public class Orden_detalleService {

    private final Orden_detalleRepository orden_detalleRepository;

    public Orden_detalleService(Orden_detalleRepository orden_detalleRepository) {
        this.orden_detalleRepository = orden_detalleRepository;
    }

    public List<Orden_detalle> getAllOrden_detalle() {
        return orden_detalleRepository.findAll();
    }

    public Optional<Orden_detalle> getOrden_detalleById(Orden_detalle.Orden_detalleId id) {
        return orden_detalleRepository.findById(id);
    }

    public Orden_detalle createOrden_detalle(Orden_detalle orden_detalle) {
        return orden_detalleRepository.save(orden_detalle);
    }

    public void deleteOrden_detalle(Orden_detalle.Orden_detalleId id) {
        orden_detalleRepository.deleteById(id);
    }

    public Optional<Orden_detalle> updateOrden_detalle(Orden_detalle.Orden_detalleId id, Orden_detalle orden_detalle) {
        return orden_detalleRepository.findById(id)
            .map(existing -> {
                BeanUtils.copyProperties(orden_detalle, existing, "id");
                return orden_detalleRepository.save(existing);
            });
    }
}

