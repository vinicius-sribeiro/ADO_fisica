"""
ui.py
-----
Componentes visuais da aplicacao: plano cartesiano, botao generico,
slider, painel de parametros (overlay/HUD) e painel de resultados
(overlay/HUD).

Nenhum destes componentes realiza calculos fisicos. Eles apenas
capturam e exibem valores, e serao consumidos futuramente por
simulation.py e physics.py (por exemplo, para desenhar a trajetoria
real dentro de CartesianPlane, ou para disparar simulation.launch()
a partir do botao "Lancar").
"""

import random

import pygame

import config


# ---------------------------------------------------------------------------
# Utilidade: fundo semitransparente tipo HUD
# ---------------------------------------------------------------------------
def draw_overlay_panel(surface, rect, radius=16):
    """Desenha um retangulo semitransparente com cantos arredondados e
    borda sutil, dando o efeito de HUD sobreposto ao plano cartesiano."""
    overlay = pygame.Surface(rect.size, pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 0))

    body = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.rect(body, config.COLORS["panel_bg_rgba"], body.get_rect(), border_radius=radius)
    pygame.draw.rect(body, config.COLORS["panel_border"], body.get_rect(), width=1, border_radius=radius)

    overlay.blit(body, (0, 0))
    surface.blit(overlay, rect.topleft)


