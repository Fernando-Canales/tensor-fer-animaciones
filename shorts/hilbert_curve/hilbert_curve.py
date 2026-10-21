from manim import *
import numpy as np

# ---------------------------------------------------------------
# FORMATO: cuadro vertical 9:16 (1080x1920), igual que los otros shorts.
# Pon PORTRAIT = False para renderizar horizontal.
# Render: manim -qh hilbert_short.py HilbertShort    (60 fps: --fps 60)
# ---------------------------------------------------------------
PORTRAIT = True
if PORTRAIT:
    config.pixel_width = 1080
    config.pixel_height = 1920
    config.frame_width = 6.0
    config.frame_height = 6.0 * 16 / 9


# ===============================================================
# GEOMETRÍA (numpy puro)
# ===============================================================
# BEGIN-GEOM
def hilbert_cells(n):
    """Curva de Hilbert de orden n: (4^n, 2) índices enteros de celda, en una malla 2^n x 2^n.
    Empieza en la esquina (0,0), pasa por todas las celdas y termina en (2^n-1, 0)."""
    t = np.arange(4 ** n, dtype=np.int64)
    x = np.zeros_like(t)
    y = np.zeros_like(t)
    s = 1
    while s < 2 ** n:
        rx = (t // 2) & 1
        ry = (t ^ rx) & 1
        flip = (ry == 0) & (rx == 1)
        x = np.where(flip, s - 1 - x, x)
        y = np.where(flip, s - 1 - y, y)
        swap = ry == 0
        x, y = np.where(swap, y, x), np.where(swap, x, y)
        x = x + s * rx
        y = y + s * ry
        t = t // 4
        s *= 2
    return np.stack([x, y], axis=1)


def hilbert_unit(n):
    """Centros de las celdas, en el cuadrado unidad [0,1]^2."""
    return (hilbert_cells(n) + 0.5) / 2 ** n


def truncate_polyline(pts, f):
    """Primer tramo de la polilínea que ocupa una fracción f de su longitud total."""
    if f >= 1.0:
        return pts
    seg = np.linalg.norm(np.diff(pts, axis=0), axis=1)
    cum = np.concatenate([[0.0], np.cumsum(seg)])
    target = max(f, 1e-6) * cum[-1]
    k = int(np.searchsorted(cum, target, side="right")) - 1
    k = min(max(k, 0), len(seg) - 1)
    u = (target - cum[k]) / seg[k] if seg[k] > 0 else 0.0
    last = pts[k] + (pts[k + 1] - pts[k]) * u
    return np.vstack([pts[:k + 1], last])
# END-GEOM


class HilbertShort(Scene):
    def construct(self):
        # ---------------- Paleta ----------------
        TXT_BASE = ManimColor("#E1E1D5")
        COLOR_RESULT = YELLOW_D
        COLOR_LOGO = BLUE_C
        GRADIENT = [BLUE_C, TEAL_C, YELLOW_D]       # color a lo largo de la curva

        W = config.frame_width

        # ---------------- Parámetros ----------------
        N = 7                                        # nivel máximo (16384 puntos)
        L = 5.2                                      # lado del cuadrado en pantalla
        CENTER = np.array([0.0, 0.7])
        K = 80                                       # trozos de color a lo largo de la curva
        WIDTHS = [0, 6.0, 5.0, 4.4, 3.9, 3.6, 3.3, 3.0]   # grosor por nivel
        STAT_Y = [-2.75, -3.45]

        def fit_width(m, frac=0.93):
            if m.width > W * frac:
                m.scale(W * frac / m.width)
            return m

        # ---------------- Curvas precalculadas ----------------
        H = [None] + [hilbert_unit(n) for n in range(1, N + 1)]

        def curve_pts(x, frac=1.0):
            """Curva en el 'progreso' x = nivel + fracción de transición (en [0,1]^2).
            Cada punto del nivel n+1 sale del centro de su celda madre (índice // 4)."""
            n = min(int(x), N)
            a = x - n
            if n >= N or a < 1e-9:
                pts = H[min(n, N)]
            else:
                s = a * a * (3 - 2 * a)              # suavizado
                parent = H[n][np.arange(4 ** (n + 1)) // 4]
                pts = parent + (H[n + 1] - parent) * s
            return truncate_polyline(pts, frac)

        def to_scene(pts):
            return np.column_stack([CENTER[0] + (pts[:, 0] - 0.5) * L,
                                    CENTER[1] + (pts[:, 1] - 0.5) * L,
                                    np.zeros(len(pts))])

        lv = ValueTracker(1.0)                       # nivel (con fracción durante la transición)
        draw = ValueTracker(0.0)                     # fracción dibujada (solo para el nivel 1)
        colors = color_gradient(GRADIENT, K)

        def make_curve():
            x = lv.get_value()
            pts = to_scene(curve_pts(x, draw.get_value()))
            n = min(int(x), N)
            a = x - n
            w = WIDTHS[n] if n >= N else WIDTHS[n] + (WIDTHS[n + 1] - WIDTHS[n]) * a
            k = min(K, len(pts) - 1)
            edges = np.linspace(0, len(pts) - 1, k + 1).astype(int)
            g = VGroup()
            for i in range(k):
                piece = VMobject()
                piece.set_points_as_corners(pts[edges[i]: edges[i + 1] + 1])
                piece.set_stroke(colors[i * K // k], width=w)
                piece.set_fill(opacity=0)
                g.add(piece)
            return g

        curve = always_redraw(make_curve)
        curve.set_z_index(3)

        # ---------------- Estadísticas (medidas de la curva real) ----------------
        def make_stat():
            x = lv.get_value()
            p = curve_pts(x)
            length = np.linalg.norm(np.diff(p, axis=0), axis=1).sum()   # lado del cuadrado = 1
            t = Text(f"Longitud: ×{length:.1f}", font_size=50, weight=BOLD, color=GREEN_C)
            return fit_width(t).move_to(UP * STAT_Y[0])

        stat_len = always_redraw(make_stat)

        # ---------------- Subtítulos ----------------
        cap_holder = [None]

        def make_caption(text, size=50, color=TXT_BASE):
            c = Text(text, font_size=size, weight=BOLD, color=color, line_spacing=1.1)
            fit_width(c).move_to(UP * 4.1)
            return c

        def swap_caption(text, **kw):
            new = make_caption(text, **kw)
            old = cap_holder[0]
            cap_holder[0] = new
            if old is None:
                return [FadeIn(new, shift=DOWN * 0.2)]
            return [FadeOut(old, shift=UP * 0.2), FadeIn(new, shift=DOWN * 0.2)]

        # =============================================================
        # 1. GANCHO: el título en grande, luego aparece el cuadrado
        # =============================================================
        title = Text("¿Puede una línea\nllenar un cuadrado?", font_size=60, weight=BOLD,
                     color=TXT_BASE, line_spacing=1.3)
        fit_width(title).move_to(ORIGIN)
        self.play(Write(title), run_time=2.2)
        self.wait(1.6)
        self.play(FadeOut(title), run_time=0.9)
        box = Square(side_length=L, color=TXT_BASE, stroke_width=4).move_to(np.array([*CENTER, 0.0]))
        self.play(Create(box), run_time=1.6)
        self.wait(0.6)

        # =============================================================
        # 2. NIVEL 1: dividir en cuatro y unir los centros
        # =============================================================
        c0 = np.array([*CENTER, 0.0])
        vline = Line(c0 + UP * L / 2, c0 + DOWN * L / 2, color=TXT_BASE, stroke_width=2.5)
        hline = Line(c0 + LEFT * L / 2, c0 + RIGHT * L / 2, color=TXT_BASE, stroke_width=2.5)
        grid1 = VGroup(vline, hline)
        centers1 = to_scene(H[1])
        dots = VGroup(*[Dot(p, radius=0.09, color=YELLOW) for p in centers1])
        dots.set_z_index(5)
        self.play(*swap_caption("Divídelo en cuatro\ny une sus centros"),
                  Create(grid1), run_time=1.6)
        self.play(FadeIn(dots, scale=2), run_time=1.1)
        self.add(curve)
        self.play(FadeIn(stat_len),
                  draw.animate.set_value(1.0), run_time=2.4, rate_func=linear)
        self.wait(0.8)

        # =============================================================
        # 3. REPETIR: cada cuarto se divide otra vez
        # =============================================================
        def new_grid(m, sw):
            """Líneas nuevas de la división m (celdas de lado L/2^m): posiciones en múltiplos impares."""
            offs = [L * (i / 2 ** m - 0.5) for i in range(1, 2 ** m, 2)]
            return VGroup(*[Line(c0 + RIGHT * o + UP * L / 2, c0 + RIGHT * o + DOWN * L / 2,
                                 color=TXT_BASE, stroke_width=sw) for o in offs],
                          *[Line(c0 + UP * o + LEFT * L / 2, c0 + UP * o + RIGHT * L / 2,
                                 color=TXT_BASE, stroke_width=sw) for o in offs])

        def new_dots(m, r):
            d = VGroup(*[Dot(p, radius=r, color=YELLOW) for p in to_scene(H[m])])
            d.set_z_index(5)
            return d

        # --- Segunda división: primero las líneas, luego los centros, luego se conectan ---
        grid2 = new_grid(2, 2.0)
        dots2 = new_dots(2, 0.07)
        self.play(*swap_caption("Ahora repite\nen cada cuarto"),
                  FadeOut(dots), Create(grid2), run_time=1.9)                 # 1) divide
        self.wait(0.4)
        self.play(FadeIn(dots2, scale=2), run_time=1.1)                       # 2) centros
        self.wait(0.6)
        self.play(FadeOut(dots2), lv.animate.set_value(2.0),                  # 3) conecta
                  run_time=3.5, rate_func=linear)
        self.wait(0.4)

        # --- Tercera división: igual de despacio ---
        grid3 = new_grid(3, 1.6)
        dots3 = new_dots(3, 0.05)
        self.play(*swap_caption("Y otra vez…"), Create(grid3), run_time=1.8)   # 1) divide
        self.wait(0.4)
        self.play(FadeIn(dots3, scale=2), run_time=1.1)                       # 2) centros
        self.wait(0.5)
        self.play(FadeOut(grid1), FadeOut(grid2), FadeOut(grid3), FadeOut(dots3),
                  lv.animate.set_value(3.0), run_time=3.0, rate_func=linear)  # 3) conecta
        self.wait(0.3)
        for n, rt in [(4, 2.2), (5, 1.9), (6, 1.8), (7, 1.8)]:
            self.play(lv.animate.set_value(float(n)), run_time=rt, rate_func=linear)
            self.wait(0.3)
        self.wait(0.8)

        # =============================================================
        # 4. REVELACIÓN: longitud infinita, y llena el cuadrado
        # =============================================================
        self.play(*swap_caption("Si repites\npara siempre…"), run_time=1.1)
        self.wait(0.8)
        stat_len.clear_updaters()
        per_inf = Text("Longitud: ∞", font_size=58, weight=BOLD, color=COLOR_RESULT)
        cover = Text("Cubre todo el cuadrado", font_size=52, weight=BOLD, color=COLOR_RESULT)
        fit_width(per_inf).move_to(UP * STAT_Y[0])
        fit_width(cover).move_to(UP * STAT_Y[1])
        filled = Square(side_length=L, stroke_width=0).move_to(c0)
        filled.set_fill(BLUE_E, opacity=0.35)
        filled.set_z_index(1)
        self.play(Transform(stat_len, per_inf), FadeIn(cover), FadeIn(filled), run_time=2.2)
        self.wait(2.2)

        # Nombre de la figura
        self.play(*swap_caption("Esta figura se llama\ncurva de Hilbert", size=54, color=COLOR_RESULT),
                  run_time=1.2)
        self.wait(2.6)

        # =============================================================
        # 5. DIMENSIÓN 2
        # =============================================================
        dim = Text("Dimensión = 2", font_size=64, weight=BOLD, color=COLOR_RESULT)
        fit_width(dim).move_to(UP * STAT_Y[0])
        self.play(*swap_caption("Una línea\nque llena un área", size=56, color=COLOR_RESULT),
                  FadeOut(stat_len), FadeOut(cover), run_time=1.4)
        self.play(FadeIn(dim, shift=UP * 0.2), run_time=1.1)
        self.wait(3.0)

        # =============================================================
        # 6. CIERRE Y LOGO
        # =============================================================
        curve.clear_updaters()
        self.play(FadeOut(VGroup(curve, box, filled, dim, cap_holder[0])), run_time=1.2)
        logo = MathTex(r"F_{GC}", font_size=150, color=COLOR_LOGO).move_to(ORIGIN)
        self.play(FadeIn(logo, scale=0.7), run_time=1.6)
        self.wait(2.5)