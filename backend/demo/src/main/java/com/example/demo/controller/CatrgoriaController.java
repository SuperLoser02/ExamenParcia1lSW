package com.example.demo.controller;

import com.example.demo.model.*;
import com.example.demo.services.*;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import java.util.List;
import java.util.Optional;

@RestController
@RequestMapping("/api/catrgorias")
@CrossOrigin(origins = "*")
public class CatrgoriaController {

    private final CatrgoriaService catrgoriaService;

    public CatrgoriaController(CatrgoriaService catrgoriaService) {
        this.catrgoriaService = catrgoriaService;
    }

    @GetMapping
    public List<Catrgoria> getAllCatrgoria() {
        return catrgoriaService.getAllCatrgoria();
    }

    @GetMapping("/{id}")
    public ResponseEntity<Catrgoria> getCatrgoriaById(@PathVariable Integer id) {
        Optional<Catrgoria> catrgoria = catrgoriaService.getCatrgoriaById(id);
        return catrgoria.map(ResponseEntity::ok)
                .orElseGet(() -> ResponseEntity.notFound().build());
    }

    @PostMapping
    public Catrgoria createCatrgoria(@RequestBody Catrgoria catrgoria) {
        return catrgoriaService.createCatrgoria(catrgoria);
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteCatrgoria(@PathVariable Integer id) {
        catrgoriaService.deleteCatrgoria(id);
        return ResponseEntity.noContent().build();
    }

    @PutMapping("/{id}")
    public ResponseEntity<Catrgoria> updateCatrgoria(
            @PathVariable Integer id,
            @RequestBody Catrgoria catrgoria) {
        Optional<Catrgoria> updatedCatrgoria = catrgoriaService.updateCatrgoria(id, catrgoria);
        return updatedCatrgoria.map(ResponseEntity::ok)
                .orElseGet(() -> ResponseEntity.notFound().build());
    }
}

