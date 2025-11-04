package com.example.demo.controller;

import com.example.demo.model.*;
import com.example.demo.services.*;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import java.util.List;
import java.util.Optional;

@RestController
@RequestMapping("/api/orden_detalles")
@CrossOrigin(origins = "*")
public class Orden_detalleController {

    private final Orden_detalleService orden_detalleService;

    public Orden_detalleController(Orden_detalleService orden_detalleService) {
        this.orden_detalleService = orden_detalleService;
    }

    @GetMapping
    public List<Orden_detalle> getAllOrden_detalle() {
        return orden_detalleService.getAllOrden_detalle();
    }

    @GetMapping("/{ordenid}/{productoid}")
    public ResponseEntity<Orden_detalle> getOrden_detalleById(@PathVariable Integer ordenid, @PathVariable Integer productoid) {
        Orden_detalle.Orden_detalleId id = new Orden_detalle.Orden_detalleId(ordenid, productoid);
        Optional<Orden_detalle> orden_detalle = orden_detalleService.getOrden_detalleById(id);
        return orden_detalle.map(ResponseEntity::ok)
                .orElseGet(() -> ResponseEntity.notFound().build());
    }

    @PostMapping
    public Orden_detalle createOrden_detalle(@RequestBody Orden_detalle orden_detalle) {
        return orden_detalleService.createOrden_detalle(orden_detalle);
    }

    @DeleteMapping("/{ordenid}/{productoid}")
    public ResponseEntity<Void> deleteOrden_detalle(@PathVariable Integer ordenid, @PathVariable Integer productoid) {
        Orden_detalle.Orden_detalleId id = new Orden_detalle.Orden_detalleId(ordenid, productoid);
        orden_detalleService.deleteOrden_detalle(id);
        return ResponseEntity.noContent().build();
    }

    @PutMapping("/{ordenid}/{productoid}")
    public ResponseEntity<Orden_detalle> updateOrden_detalle(
            @PathVariable Integer ordenid, @PathVariable Integer productoid,
            @RequestBody Orden_detalle orden_detalle) {
        Orden_detalle.Orden_detalleId id = new Orden_detalle.Orden_detalleId(ordenid, productoid);
        Optional<Orden_detalle> updatedOrden_detalle = orden_detalleService.updateOrden_detalle(id, orden_detalle);
        return updatedOrden_detalle.map(ResponseEntity::ok)
                .orElseGet(() -> ResponseEntity.notFound().build());
    }
}

