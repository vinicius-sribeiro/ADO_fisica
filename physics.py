"""
physics.py
----------
Modulo de Fisica analitica do simulador de lancamento de projeteis.

Implementa as equacoes analiticas classicas de lancamento de projetil
(trajetoria balistica sem resistencia do ar):

    x(t)   = x0 + v0 * cos(theta) * t
    y(t)   = y0 + v0 * sin(theta) * t - 0.5 * g * t^2
    t_voo  = (v0 * sin(theta) + sqrt((v0 * sin(theta))^2 + 2 * g * y0)) / g
    y_max  = y0 + (v0 * sin(theta))^2 / (2 * g)
    R      = x0 + v0 * cos(theta) * t_voo

Nenhuma integracao numerica (Euler/Verlet) e utilizada para calcular a curva;
todas as posicoes e resultados sao calculados analiticamente.
"""

from dataclasses import dataclass
import math

import config


@dataclass
class ProjectileParameters:
    """Parametros de entrada do lancamento de projetil."""
    v0: float = config.DEFAULT_V0            # velocidade inicial (m/s)
    angle_deg: float = config.DEFAULT_ANGLE  # angulo de lancamento (graus)
    y0: float = config.DEFAULT_Y0            # altura inicial (m)
    g: float = config.DEFAULT_G              # aceleracao da gravidade (m/s^2)
    x0: float = 0.0                          # posicao horizontal inicial (m)

    def copy(self) -> "ProjectileParameters":
        """Retorna uma copia independente dos parametros."""
        return ProjectileParameters(
            v0=self.v0,
            angle_deg=self.angle_deg,
            y0=self.y0,
            g=self.g,
            x0=self.x0,
        )

    def reset(self):
        """Restaura os valores in-place para os padroes de config."""
        self.v0 = config.DEFAULT_V0
        self.angle_deg = config.DEFAULT_ANGLE
        self.y0 = config.DEFAULT_Y0
        self.g = config.DEFAULT_G
        self.x0 = 0.0


@dataclass
class PhysicsResults:
    """Resultados teoricos calculados a partir dos parametros."""
    range_m: float           # Alcance horizontal R (m)
    max_height_m: float      # Altura maxima Ymax (m)
    time_of_flight_s: float  # Tempo total de voo T (s)


def validar_parametros(params: ProjectileParameters) -> tuple[bool, str]:
    """
    Valida se os parametros estao dentro de faixas fisicas seguras.
    Evita divisao por zero, discriminantes negativos e valores fisicamente absurdos.
    """
    if params.g <= 0.0:
        return False, "A aceleracao da gravidade (g) deve ser maior que zero."
    if params.v0 < 0.0:
        return False, "A velocidade inicial (v0) nao pode ser negativa."
    if not (0.0 <= params.angle_deg <= 90.0):
        return False, "O angulo (theta) deve estar entre 0 e 90 graus."
    if params.y0 < 0.0:
        return False, "A altura inicial (y0) nao pode ser negativa."

    return True, "Parametros validos."


def calcular_posicao(t: float, params: ProjectileParameters) -> tuple[float, float]:
    """
    Calcula a posicao (x(t), y(t)) do projetil no instante t (segundos) em metros:
        x(t) = x0 + v0 * cos(theta) * t
        y(t) = y0 + v0 * sin(theta) * t - (1/2) * g * t^2
    """
    if t < 0.0:
        t = 0.0

    theta_rad = math.radians(params.angle_deg)
    vx0 = params.v0 * math.cos(theta_rad)
    vy0 = params.v0 * math.sin(theta_rad)

    x = params.x0 + vx0 * t
    y = params.y0 + vy0 * t - 0.5 * params.g * (t ** 2)

    # Se atingir ou passar abaixo do solo (y <= 0), restringe a y=0
    if y < 0.0:
        y = 0.0

    return (x, y)


def calcular_tempo_voo(params: ProjectileParameters) -> float:
    """
    Calcula o tempo total de voo (t_voo) ate o projetil atingir o solo (y = 0):
        t_voo = (v0 * sin(theta) + sqrt((v0 * sin(theta))^2 + 2 * g * y0)) / g
    """
    if params.g <= 0.0:
        return 0.0

    theta_rad = math.radians(params.angle_deg)
    v_y0 = params.v0 * math.sin(theta_rad)
    discriminant = (v_y0 ** 2) + 2.0 * params.g * params.y0

    if discriminant < 0.0:
        return 0.0

    t_voo = (v_y0 + math.sqrt(discriminant)) / params.g
    return max(0.0, t_voo)


def calcular_altura_maxima(params: ProjectileParameters) -> float:
    """
    Calcula a altura maxima (y_max) alcancada pelo projetil:
        y_max = y0 + (v0 * sin(theta))^2 / (2 * g)
    """
    if params.g <= 0.0:
        return params.y0

    theta_rad = math.radians(params.angle_deg)
    v_y0 = params.v0 * math.sin(theta_rad)
    y_max = params.y0 + (v_y0 ** 2) / (2.0 * params.g)
    return y_max


def calcular_alcance(params: ProjectileParameters) -> float:
    """
    Calcula o alcance horizontal (R):
        R = x0 + v0 * cos(theta) * t_voo
    """
    t_voo = calcular_tempo_voo(params)
    theta_rad = math.radians(params.angle_deg)
    vx0 = params.v0 * math.cos(theta_rad)
    return params.x0 + vx0 * t_voo


def calcular_resultados(params: ProjectileParameters) -> PhysicsResults:
    """
    Calcula e retorna os tres resultados principais de uma so vez:
    alcance (R), altura maxima (Ymax) e tempo de voo (T).
    """
    t_voo = calcular_tempo_voo(params)
    theta_rad = math.radians(params.angle_deg)
    vx0 = params.v0 * math.cos(theta_rad)
    v_y0 = params.v0 * math.sin(theta_rad)

    r = params.x0 + vx0 * t_voo
    y_max = params.y0 + (v_y0 ** 2) / (2.0 * params.g) if params.g > 0 else params.y0

    return PhysicsResults(
        range_m=r,
        max_height_m=y_max,
        time_of_flight_s=t_voo,
    )


def calcular_trajetoria_analitica(
    params: ProjectileParameters, num_pontos: int = 150
) -> list[tuple[float, float]]:
    """
    Calcula analiticamente uma lista de pontos (x, y) em metros que compoem
    a trajetoria completa prevista desde t=0 ate t=t_voo.
    Garante que o ponto final seja exatamente (R, 0).
    """
    t_voo = calcular_tempo_voo(params)
    if t_voo <= 1e-9:
        return [(params.x0, params.y0)]

    points = []
    num_pontos = max(num_pontos, 2)
    dt = t_voo / (num_pontos - 1)

    theta_rad = math.radians(params.angle_deg)
    vx0 = params.v0 * math.cos(theta_rad)
    vy0 = params.v0 * math.sin(theta_rad)

    for i in range(num_pontos):
        t = i * dt
        if i == num_pontos - 1:
            t = t_voo  # precisao exata no instante final
        x = params.x0 + vx0 * t
        y = params.y0 + vy0 * t - 0.5 * params.g * (t ** 2)
        if y < 0.0 or i == num_pontos - 1:
            y = 0.0
        points.append((x, y))

    return points


# -- Aliases de compatibilidade (para compatibilidade com codigo existente) ---
position_at_time = calcular_posicao
calculate_time_of_flight = calcular_tempo_voo
calculate_max_height = calcular_altura_maxima
calculate_range = calcular_alcance
