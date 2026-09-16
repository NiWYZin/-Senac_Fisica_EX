"""Modelo físico do lançamento de objetos."""

import math
from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class ParametrosLancamento:
    """Valores de entrada de um lançamento de objeto."""

    velocidade: float
    angulo: float
    altura: float
    gravidade: float

    def validar(self):
        """Valida os intervalos aceitos pela aplicação."""
        if not (5 <= self.velocidade <= 150):
            raise ValueError("A velocidade deve estar entre 5 e 150 m/s.")
        if not (1 < self.angulo < 90):
            raise ValueError("O ângulo deve estar entre 1° e 89°.")
        if not (0 <= self.altura <= 50):
            raise ValueError("A altura inicial deve estar entre 0 e 50 m.")
        if not (1.6 <= self.gravidade <= 24.8):
            raise ValueError("A gravidade deve estar entre 1,6 e 24,8 m/s².")


@dataclass(frozen=True)
class ResultadoLancamento:
    """Grandezas calculadas para um lançamento."""

    tempo_voo: float
    altura_maxima: float
    alcance: float


class SimuladorProjetil:
    """Aplica o modelo físico do lançamento de um objeto sem resistência do ar."""

    def __init__(self, parametros):
        parametros.validar()
        self.parametros = parametros

    def calcular_resultados(self):
        theta = math.radians(self.parametros.angulo)
        vy0 = self.parametros.velocidade * math.sin(theta)
        vx0 = self.parametros.velocidade * math.cos(theta)

        discriminante = vy0**2 + 2 * self.parametros.gravidade * self.parametros.altura
        tempo_voo = (vy0 + math.sqrt(discriminante)) / self.parametros.gravidade
        altura_maxima = self.parametros.altura + vy0**2 / (2 * self.parametros.gravidade)
        alcance = vx0 * tempo_voo

        return ResultadoLancamento(tempo_voo, altura_maxima, alcance)

    def calcular_trajetoria(self, quantidade_pontos=500):
        theta = math.radians(self.parametros.angulo)
        tempo_voo = self.calcular_resultados().tempo_voo
        tempo = np.linspace(0, tempo_voo, quantidade_pontos)
        x = self.parametros.velocidade * math.cos(theta) * tempo
        y = (
            self.parametros.altura
            + self.parametros.velocidade * math.sin(theta) * tempo
            - 0.5 * self.parametros.gravidade * tempo**2
        )

        return tempo, x, np.maximum(y, 0)

    def calcular_velocidades(self, tempo):
        """Calcula o módulo da velocidade instantânea em cada instante."""
        theta = math.radians(self.parametros.angulo)
        vx = self.parametros.velocidade * math.cos(theta)
        vy = self.parametros.velocidade * math.sin(theta) - self.parametros.gravidade * tempo
        return np.sqrt(vx**2 + vy**2)


def calcular_resultados(v0, theta_graus, y0, g):
    """Mantém a API procedural para código externo existente."""
    simulador = SimuladorProjetil(ParametrosLancamento(v0, theta_graus, y0, g))
    resultado = simulador.calcular_resultados()
    return resultado.tempo_voo, resultado.altura_maxima, resultado.alcance


def calcular_trajetoria(v0, theta_graus, y0, g, n=500):
    """Mantém a API procedural para código externo existente."""
    simulador = SimuladorProjetil(ParametrosLancamento(v0, theta_graus, y0, g))
    return simulador.calcular_trajetoria(n)
