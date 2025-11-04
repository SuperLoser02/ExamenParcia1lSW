package com.example.demo.controller;

import com.example.demo.model.*;
import com.example.demo.services.*;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import java.util.List;
import java.util.Optional;

@RestController
@RequestMapping("/api/ordens")
@CrossOrigin(origins = "*")
public class OrdenController {

    private final OrdenService ordenService;

    public OrdenController(OrdenService ordenService) {
        this.ordenService = ordenService;
    }

    @GetMapping
    public List<Orden> getAllOrden() {
        return ordenService.getAllOrden();
    }

    @GetMapping("/{id}")
    public ResponseEntity<Orden> getOrdenById(@PathVariable Integer id) {
        Optional<Orden> orden = ordenService.getOrdenById(id);
        return orden.map(ResponseEntity::ok)
                .orElseGet(() -> ResponseEntity.notFound().build());
    }

    @PostMapping
    public Orden createOrden(@RequestBody Orden orden) {
        return ordenService.createOrden(orden);
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteOrden(@PathVariable Integer id) {
        ordenService.deleteOrden(id);
        return ResponseEntity.noContent().build();
    }

    @PutMapping("/{id}")
    public ResponseEntity<Orden> updateOrden(
            @PathVariable Integer id,
            @RequestBody Orden orden) {
        Optional<Orden> updatedOrden = ordenService.updateOrden(id, orden);
        return updatedOrden.map(ResponseEntity::ok)
                .orElseGet(() -> ResponseEntity.notFound().build());
    }
}