# ---------------------------------------------------------------------------
# Plano cartesiano (elemento principal da interface)
# ---------------------------------------------------------------------------
class CartesianPlane:
    """
    Area principal da simulacao. Desenha um cenario de campo aberto
    (ceu + grama, feito inteiramente com formas vetoriais - nenhuma
    imagem/sprite e usada nesta etapa) e, por cima dele, a grade
    discreta, os eixos e as marcacoes numericas, mantendo escala igual
    em X e Y (proporcao visual coerente).

    Expoe world_to_screen()/screen_to_world() para que a fisica e a
    animacao possam converter metros em pixels sem conhecer detalhes de layout.
    Inclui escala dinamica (adapt_scale) para manter trajetorias de qualquer
    alcance perfeitamente visiveis e legiveis.
    """

    def __init__(self, rect):
        self.rect = rect
        self.world_width_m = config.PLANE_WORLD_WIDTH_M
        self.margin = config.PLANE_MARGIN
        self._tuft_seeds = None  # posicoes da grama, geradas uma unica vez
        self._recalculate_scale()

    def resize(self, rect):
        self.rect = rect
        self._recalculate_scale()

    def adapt_scale(self, max_x_needed: float, max_y_needed: float):
        """
        Ajusta dinamicamente a escala do plano para que a trajetoria atual
        (e anterior) caiba confortavelmente na tela com margem visual adequada.
        """
        usable_w = max(self.rect.width - 2 * self.margin, 1)
        usable_h = max(self.rect.height - 2 * self.margin, 1)

        # Margem de folga visual (15% em X, 25% em Y para caber o HUD)
        target_world_w = max(max_x_needed * 1.15, 30.0)
        target_world_h = max(max_y_needed * 1.25, 20.0)

        # Escala uniforme (px por metro) para manter proporcoes fisicas reais
        scale_x = usable_w / target_world_w
        scale_y = usable_h / target_world_h
        target_scale = min(scale_x, scale_y)

        # Limita mudancas insignificantes para manter estabilidade visual
        new_w = usable_w / target_scale
        if abs(new_w - self.world_width_m) > 1.0:
            self.world_width_m = new_w
            self.scale = target_scale
            self.world_height_m = usable_h / self.scale

    def _recalculate_scale(self):
        usable_w = max(self.rect.width - 2 * self.margin, 1)
        usable_h = max(self.rect.height - 2 * self.margin, 1)

        # Escala unica (px por metro) para X e Y -> proporcao coerente
        self.scale = usable_w / self.world_width_m
        self.world_height_m = usable_h / self.scale

        self.origin = (
            self.rect.left + self.margin,
            self.rect.bottom - self.margin,
        )

        self._build_scenery()

    # -- Conversoes (metros <-> pixels) ------------------------------------
    def world_to_screen(self, x_m, y_m):
        """Converte coordenadas fisicas (metros) para coordenadas de tela (px)."""
        ox, oy = self.origin
        return (ox + x_m * self.scale, oy - y_m * self.scale)

    def screen_to_world(self, x_px, y_px):
        """Converte coordenadas de tela (px) para coordenadas fisicas (metros)."""
        ox, oy = self.origin
        return ((x_px - ox) / self.scale, (oy - y_px) / self.scale)

    def _grid_step_m(self):
        """Escolhe um passo de grade redondo e agradavel conforme a escala."""
        candidates = [1.0, 2.0, 5.0, 10.0, 20.0, 25.0, 50.0, 100.0, 200.0, 250.0, 500.0, 1000.0]
        for c in candidates:
            divisions = self.world_width_m / c
            if 5 <= divisions <= 14:
                return c
        return max(10.0, round(self.world_width_m / 10.0))

    # -- Cenario de fundo (ceu + grama), pre-renderizado --------------------
    def _build_scenery(self):
        """Monta o cenario (ceu, grama, sol, nuvens e tufos de grama) em
        um Surface do tamanho do plano. So roda ao iniciar/redimensionar."""
        w, h = self.rect.size
        scenery = pygame.Surface((w, h))

        horizon_y = max(h - self.margin, 1)  # linha do horizonte == y=0 do mundo

        self._fill_vertical_gradient(
            scenery, pygame.Rect(0, 0, w, horizon_y),
            config.COLORS["sky_top"], config.COLORS["sky_horizon"],
        )
        self._fill_vertical_gradient(
            scenery, pygame.Rect(0, horizon_y, w, h - horizon_y),
            config.COLORS["grass_top"], config.COLORS["grass_bottom"],
        )

        self._draw_sun(scenery, w, horizon_y)
        self._draw_clouds(scenery, w, horizon_y)
        self._draw_grass_tufts(scenery, horizon_y)

        self.scenery_surface = scenery

    @staticmethod
    def _lerp_color(color_a, color_b, t):
        return tuple(int(color_a[i] + (color_b[i] - color_a[i]) * t) for i in range(3))

    def _fill_vertical_gradient(self, surface, area, color_top, color_bottom):
        """Preenche 'area' com um degrade vertical simples (uma linha por pixel)."""
        height = max(area.height, 1)
        for row in range(area.height):
            t = row / max(height - 1, 1)
            color = self._lerp_color(color_top, color_bottom, t)
            y = area.top + row
            pygame.draw.line(surface, color, (area.left, y), (area.right, y))

    def _draw_sun(self, surface, w, horizon_y):
        """Sol simples: alguns circulos concentricos simulando um brilho suave."""
        cx, cy = int(w * 0.85), int(horizon_y * 0.24)
        for radius, color in (
            (64, (255, 250, 235)),
            (48, (255, 243, 208)),
            (34, (255, 234, 178)),
        ):
            pygame.draw.circle(surface, color, (cx, cy), radius)

    def _draw_clouds(self, surface, w, horizon_y):
        """Nuvens simples: grupos de circulos sobrepostos."""
        cloud_color = config.COLORS["cloud"]
        specs = [(0.16, 0.20, 1.0), (0.38, 0.34, 0.75), (0.60, 0.14, 0.85)]
        puffs = [(-24, 4, 16), (0, -6, 20), (24, 3, 16), (44, 6, 12), (-44, 7, 11)]
        for cx_ratio, cy_ratio, scale in specs:
            cx = w * cx_ratio
            cy = horizon_y * cy_ratio
            for dx, dy, r in puffs:
                pygame.draw.circle(
                    surface, cloud_color,
                    (int(cx + dx * scale), int(cy + dy * scale)), int(r * scale),
                )

    def _draw_grass_tufts(self, surface, horizon_y):
        """Pequenos tufos de grama ao longo do horizonte, com posicoes
        pseudo-aleatorias porem fixas (mesma semente)."""
        w, _ = self.rect.size
        if self._tuft_seeds is None:
            rng = random.Random(42)
            count = 140
            self._tuft_seeds = [
                (
                    rng.uniform(0.02, 0.98),              # fracao da largura
                    rng.uniform(7, 17),                   # altura da folha (px)
                    rng.uniform(-4, 4),                   # inclinacao (px)
                    rng.uniform(0.0, 1.0),                # variacao do tom de verde
                )
                for _ in range(count)
            ]

        dark = config.COLORS["grass_tuft_dark"]
        light = config.COLORS["grass_tuft_light"]
        for frac, height, lean, shade in self._tuft_seeds:
            sx = self.margin + frac * (w - 2 * self.margin)
            color = self._lerp_color(dark, light, shade)
            pygame.draw.line(surface, color, (sx, horizon_y), (sx + lean, horizon_y - height), 2)

    # -- Desenho do cenario, grade e eixos -----------------------------
    def draw(self, surface, font):
        # Cenario pre-renderizado (ceu + grama)
        surface.blit(self.scenery_surface, self.rect.topleft)

        step = self._grid_step_m()
        top = self.rect.top + self.margin // 2
        bottom = self.rect.bottom - self.margin // 2
        left = self.rect.left + self.margin // 2
        right = self.rect.right - self.margin // 2

        # Grade em overlay translucido
        grid_overlay = pygame.Surface(self.rect.size, pygame.SRCALPHA)
        grid_color = (*config.COLORS["grid"], config.COLORS["grid_alpha"])

        x = 0.0
        while x <= self.world_width_m + 1e-6:
            sx, _ = self.world_to_screen(x, 0)
            local_sx = sx - self.rect.left
            if self.rect.left <= sx <= self.rect.right:
                pygame.draw.line(
                    grid_overlay, grid_color,
                    (local_sx, top - self.rect.top), (local_sx, bottom - self.rect.top), 1,
                )
            x += step

        y = 0.0
        while y <= self.world_height_m + 1e-6:
            _, sy = self.world_to_screen(0, y)
            local_sy = sy - self.rect.top
            if self.rect.top <= sy <= self.rect.bottom:
                pygame.draw.line(
                    grid_overlay, grid_color,
                    (left - self.rect.left, local_sy), (right - self.rect.left, local_sy), 1,
                )
            y += step

        surface.blit(grid_overlay, self.rect.topleft)

        # Marcacoes numericas do eixo X
        x = 0.0
        while x <= self.world_width_m + 1e-6:
            if x > 0:
                sx, _ = self.world_to_screen(x, 0)
                if self.rect.left <= sx <= self.rect.right - 20:
                    label = font.render(f"{x:g}", True, config.COLORS["axis_text"])
                    surface.blit(label, (sx - label.get_width() / 2, self.origin[1] + 6))
            x += step

        # Marcacoes numericas do eixo Y
        y = 0.0
        while y <= self.world_height_m + 1e-6:
            if y > 0:
                _, sy = self.world_to_screen(0, y)
                if self.rect.top + 20 <= sy <= self.rect.bottom:
                    label = font.render(f"{y:g}", True, config.COLORS["axis_text"])
                    surface.blit(label, (self.origin[0] - label.get_width() - 8, sy - label.get_height() / 2))
            y += step

        # Eixos principais (destacados sobre a grade)
        ox, oy = self.origin
        pygame.draw.line(surface, config.COLORS["axis"], (ox, top), (ox, bottom), 2)
        pygame.draw.line(surface, config.COLORS["axis"], (left, oy), (right, oy), 2)

        # Indicacao das unidades
        unit_x = font.render("x (m)", True, config.COLORS["unit_text"])
        unit_y = font.render("y (m)", True, config.COLORS["unit_text"])
        surface.blit(unit_x, (right - unit_x.get_width(), oy + 6))
        surface.blit(unit_y, (ox + 8, top - unit_y.get_height() - 2))

        # Marca da origem (0, 0)
        pygame.draw.circle(surface, config.COLORS["origin_mark"], (int(ox), int(oy)), 5)

    # -- Desenho de trajetorias e projetil -----------------------------
    def draw_dashed_curve(self, surface, points, color, dash_px=8, gap_px=6, width=2):
        """
        Desenha uma curva pontilhada/tracejada analitica suave.
        Utiliza acumulacao de distancia euclidiana para manter tamanho uniforme dos tracos.
        """
        if len(points) < 2:
            return

        screen_pts = [self.world_to_screen(x, y) for x, y in points]

        drawing = True
        accum = 0.0

        for i in range(len(screen_pts) - 1):
            p1 = pygame.math.Vector2(screen_pts[i])
            p2 = pygame.math.Vector2(screen_pts[i + 1])
            seg_vec = p2 - p1
            seg_len = seg_vec.length()
            if seg_len < 1e-5:
                continue

            seg_dir = seg_vec.normalize()
            curr_offset = 0.0

            while curr_offset < seg_len:
                remaining = (dash_px - accum) if drawing else (gap_px - accum)
                step = min(seg_len - curr_offset, remaining)
                start_pt = p1 + seg_dir * curr_offset
                end_pt = p1 + seg_dir * (curr_offset + step)

                if drawing:
                    pygame.draw.line(
                        surface,
                        color,
                        (round(start_pt.x), round(start_pt.y)),
                        (round(end_pt.x), round(end_pt.y)),
                        width,
                    )

                accum += step
                curr_offset += step

                if drawing and accum >= dash_px:
                    drawing = False
                    accum = 0.0
                elif not drawing and accum >= gap_px:
                    drawing = True
                    accum = 0.0

    def draw_actual_trajectory(self, surface, points, color, width=3):
        """
        Desenha a linha solida que acompanha o projetil em voo.
        Permanece desenhada apos o termino do lancamento.
        """
        if len(points) < 2:
            return

        screen_pts = [self.world_to_screen(x, y) for x, y in points]

        # Brilho sutil ao fundo para destacar a trajetoria percorrida
        glow_surf = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        glow_color = (*color[:3], 70) if len(color) >= 3 else (255, 255, 255, 70)
        pygame.draw.lines(glow_surf, glow_color, False, screen_pts, width + 4)
        surface.blit(glow_surf, (0, 0))

        pygame.draw.lines(surface, color, False, screen_pts, width)

    def draw_projectile(self, surface, world_pos):
        """
        Desenha o projetil geometrico temporario (sem sprites/imagens ainda).
        Totalmente isolado para que na proxima etapa a substituicao por uma imagem
        PNG seja direta e localizada em um unico ponto.
        """
        sx, sy = self.world_to_screen(world_pos[0], world_pos[1])
        center = (int(round(sx)), int(round(sy)))

        # 1. Brilho sutil (halo)
        glow_surf = pygame.Surface((32, 32), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, config.COLORS["projectile_glow"], (16, 16), 12)
        surface.blit(glow_surf, (center[0] - 16, center[1] - 16))

        # 2. Borda externa
        pygame.draw.circle(surface, config.COLORS["projectile_border"], center, 7)

        # 3. Miolo colorido
        pygame.draw.circle(surface, config.COLORS["projectile_core"], center, 5)

        # 4. Ponto de brilho especular para sensacao de profundidade
        pygame.draw.circle(surface, (255, 255, 230), (center[0] - 2, center[1] - 2), 2)


