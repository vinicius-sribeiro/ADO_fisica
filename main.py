"""
main.py
-------
Ponto de entrada da aplicacao do Simulador de Lancamento de Projetil.

Orquestra os modulos:
    - physics.py     -> calculos analiticos exatos (R, Ymax, T, x(t), y(t))
    - simulation.py  -> ciclo de vida, tempo fisico real, trajetorias e historico
    - ui.py          -> plano cartesiano, botoes de controle, HUD de parametros e resultados
"""

import sys

import pygame

import config
from physics import validar_parametros
from simulation import SimulationState, SimulationStatus
from ui import Button, CartesianPlane, ParametersPanel, ResultsPanel


class App:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption(config.WINDOW_TITLE)

        self.screen = pygame.display.set_mode(
            (config.WINDOW_DEFAULT_WIDTH, config.WINDOW_DEFAULT_HEIGHT),
            pygame.RESIZABLE,
        )
        self.clock = pygame.time.Clock()
        self.running = True

        # Fontes centralizadas
        self.font_small = pygame.font.SysFont(config.FONT_NAME, config.FONT_SIZE_SMALL)
        self.font_normal = pygame.font.SysFont(config.FONT_NAME, config.FONT_SIZE_NORMAL)
        self.font_title = pygame.font.SysFont(config.FONT_NAME, config.FONT_SIZE_TITLE, bold=True)
        self.font_result = pygame.font.SysFont(config.FONT_NAME, config.FONT_SIZE_RESULT, bold=True)

        # Estado da simulacao
        self.simulation_state = SimulationState()

        # Componentes de interface
        self.plane = CartesianPlane(self._plane_rect())

        self.toggle_button = Button(
            self._toggle_button_rect(),
            "Parametros",
            self.font_normal,
            on_click=self._toggle_panel,
        )

        self.parameters_panel = ParametersPanel(
            self._panel_rect(),
            self.font_small,
            self.font_title,
            self.simulation_state.params,
            on_param_change=self._on_param_change,
        )

        self.results_panel = ResultsPanel(
            self._results_rect(),
            self.font_small,
            self.font_result,
        )

        # Botoes de controle (Lancar, Pausar/Continuar, Resetar tudo)
        self.launch_button = Button(
            self._launch_button_rect(),
            "Lancar",
            self.font_normal,
            on_click=self._on_launch_click,
            style="launch",
        )

        self.pause_button = Button(
            self._pause_button_rect(),
            "Pausar",
            self.font_normal,
            on_click=self._on_pause_click,
            style="pause",
        )

        self.reset_button = Button(
            self._reset_button_rect(),
            "Resetar tudo",
            self.font_normal,
            on_click=self._on_reset_click,
            style="reset",
        )

    # ------------------------------------------------------------------
    # Calculo de layout responsivo
    # ------------------------------------------------------------------
    def _plane_rect(self):
        w, h = self.screen.get_size()
        return pygame.Rect(0, 0, w, h)

    def _toggle_button_rect(self):
        w, _ = self.screen.get_size()
        return pygame.Rect(
            w - config.TOGGLE_BUTTON_WIDTH - config.TOGGLE_BUTTON_MARGIN,
            config.TOGGLE_BUTTON_MARGIN,
            config.TOGGLE_BUTTON_WIDTH,
            config.TOGGLE_BUTTON_HEIGHT,
        )

    def _panel_rect(self):
        w, h = self.screen.get_size()
        available = h - config.PANEL_TOP_MARGIN - config.PANEL_RIGHT_MARGIN
        panel_height = min(available, config.PANEL_MAX_HEIGHT)
        return pygame.Rect(
            w - config.PANEL_WIDTH - config.PANEL_RIGHT_MARGIN,
            config.PANEL_TOP_MARGIN,
            config.PANEL_WIDTH,
            panel_height,
        )

    def _results_rect(self):
        return pygame.Rect(
            config.RESULTS_PANEL_MARGIN,
            config.RESULTS_PANEL_MARGIN,
            config.RESULTS_PANEL_WIDTH,
            config.RESULTS_PANEL_HEIGHT,
        )

    def _launch_button_rect(self):
        w, h = self.screen.get_size()
        bw = 135
        bh = config.LAUNCH_BUTTON_HEIGHT
        m = config.LAUNCH_BUTTON_MARGIN
        return pygame.Rect(w - bw - m, h - bh - m, bw, bh)

    def _pause_button_rect(self):
        w, h = self.screen.get_size()
        bw = 120
        bh = config.LAUNCH_BUTTON_HEIGHT
        m = config.LAUNCH_BUTTON_MARGIN
        launch_bw = 135
        sp = config.CONTROL_BUTTON_SPACING
        return pygame.Rect(w - bw - launch_bw - m - sp, h - bh - m, bw, bh)

    def _reset_button_rect(self):
        w, h = self.screen.get_size()
        bw = 135
        bh = config.LAUNCH_BUTTON_HEIGHT
        m = config.LAUNCH_BUTTON_MARGIN
        launch_bw = 135
        pause_bw = 120
        sp = config.CONTROL_BUTTON_SPACING
        return pygame.Rect(w - bw - pause_bw - launch_bw - m - 2 * sp, h - bh - m, bw, bh)

    def _recompute_layout(self):
        self.plane.resize(self._plane_rect())
        self.toggle_button.rect = self._toggle_button_rect()
        self.parameters_panel.resize(self._panel_rect())
        self.results_panel.rect = self._results_rect()
        self.launch_button.rect = self._launch_button_rect()
        self.pause_button.rect = self._pause_button_rect()
        self.reset_button.rect = self._reset_button_rect()

    # ------------------------------------------------------------------
    # Acoes e Callbacks
    # ------------------------------------------------------------------
    def _toggle_panel(self):
        self.parameters_panel.toggle()

    def _on_param_change(self):
        """Notificado em tempo real sempre que qualquer parametro e alterado."""
        valid, _ = validar_parametros(self.simulation_state.params)
        if valid:
            self.simulation_state.on_parameters_changed()

    def _on_launch_click(self):
        """Dispara um novo lancamento a partir dos parametros atuais."""
        valid, _ = validar_parametros(self.simulation_state.params)
        if not valid:
            return
        self.simulation_state.launch()
        self.pause_button.set_text("Pausar")

    def _on_pause_click(self):
        """Pausa ou retoma a simulacao."""
        self.simulation_state.toggle_pause()
        if self.simulation_state.status == SimulationStatus.PAUSED:
            self.pause_button.set_text("Continuar")
        else:
            self.pause_button.set_text("Pausar")

    def _on_reset_click(self):
        """Restaura todos os parametros, trajetorias e historico ao estado inicial."""
        self.simulation_state.reset_all()
        self.parameters_panel.sync_from_params(self.simulation_state.params)
        self.pause_button.set_text("Pausar")

    # ------------------------------------------------------------------
    # Loop principal
    # ------------------------------------------------------------------
    def run(self):
        while self.running:
            dt = self.clock.tick(config.FPS) / 1000.0
            self._handle_events()
            self._update(dt)
            self._draw()

        pygame.quit()
        sys.exit()

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.VIDEORESIZE:
                w = max(event.w, config.WINDOW_MIN_WIDTH)
                h = max(event.h, config.WINDOW_MIN_HEIGHT)
                self.screen = pygame.display.set_mode((w, h), pygame.RESIZABLE)
                self._recompute_layout()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.running = False

            self.toggle_button.handle_event(event)
            self.parameters_panel.handle_event(event)
            self.launch_button.handle_event(event)
            self.pause_button.handle_event(event)
            self.reset_button.handle_event(event)

    def _update(self, dt):
        # Avanca o tempo fisico da simulacao
        self.simulation_state.update(dt)

        # Atualiza o texto do botao de pausa se o lancamento terminou
        if self.simulation_state.status == SimulationStatus.FINISHED:
            self.pause_button.set_text("Pausar")

        # Escala dinamica: ajusta a visualizacao para caber a trajetoria atual e anterior
        curr_res = self.simulation_state.current_results
        last_res = self.simulation_state.last_results
        proj_x, proj_y = self.simulation_state.get_projectile_position()

        max_x = max(
            curr_res.range_m,
            last_res.range_m if last_res else 0.0,
            proj_x,
            self.simulation_state.params.x0,
            30.0,
        )
        max_y = max(
            curr_res.max_height_m,
            last_res.max_height_m if last_res else 0.0,
            proj_y,
            self.simulation_state.params.y0,
            20.0,
        )
        self.plane.adapt_scale(max_x, max_y)

        # Atualiza os resultados numericos no painel HUD
        st = self.simulation_state.status
        if st == SimulationStatus.IDLE:
            status_desc = "Pronto para lancar"
        elif st == SimulationStatus.RUNNING:
            status_desc = f"Em voo (t={self.simulation_state.current_time:.2f}s)"
        elif st == SimulationStatus.PAUSED:
            status_desc = f"Pausado (t={self.simulation_state.current_time:.2f}s)"
        else:
            status_desc = "Lancamento concluido"

        self.results_panel.update_results(
            result_range=curr_res.range_m,
            result_max_height=curr_res.max_height_m,
            result_time_of_flight=curr_res.time_of_flight_s,
            status_text=status_desc,
        )

    def _draw(self):
        self.screen.fill(config.COLORS["background"])

        # 1. Desenho do cenario de fundo, grade e eixos
        self.plane.draw(self.screen, self.font_small)

        # 2. Trajetoria prevista do ULTIMO lancamento (preservada, linha pontilhada azulada/cinza)
        if self.simulation_state.predicted_trajectory_last:
            self.plane.draw_dashed_curve(
                self.screen,
                self.simulation_state.predicted_trajectory_last,
                config.COLORS["traj_predicted_last"],
                dash_px=6,
                gap_px=6,
                width=2,
            )

        # 3. Trajetoria prevista dos parametros ATUAIS (linha pontilhada preta)
        if self.simulation_state.predicted_trajectory_current:
            self.plane.draw_dashed_curve(
                self.screen,
                self.simulation_state.predicted_trajectory_current,
                config.COLORS["traj_predicted_current"],
                dash_px=8,
                gap_px=5,
                width=2,
            )

        # 4. Trajetoria REAL percorrida pelo projetil (linha solida vermelha)
        if len(self.simulation_state.actual_trajectory_points) >= 2:
            self.plane.draw_actual_trajectory(
                self.screen,
                self.simulation_state.actual_trajectory_points,
                config.COLORS["traj_actual"],
                width=3,
            )

        # 5. Projetil geometrico temporario (sem sprites/imagens ainda)
        proj_pos = self.simulation_state.get_projectile_position()
        self.plane.draw_projectile(self.screen, proj_pos)

        # 6. Painel HUD de resultados (canto superior esquerdo)
        self.results_panel.draw(self.screen)

        # 7. Botoes de controle (canto inferior direito)
        self.reset_button.draw(self.screen)
        self.pause_button.draw(self.screen)
        self.launch_button.draw(self.screen)

        # 8. Painel HUD de parametros e botao de alternancia (canto superior direito)
        self.parameters_panel.draw(self.screen)
        self.toggle_button.draw(self.screen)

        pygame.display.flip()


if __name__ == "__main__":
    App().run()
