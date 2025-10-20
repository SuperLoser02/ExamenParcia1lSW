package com.example.demo.controller;

import com.example.demo.model.*;
import com.example.demo.services.*;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import java.util.List;
import java.util.Optional;

@RestController
@RequestMapping("/api/autors")
@CrossOrigin(origins = "*")
public class AutorController {

    private final AutorService autorService;

    public AutorController(AutorService autorService) {
        this.autorService = autorService;
    }

    @GetMapping
    public List<Autor> getAllAutor() {
        return autorService.getAllAutor();
    }

    @GetMapping("/{id}")
    public ResponseEntity<Autor> getAutorById(@PathVariable Integer id) {
        Optional<Autor> autor = autorService.getAutorById(id);
        return autor.map(ResponseEntity::ok)
                .orElseGet(() -> ResponseEntity.notFound().build());
    }

    @PostMapping
    public Autor createAutor(@RequestBody Autor autor) {
        return autorService.createAutor(autor);
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteAutor(@PathVariable Integer id) {
        autorService.deleteAutor(id);
        return ResponseEntity.noContent().build();
    }

    @PutMapping("/{id}")
    public ResponseEntity<Autor> updateAutor(
            @PathVariable Integer id,
            @RequestBody Autor autor) {
        Optional<Autor> updatedAutor = autorService.updateAutor(id, autor);
        return updatedAutor.map(ResponseEntity::ok)
                .orElseGet(() -> ResponseEntity.notFound().build());
    }
}

