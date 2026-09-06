"""
config.py
----------
Configuracoes centrais da aplicacao: cores, dimensoes, fontes e
parametros visuais/padrao. Manter tudo centralizado aqui evita
numeros "magicos" espalhados pelo codigo e facilita ajustes futuros
(inclusive quando a fisica e as animacoes forem implementadas).
"""

# ---------------------------------------------------------------------------
# Janela
# ---------------------------------------------------------------------------
WINDOW_TITLE = "Simulador de Lancamento de Projetil"
WINDOW_MIN_WIDTH = 900
WINDOW_MIN_HEIGHT = 600
WINDOW_DEFAULT_WIDTH = 1280
WINDOW_DEFAULT_HEIGHT = 800
FPS = 60

# ---------------------------------------------------------------------------
# Cores (cenario de campo aberto: ceu + grama, com grid/eixos por cima)
# ---------------------------------------------------------------------------
COLORS = {
    "background": (18, 22, 28),

    # Ceu (gradiente vertical, do topo ate a linha do horizonte)
    "sky_top": (120, 188, 230),
    "sky_horizon": (223, 240, 236),

    # Grama (gradiente vertical, do horizonte ate a base da janela)
    "grass_top": (150, 196, 92),
    "grass_bottom": (66, 122, 58),
    "grass_tuft_dark": (46, 90, 42),
    "grass_tuft_light": (140, 190, 90),

    # Sol e nuvens (desenhados com formas simples, sem imagens)
    "sun": (255, 246, 214),
    "cloud": (255, 255, 255),

    # Marca da origem (0, 0) - futuro ponto de apoio do estilingue
    "origin_mark": (95, 64, 40),

    # Grid/eixos sobrepostos ao cenario
    "grid": (255, 255, 255),
    "grid_alpha": 55,
    "axis": (42, 54, 46),
    "axis_text": (40, 52, 44),
    "unit_text": (55, 70, 60),

    "panel_bg_rgba": (26, 32, 40, 225),   # painel semitransparente (overlay/HUD)
    "panel_border": (80, 130, 180, 110),
    "panel_title": (235, 240, 245),
    "panel_text": (205, 215, 225),

    "button_bg": (38, 46, 58),
    "button_hover": (52, 108, 158),
    "button_border": (70, 130, 180),
    "button_text": (235, 240, 245),

    "accent": (86, 176, 232),
    "accent_dark": (56, 130, 180),

    "slider_track": (60, 70, 84),

    "result_label": (165, 178, 190),
    "result_value": (235, 240, 245),

    "launch_bg": (46, 160, 110),
    "launch_hover": (56, 190, 130),
    "launch_text": (18, 22, 28),

    "pause_bg": (210, 155, 45),
    "pause_hover": (235, 180, 65),
    "pause_text": (18, 22, 28),

    "reset_bg": (175, 55, 55),
    "reset_hover": (205, 75, 75),
    "reset_text": (245, 245, 250),

    # Trajetórias
    "traj_predicted_current": (18, 22, 28),     # Preto pontilhado (parâmetros atuais - alto contraste)
    "traj_predicted_last": (110, 145, 175),     # Azul/cinza suave pontilhado (último lançamento concluído)
    "traj_actual": (230, 35, 35),               # Vermelho vibrante (linha que segue a bolinha)

    # Projétil temporário (geométrico)
    "projectile_core": (255, 225, 65),
    "projectile_border": (35, 40, 50),
    "projectile_glow": (255, 240, 160, 110),
}

# ---------------------------------------------------------------------------
# Plano cartesiano
# ---------------------------------------------------------------------------
PLANE_MARGIN = 56             # margem interna para numeros e eixos (px)
PLANE_WORLD_WIDTH_M = 100.0    # faixa visivel padrao do eixo X, em metros
GRID_DIVISIONS = 10            # numero de divisoes da grade

# ---------------------------------------------------------------------------
# Painel de parametros (overlay)
# ---------------------------------------------------------------------------
PANEL_WIDTH = 300
PANEL_TOP_MARGIN = 76
PANEL_RIGHT_MARGIN = 24
PANEL_PADDING = 24
PANEL_MAX_HEIGHT = 300
SLIDER_ROW_HEIGHT = 52

# Botao "Parametros"
TOGGLE_BUTTON_WIDTH = 150
TOGGLE_BUTTON_HEIGHT = 40
TOGGLE_BUTTON_MARGIN = 20

# Painel de resultados (overlay)
RESULTS_PANEL_WIDTH = 270
RESULTS_PANEL_HEIGHT = 145
RESULTS_PANEL_MARGIN = 24

# Botoes de controle (Lancar, Pausar, Resetar)
CONTROL_BUTTON_WIDTH = 130
CONTROL_BUTTON_HEIGHT = 44
CONTROL_BUTTON_SPACING = 12
LAUNCH_BUTTON_WIDTH = 180
LAUNCH_BUTTON_HEIGHT = 50
LAUNCH_BUTTON_MARGIN = 24

# ---------------------------------------------------------------------------
# Fontes
# ---------------------------------------------------------------------------
FONT_NAME = None  # None -> fonte padrao do sistema (via pygame.font.SysFont)
FONT_SIZE_SMALL = 15
FONT_SIZE_NORMAL = 18
FONT_SIZE_TITLE = 22
FONT_SIZE_RESULT = 20

# ---------------------------------------------------------------------------
# Parametros fisicos padrao e faixas permitidas
# ---------------------------------------------------------------------------
DEFAULT_V0 = 25.0      # m/s
DEFAULT_ANGLE = 45.0   # graus
DEFAULT_Y0 = 0.0       # m
DEFAULT_G = 9.8        # m/s^2

V0_RANGE = (5.0, 150.0)
ANGLE_RANGE = (1.0, 89.0)
Y0_RANGE = (0.0, 50.0)
G_RANGE = (1.6, 24.8)

# ---------------------------------------------------------------------------
# Assets (preparacao para etapa futura - sprites ainda NAO sao usados)
# ---------------------------------------------------------------------------
ASSETS_DIR = "assets"
SLINGSHOT_IMAGE = "slingshot.png"
TARGET_IMAGE = "target.png"
PROJECTILE_IMAGE = "projectile.png"
