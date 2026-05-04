import random
import numpy as np
from dataclasses import dataclass
from typing import List, Dict, Any, Callable

@dataclass
class Individual:
    h: float          # Espessura (m)
    fck: float        # Resistência (MPa)
    cost: float = 0.0
    fitness: float = 0.0
    valid: bool = True
    metadata: dict = None

class GeneticOptimizer:
    """
    Motor de Otimização Genética para Engenharia Estrutural (M5-Master).
    Busca o equilíbrio entre Custo e Segurança.
    """
    def __init__(
        self, 
        pop_size: int = 20, 
        generations: int = 10,
        concrete_price_m3: float = 700.0,
        steel_price_kg: float = 12.0,
        formwork_price_m2: float = 80.0
    ):
        self.pop_size = pop_size
        self.generations = generations
        self.prices = {
            'concrete': concrete_price_m3,
            'steel': steel_price_kg,
            'formwork': formwork_price_m2
        }

    def _calculate_cost(self, h: float, fck: float, steel_kg: float, area_m2: float) -> float:
        c_conc = (h * area_m2) * self.prices['concrete']
        c_steel = steel_kg * self.prices['steel']
        c_form = (np.sqrt(area_m2) * 4 * h) * self.prices['formwork'] # Perímetro aproximado
        return c_conc + c_steel + c_form

    def optimize_radier(
        self, 
        area_m2: float, 
        validation_fn: Callable[[float, float], dict]
    ) -> Individual:
        """
        Otimiza um Radier variando h e fck.
        validation_fn: Recebe (h, fck) e retorna {'steel_kg': float, 'valid': bool}
        """
        # População inicial
        population = []
        for _ in range(self.pop_size):
            h = random.choice([0.20, 0.25, 0.30, 0.35, 0.40, 0.50])
            fck = random.choice([25, 30, 35, 40])
            population.append(Individual(h, fck))

        for gen in range(self.generations):
            # Avaliação
            for ind in population:
                result = validation_fn(ind.h, ind.fck)
                ind.valid = result.get('valid', True)
                steel_kg = result.get('steel_kg', 0)
                ind.cost = self._calculate_cost(ind.h, ind.fck, steel_kg, area_m2)
                # Fitness: Inverso do custo, com penalidade pesada se inválido
                ind.fitness = 1.0 / (ind.cost + (0 if ind.valid else 1e9))
                ind.metadata = result

            # Seleção (Torneio)
            population.sort(key=lambda x: x.fitness, reverse=True)
            best_ind = population[0]
            
            new_pop = [best_ind] # Elitismo
            
            while len(new_pop) < self.pop_size:
                # Crossover
                parent1, parent2 = random.sample(population[:10], 2)
                child_h = random.choice([parent1.h, parent2.h])
                child_fck = random.choice([parent1.fck, parent2.fck])
                
                # Mutação (10% chance)
                if random.random() < 0.10:
                    child_h = random.choice([0.20, 0.25, 0.30, 0.35, 0.40, 0.50])
                if random.random() < 0.10:
                    child_fck = random.choice([25, 30, 35, 40])
                    
                new_pop.append(Individual(child_h, child_fck))
            
            population = new_pop
            
        return population[0]

if __name__ == "__main__":
    # Teste rápido
    def dummy_validation(h, fck):
        # Regra fictícia: h >= 0.25 e fck >= 30 é válido
        valid = (h >= 0.25 and fck >= 30)
        # Taxa de aço fictícia (kg/m3) diminui com fck maior
        steel_rate = 120.0 - (fck - 25) * 2.0
        return {'steel_kg': (h * 100) * steel_rate, 'valid': valid}

    opt = GeneticOptimizer(pop_size=10, generations=5)
    best = opt.optimize_radier(area_m2=100.0, validation_fn=dummy_validation)
    print(f"M5-MASTER OPTIMIZER RESULT:")
    print(f"Espessura Ótima: {best.h*100:.0f} cm")
    print(f"FCK Ótimo: {best.fck:.0f} MPa")
    print(f"Custo Total: R$ {best.cost:.2f}")