# ---------------------------------------------------------------------------
# Botao generico
# ---------------------------------------------------------------------------
class Button:
    """Botao clicavel simples, com suporte a estilos visuais e hover."""

    def __init__(self, rect, text, font, on_click=None, style="default"):
        self.rect = rect
        self.text = text
        self.font = font
        self.on_click = on_click
        self.style = style
        self.hovered = False

    def set_text(self, new_text: str):
        self.text = new_text

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos) and self.on_click:
                self.on_click()

    def draw(self, surface):
        if self.style == "launch":
            bg = config.COLORS["launch_hover"] if self.hovered else config.COLORS["launch_bg"]
            text_color = config.COLORS["launch_text"]
            border = None
        elif self.style == "pause":
            bg = config.COLORS["pause_hover"] if self.hovered else config.COLORS["pause_bg"]
            text_color = config.COLORS["pause_text"]
            border = None
        elif self.style == "reset":
            bg = config.COLORS["reset_hover"] if self.hovered else config.COLORS["reset_bg"]
            text_color = config.COLORS["reset_text"]
            border = None
        else:
            bg = config.COLORS["button_hover"] if self.hovered else config.COLORS["button_bg"]
            text_color = config.COLORS["button_text"]
            border = config.COLORS["button_border"]

        pygame.draw.rect(surface, bg, self.rect, border_radius=10)
        if border:
            pygame.draw.rect(surface, border, self.rect, width=1, border_radius=10)

        label = self.font.render(self.text, True, text_color)
        surface.blit(label, label.get_rect(center=self.rect.center))


