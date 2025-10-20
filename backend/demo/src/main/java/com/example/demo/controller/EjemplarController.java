package com.example.demo.controller;

import com.example.demo.model.*;
import com.example.demo.services.*;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import java.util.List;
import java.util.Optional;

@RestController
@RequestMapping("/api/ejemplars")
@CrossOrigin(origins = "*")
public class EjemplarController {

    private final EjemplarService ejemplarService;

    public EjemplarController(EjemplarService ejemplarService) {
        this.ejemplarService = ejemplarService;
    }

    @GetMapping
    public List<Ejemplar> getAllEjemplar() {
        return ejemplarService.getAllEjemplar();
    }

    @GetMapping("/{id}")
    public ResponseEntity<Ejemplar> getEjemplarById(@PathVariable Integer id) {
        Optional<Ejemplar> ejemplar = ejemplarService.getEjemplarById(id);
        return ejemplar.map(ResponseEntity::ok)
                .orElseGet(() -> ResponseEntity.notFound().build());
    }

    @PostMapping
    public Ejemplar createEjemplar(@RequestBody Ejemplar ejemplar) {
        return ejemplarService.createEjemplar(ejemplar);
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteEjemplar(@PathVariable Integer id) {
        ejemplarService.deleteEjemplar(id);
        return ResponseEntity.noContent().build();
    }

    @PutMapping("/{id}")
    public ResponseEntity<Ejemplar> updateEjemplar(
            @PathVariable Integer id,
            @RequestBody Ejemplar ejemplar) {
        Optional<Ejemplar> updatedEjemplar = ejemplarService.updateEjemplar(id, ejemplar);
        return updatedEjemplar.map(ResponseEntity::ok)
                .orElseGet(() -> ResponseEntity.notFound().build());
    }
}

