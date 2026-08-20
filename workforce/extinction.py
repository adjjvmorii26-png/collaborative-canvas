"""Extinction: cull the weakest fraction of a population."""

from __future__ import annotations


class Extinction:
    @staticmethod
    def cull(population: list, fitness: list) -> dict:
        if not population:
            return {"survivors": [], "extinct": []}
        order = sorted(range(len(population)), key=lambda i: fitness[i])
        k = max(1, len(order) // 3)
        extinct = [population[i] for i in order[:k]]
        survivors = [population[i] for i in order[k:]]
        return {"survivors": survivors, "extinct": extinct}