# ---------------------------------------------------------------------------
# Slider (com callback em tempo real)
# ---------------------------------------------------------------------------
class Slider:
    """Slider horizontal: permite arrastar ou clicar para alterar o valor em tempo real."""

    def __init__(self, rect, min_value, max_value, value, label, unit, font, on_change=None):
        self.rect = rect
        self.min_value = min_value
        self.max_value = max_value
        self.value = value
        self.label = label
        self.unit = unit
        self.font = font
        self.on_change = on_change
        self.dragging = False
        self.attr = None  # nome do atributo em ProjectileParameters

        self.track = pygame.Rect(rect.x, rect.y + 30, rect.width, 4)
        self._update_handle()

    def _update_handle(self):
        span = self.max_value - self.min_value
        ratio = 0.0 if span == 0 else (self.value - self.min_value) / span
        hx = self.track.x + ratio * self.track.width
        self.handle = pygame.Rect(0, 0, 14, 14)
        self.handle.center = (hx, self.track.centery)

    def _hit_area(self):
        return self.handle.inflate(10, 10)

    def set_value(self, new_value: float):
        self.value = max(self.min_value, min(self.max_value, new_value))
        self._update_handle()

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self._hit_area().collidepoint(event.pos) or self.track.collidepoint(event.pos):
                self.dragging = True
                self._set_from_mouse_x(event.pos[0])
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            self._set_from_mouse_x(event.pos[0])

    def _set_from_mouse_x(self, mouse_x):
        ratio = (mouse_x - self.track.x) / self.track.width
        ratio = max(0.0, min(1.0, ratio))
        self.value = self.min_value + ratio * (self.max_value - self.min_value)
        self._update_handle()
        if self.on_change:
            self.on_change(self.attr, self.value)

    def move_to(self, new_rect):
        self.rect = new_rect
        self.track = pygame.Rect(new_rect.x, new_rect.y + 30, new_rect.width, 4)
        self._update_handle()

    def draw(self, surface):
        label = self.font.render(
            f"{self.label}: {self.value:.1f} {self.unit}", True, config.COLORS["panel_text"]
        )
        surface.blit(label, (self.rect.x, self.rect.y))

        pygame.draw.rect(surface, config.COLORS["slider_track"], self.track, border_radius=2)
        filled_width = max(self.handle.centerx - self.track.x, 0)
        filled = pygame.Rect(self.track.x, self.track.y, filled_width, self.track.height)
        pygame.draw.rect(surface, config.COLORS["accent_dark"], filled, border_radius=2)
        pygame.draw.circle(surface, config.COLORS["accent"], self.handle.center, 8)


