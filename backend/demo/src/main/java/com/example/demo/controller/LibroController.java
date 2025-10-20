package com.example.demo.controller;

import com.example.demo.model.*;
import com.example.demo.services.*;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import java.util.List;
import java.util.Optional;

@RestController
@RequestMapping("/api/libros")
@CrossOrigin(origins = "*")
public class LibroController {

    private final LibroService libroService;

    public LibroController(LibroService libroService) {
        this.libroService = libroService;
    }

    @GetMapping
    public List<Libro> getAllLibro() {
        return libroService.getAllLibro();
    }

    @GetMapping("/{id}")
    public ResponseEntity<Libro> getLibroById(@PathVariable String id) {
        Optional<Libro> libro = libroService.getLibroById(id);
        return libro.map(ResponseEntity::ok)
                .orElseGet(() -> ResponseEntity.notFound().build());
    }

    @PostMapping
    public Libro createLibro(@RequestBody Libro libro) {
        return libroService.createLibro(libro);
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteLibro(@PathVariable String id) {
        libroService.deleteLibro(id);
        return ResponseEntity.noContent().build();
    }

    @PutMapping("/{id}")
    public ResponseEntity<Libro> updateLibro(
            @PathVariable String id,
            @RequestBody Libro libro) {
        Optional<Libro> updatedLibro = libroService.updateLibro(id, libro);
        return updatedLibro.map(ResponseEntity::ok)
                .orElseGet(() -> ResponseEntity.notFound().build());
    }
}

