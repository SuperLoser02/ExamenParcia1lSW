package com.example.demo.controller;

import com.example.demo.model.*;
import com.example.demo.services.*;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import java.util.List;
import java.util.Optional;

@RestController
@RequestMapping("/api/categorias")
@CrossOrigin(origins = "*")
public class CategoriaController {

    private final CategoriaService categoriaService;

    public CategoriaController(CategoriaService categoriaService) {
        this.categoriaService = categoriaService;
    }

    @GetMapping
    public List<Categoria> getAllCategoria() {
        return categoriaService.getAllCategoria();
    }

    @GetMapping("/{id}")
    public ResponseEntity<Categoria> getCategoriaById(@PathVariable Integer id) {
        Optional<Categoria> categoria = categoriaService.getCategoriaById(id);
        return categoria.map(ResponseEntity::ok)
                .orElseGet(() -> ResponseEntity.notFound().build());
    }

    @PostMapping
    public Categoria createCategoria(@RequestBody Categoria categoria) {
        return categoriaService.createCategoria(categoria);
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteCategoria(@PathVariable Integer id) {
        categoriaService.deleteCategoria(id);
        return ResponseEntity.noContent().build();
    }

    @PutMapping("/{id}")
    public ResponseEntity<Categoria> updateCategoria(
            @PathVariable Integer id,
            @RequestBody Categoria categoria) {
        Optional<Categoria> updatedCategoria = categoriaService.updateCategoria(id, categoria);
        return updatedCategoria.map(ResponseEntity::ok)
                .orElseGet(() -> ResponseEntity.notFound().build());
    }
}