# ---------------------------------------------------------------------------
# Painel de parametros (overlay / HUD)
# ---------------------------------------------------------------------------
class ParametersPanel:
    """
    Painel semitransparente (HUD) com os controles de v0, angulo, y0 e g.
    Ao alterar os controles, notifica a simulacao imediatamente para recalculor
    em tempo real a trajetoria e resultados analiticos.
    """

    def __init__(self, rect, font, title_font, params, on_param_change=None):
        self.rect = rect
        self.font = font
        self.title_font = title_font
        self.visible = False
        self.params = params  # instancia de physics.ProjectileParameters
        self.on_param_change = on_param_change

        self.sliders = []
        self._build_sliders()

    def _build_sliders(self):
        specs = [
            ("v0", "Velocidade inicial (v0)", config.V0_RANGE, "m/s"),
            ("angle_deg", "Angulo de lancamento (theta)", config.ANGLE_RANGE, "graus"),
            ("y0", "Altura inicial (y0)", config.Y0_RANGE, "m"),
            ("g", "Gravidade (g)", config.G_RANGE, "m/s^2"),
        ]
        self.sliders = []
        for i, (attr, label, (vmin, vmax), unit) in enumerate(specs):
            value = getattr(self.params, attr)
            slider = Slider(
                self._slider_rect(i),
                vmin,
                vmax,
                value,
                label,
                unit,
                self.font,
                on_change=self._on_slider_changed,
            )
            slider.attr = attr
            self.sliders.append(slider)

    def _on_slider_changed(self, attr, value):
        setattr(self.params, attr, value)
        if self.on_param_change:
            self.on_param_change()

    def sync_from_params(self, params=None):
        """Atualiza a posicao visual dos sliders a partir dos dados do objeto params."""
        if params is not None:
            self.params = params
        for slider in self.sliders:
            # Um reset pode ocorrer enquanto um slider ainda estava sendo arrastado.
            # Libera esse estado antes de reposicionar o controle para os padroes.
            slider.dragging = False
            slider.set_value(getattr(self.params, slider.attr))

    def _slider_rect(self, index):
        top = self.rect.y + 56 + index * config.SLIDER_ROW_HEIGHT
        return pygame.Rect(
            self.rect.x + config.PANEL_PADDING,
            top,
            self.rect.width - 2 * config.PANEL_PADDING,
            config.SLIDER_ROW_HEIGHT - 12,
        )

    def resize(self, rect):
        self.rect = rect
        for i, slider in enumerate(self.sliders):
            slider.move_to(self._slider_rect(i))

    def toggle(self):
        self.visible = not self.visible

    def handle_event(self, event):
        if not self.visible:
            return
        for slider in self.sliders:
            slider.handle_event(event)

    def draw(self, surface):
        if not self.visible:
            return
        draw_overlay_panel(surface, self.rect)

        title = self.title_font.render("Parametros", True, config.COLORS["panel_title"])
        surface.blit(title, (self.rect.x + config.PANEL_PADDING, self.rect.y + 18))

        for slider in self.sliders:
            slider.draw(surface)


