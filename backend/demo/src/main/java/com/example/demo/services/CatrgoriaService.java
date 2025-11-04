package com.example.demo.services;

import com.example.demo.model.*;
import com.example.demo.repository.*;
import org.springframework.beans.BeanUtils;
import org.springframework.stereotype.Service;
import java.util.List;
import java.util.Optional;

@Service
public class CatrgoriaService {

    private final CatrgoriaRepository catrgoriaRepository;

    public CatrgoriaService(CatrgoriaRepository catrgoriaRepository) {
        this.catrgoriaRepository = catrgoriaRepository;
    }

    public List<Catrgoria> getAllCatrgoria() {
        return catrgoriaRepository.findAll();
    }

    public Optional<Catrgoria> getCatrgoriaById(Integer id) {
        return catrgoriaRepository.findById(id);
    }

    public Catrgoria createCatrgoria(Catrgoria catrgoria) {
        return catrgoriaRepository.save(catrgoria);
    }

    public void deleteCatrgoria(Integer id) {
        catrgoriaRepository.deleteById(id);
    }

    public Optional<Catrgoria> updateCatrgoria(Integer id, Catrgoria catrgoria) {
        return catrgoriaRepository.findById(id)
            .map(existing -> {
                BeanUtils.copyProperties(catrgoria, existing, "id");
                return catrgoriaRepository.save(existing);
            });
    }
}

