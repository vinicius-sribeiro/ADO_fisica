"""
simulation.py
-------------
Controle e estado da simulacao de lancamento de projeteis.

Gerencia:
- O ciclo de vida do lancamento (IDLE, RUNNING, PAUSED, FINISHED).
- O avanco do tempo fisico t.
- O calculo em tempo real da trajetoria prevista para os parametros atuais.
- A preservacao da trajetoria prevista do ultimo lancamento concluido.
- O registro contínuo da trajetoria real percorrida pelo projetil.
- O historico de lancamentos concluidos (historico_trajetorias).
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Tuple

import config
from physics import (
    PhysicsResults,
    ProjectileParameters,
    calcular_alcance,
    calcular_altura_maxima,
    calcular_posicao,
    calcular_resultados,
    calcular_tempo_voo,
    calcular_trajetoria_analitica,
)


class SimulationStatus(Enum):
    IDLE = "idle"          # Pronto para lancamento; projetil na posicao inicial (x0, y0)
    RUNNING = "running"    # Projetil em voo, tempo fisico avancando
    PAUSED = "paused"      # Voo pausado; projetil estatico no instante atual
    FINISHED = "finished"  # Projetil atingiu o solo (t = t_voo); lancamento concluido


@dataclass
class LaunchRecord:
    """Registro historico de um lancamento concluido."""
    params: ProjectileParameters
    actual_points: List[Tuple[float, float]]
    range_m: float
    max_height_m: float
    time_of_flight_s: float


class SimulationState:
    """
    Guarda e coordena o estado completo da simulacao:
    parametros ativos, trajetorias previstas, trajetoria percorrida,
    tempo decorrido e historico de lancamentos.
    """

    def __init__(self):
        # Parametros selecionados na interface
        self.params = ProjectileParameters()

        # Parametros do lancamento em andamento/ativo
        self.active_params = self.params.copy()

        self.status = SimulationStatus.IDLE
        self.current_time = 0.0
        self.has_launched_once = False

        # Trajetoria prevista com base nos parametros atuais da interface
        self.predicted_trajectory_current: List[Tuple[float, float]] = []

        # Trajetoria prevista do ultimo lancamento concluido (preservada)
        self.predicted_trajectory_last: Optional[List[Tuple[float, float]]] = None

        # Trajetoria real percorrida pelo projetil (cresce durante o voo e permanece ao aterrissar)
        self.actual_trajectory_points: List[Tuple[float, float]] = []

        # Resultados calculados para os parametros atuais da interface
        self.current_results: PhysicsResults = calcular_resultados(self.params)

        # Resultados do ultimo lancamento concluido
        self.last_results: Optional[PhysicsResults] = None

        # Historico de todos os lancamentos concluidos
        self.historico_trajetorias: List[LaunchRecord] = []

        # Calcula a trajetoria prevista inicial
        self.recalculate_current_prediction()

    def recalculate_current_prediction(self):
        """
        Recalcula em tempo real a trajetoria analitica prevista e os
        resultados numericos (R, Ymax, T) com base nos parametros atuais.
        """
        self.predicted_trajectory_current = calcular_trajetoria_analitica(self.params)
        self.current_results = calcular_resultados(self.params)

    def on_parameters_changed(self):
        """
        Chamado sempre que o usuario altera qualquer slider de parametro.
        Atualiza as previsoes analiticas em tempo real sem afetar a trajetoria
        do ultimo lancamento concluido.
        """
        self.recalculate_current_prediction()

        if self.status == SimulationStatus.PAUSED:
            # Se pausado, atualiza os parametros do voo em curso e a posicao do projetil em t
            self.active_params = self.params.copy()
            # Regenera a trajetoria percorrida ate o instante atual t com os novos parametros
            self._regenerate_actual_trajectory_up_to(self.current_time)

        elif self.status == SimulationStatus.FINISHED:
            # Se o lancamento anterior ja havia terminado e o usuario mexeu nos parametros,
            # o estado volta para IDLE preparando o proximo lancamento na nova posicao (x0, y0)
            self.status = SimulationStatus.IDLE
            self.current_time = 0.0

    def _regenerate_actual_trajectory_up_to(self, target_t: float, steps: int = 80):
        """Regenera os pontos percorridos ate target_t com base nos parametros ativos."""
        if target_t <= 0:
            self.actual_trajectory_points = [(self.active_params.x0, self.active_params.y0)]
            return

        pts = []
        dt = target_t / max(steps, 1)
        for i in range(steps + 1):
            t = min(i * dt, target_t)
            pts.append(calcular_posicao(t, self.active_params))
        self.actual_trajectory_points = pts

    def launch(self):
        """
        Inicia um novo lancamento com os parametros atuais da interface.
        Inicia o tempo fisico em t = 0.0.
        """
        self.active_params = self.params.copy()
        self.current_time = 0.0
        self.status = SimulationStatus.RUNNING
        self.has_launched_once = True

        # Inicia a trajetoria percorrida no ponto de lancamento (x0, y0)
        self.actual_trajectory_points = [(self.active_params.x0, self.active_params.y0)]

    def toggle_pause(self):
        """Pausa ou retoma a simulacao."""
        if self.status == SimulationStatus.RUNNING:
            self.status = SimulationStatus.PAUSED
        elif self.status == SimulationStatus.PAUSED:
            self.status = SimulationStatus.RUNNING

    def reset_all(self):
        """
        Restaura o estado inicial completo:
        - Interrompe qualquer lancamento ativo;
        - Reseta os parametros para os valores padrao;
        - Remove todas as trajetorias desenhadas;
        - Remove a trajetoria prevista anterior;
        - Limpa o historico de lancamentos;
        - Reseta o relogio para t = 0.0 e status para IDLE.
        """
        self.params.reset()
        self.active_params = self.params.copy()
        self.status = SimulationStatus.IDLE
        self.current_time = 0.0
        self.has_launched_once = False

        self.predicted_trajectory_last = None
        self.actual_trajectory_points.clear()
        self.historico_trajetorias.clear()
        self.last_results = None

        self.recalculate_current_prediction()

    def update(self, dt: float):
        """
        Avanca a simulacao pelo passo de tempo fisico dt (em segundos).
        A posicao do projetil e calculada pelas equacoes analiticas exatas.
        """
        if self.status != SimulationStatus.RUNNING:
            return

        t_voo = calcular_tempo_voo(self.active_params)

        self.current_time += dt

        if self.current_time >= t_voo:
            # O projetil atingiu o solo (y = 0)
            self.current_time = t_voo
            self.status = SimulationStatus.FINISHED

            # Ponto final exato na aterrissagem (R, 0)
            final_pos = calcular_posicao(t_voo, self.active_params)
            self.actual_trajectory_points.append(final_pos)

            # 1. Registra no historico
            res = calcular_resultados(self.active_params)
            record = LaunchRecord(
                params=self.active_params.copy(),
                actual_points=list(self.actual_trajectory_points),
                range_m=res.range_m,
                max_height_m=res.max_height_m,
                time_of_flight_s=res.time_of_flight_s,
            )
            self.historico_trajetorias.append(record)

            # 2. A trajetoria deste lancamento agora se torna a "trajetoria prevista do ultimo lancamento"
            self.predicted_trajectory_last = calcular_trajetoria_analitica(self.active_params)
            self.last_results = res
        else:
            # Em voo: calcula a posicao analitica em t e registra na trajetoria percorrida
            pos = calcular_posicao(self.current_time, self.active_params)
            self.actual_trajectory_points.append(pos)

    def get_projectile_position(self) -> Tuple[float, float]:
        """
        Retorna as coordenadas fisicas (x, y) em metros do projetil no momento:
        - Se IDLE: posicao inicial (x0, y0) dos parametros atuais.
        - Se RUNNING ou PAUSED: posicao em t calculada analiticamente com active_params.
        - Se FINISHED: posicao de impacto no solo (R, 0).
        """
        if self.status == SimulationStatus.IDLE:
            return (self.params.x0, self.params.y0)
        else:
            return calcular_posicao(self.current_time, self.active_params)