# ---------------------------------------------------------------------------
# Painel de resultados (overlay / HUD)
# ---------------------------------------------------------------------------
class ResultsPanel:
    """
    Painel semitransparente (HUD) com os resultados fisicos analiticos em tempo real:
    Alcance (R), Altura maxima (Ymax) e Tempo de voo (T).
    """

    def __init__(self, rect, font, value_font):
        self.rect = rect
        self.font = font
        self.value_font = value_font
        self.result_range = None
        self.result_max_height = None
        self.result_time_of_flight = None
        self.status_text = "Pronto"

    def update_results(
        self,
        result_range=None,
        result_max_height=None,
        result_time_of_flight=None,
        status_text=None,
    ):
        """Atualiza os valores exibidos instantaneamente."""
        self.result_range = result_range
        self.result_max_height = result_max_height
        self.result_time_of_flight = result_time_of_flight
        if status_text is not None:
            self.status_text = status_text

    @staticmethod
    def _fmt(value, unit):
        return f"{value:.2f} {unit}" if value is not None else "--"

    def draw(self, surface):
        draw_overlay_panel(surface, self.rect)

        rows = [
            ("Alcance (R)", self._fmt(self.result_range, "m")),
            ("Altura max. (Ymax)", self._fmt(self.result_max_height, "m")),
            ("Tempo de voo (T)", self._fmt(self.result_time_of_flight, "s")),
        ]

        y = self.rect.y + 14
        for label, value in rows:
            label_surf = self.font.render(label, True, config.COLORS["result_label"])
            value_surf = self.value_font.render(value, True, config.COLORS["result_value"])
            surface.blit(label_surf, (self.rect.x + 16, y))
            surface.blit(value_surf, (self.rect.x + 16, y + 17))
            y += 37
