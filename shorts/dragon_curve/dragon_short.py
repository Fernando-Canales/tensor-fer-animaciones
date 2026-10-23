from manim import *
import numpy as np

# ---------------------------------------------------------------
# FORMATO: cuadro vertical 9:16 (1080x1920), igual que los otros shorts.
# Pon PORTRAIT = False para renderizar horizontal.
# Render: manim -qh --fps 60 dragon_short.py DragonShort
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
def unfold(P, alpha=1.0):
    """Un paso de 'desdoblar' la curva del dragón.

    P: (m, 2) vértices de una polilínea. Cada segmento p_i -> p_{i+1} se sustituye por
    dos segmentos que forman un ángulo recto: el vértice nuevo es el punto medio,
    desplazado perpendicularmente la mitad del segmento (así cuelga del segmento como
    el vértice de un triángulo rectángulo isósceles). El lado va alternando: izquierda,
    derecha, izquierda, ...

    alpha en [0, 1]: cuánto del desplazamiento se ha aplicado (para animar el pliegue).
    Los extremos P[0] y P[-1] no se mueven. Devuelve (2m - 1, 2).
    """
    d = P[1:] - P[:-1]                                   # segmentos
    mid = (P[:-1] + P[1:]) / 2
    perp = np.stack([-d[:, 1], d[:, 0]], axis=1)         # d girado +90 grados
    sign = np.where(np.arange(len(d)) % 2 == 0, 1.0, -1.0)[:, None]
    new = mid + alpha * sign * perp / 2
    out = np.empty((2 * len(P) - 1, 2))
    out[0::2] = P
    out[1::2] = new
    return out


def dragon_levels(n_max):
    """Niveles 0..n_max (extremos fijos en (0,0) y (1,0))."""
    levels = [np.array([[0.0, 0.0], [1.0, 0.0]])]
    for _ in range(n_max):
        levels.append(unfold(levels[-1]))
    return levels


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


def rot(theta):
    c, s = np.cos(theta), np.sin(theta)
    return np.array([[c, -s], [s, c]])


def bbox(pts):
    lo, hi = pts.min(axis=0), pts.max(axis=0)
    return lo, hi
# END-GEOM


class DragonShort(Scene):
    def construct(self):
        # ---------------- Paleta ----------------
        TXT_BASE = ManimColor("#E1E1D5")
        COLOR_RESULT = YELLOW_D
        COLOR_LOGO = BLUE_C
        # un degradado por dragón (el primero es el protagonista)
        PALETTES = [
            [BLUE_D, BLUE_C, TEAL_C],
            [YELLOW_E, YELLOW_D, ORANGE],
            [PURPLE_C, PINK, RED_C],
            [GREEN_E, GREEN_C, GREEN_A],
        ]

        W = config.frame_width

        # ---------------- Parámetros ----------------
        N = 14                                       # nivel máximo (2^14 = 16384 segmentos)
        CENTER = np.array([0.0, 0.7])
        BOX_W, BOX_H = 5.5, 5.4                      # zona útil en pantalla
        K = 80                                       # trozos de color a lo largo de la curva
        WIDTHS = [7.0, 6.5, 6.0, 5.4, 4.8, 4.2, 3.7, 3.3, 3.0, 2.7, 2.4, 2.1, 1.9, 1.7, 1.5]
        STAT_Y = 2.75 * -1

        def fit_width(m, frac=0.93):
            if m.width > W * frac:
                m.scale(W * frac / m.width)
            return m

        # ---------------- Curvas y encuadre ----------------
        LV = dragon_levels(N)
        final = LV[N]

        # Giro del dragón (alrededor de su punto inicial) que mejor llena la zona útil
        best = None
        for deg in np.arange(0.0, 90.0, 1.0):
            q = final @ rot(np.radians(deg)).T
            lo, hi = bbox(q)
            sc = min(BOX_W / (hi[0] - lo[0]), BOX_H / (hi[1] - lo[1]))
            if best is None or sc > best[0]:
                best = (sc, np.radians(deg), (lo + hi) / 2)
        SC1, ROT, C1 = best                          # escala, giro y centro de UN dragón

        # Cuatro dragones (giros de 90° alrededor del mismo punto inicial)
        union = np.vstack([final @ rot(ROT + k * np.pi / 2).T for k in range(4)])
        lo, hi = bbox(union)
        SC4 = min(BOX_W / (hi[0] - lo[0]), BOX_H / (hi[1] - lo[1]))   # el centro es el origen

        # ---------------- Estado animable ----------------
        lv = ValueTracker(0.0)                       # nivel (con fracción durante el pliegue)
        draw = ValueTracker(0.0)                     # fracción dibujada (solo nivel 0)
        cam = ValueTracker(0.0)                      # 0: un dragón · 1: vista de los cuatro
        op4 = ValueTracker(0.0)                      # opacidad de los 3 dragones extra
        colors = [color_gradient(p, K) for p in PALETTES]

        def curve_pts(x, frac=1.0):
            n = min(int(x), N)
            a = x - n
            if n >= N or a < 1e-9:
                pts = LV[min(n, N)]
            else:
                s = a * a * (3 - 2 * a)              # suavizado
                pts = unfold(LV[n], s)
            return truncate_polyline(pts, frac)

        def make_curve():
            x = lv.get_value()
            base = curve_pts(x, draw.get_value())
            c = cam.get_value()
            c = c * c * (3 - 2 * c)
            sc = SC1 * (SC4 / SC1) ** c
            c0 = C1 * (1 - c)                        # el centro pasa de C1 al origen (pivote)
            n = min(int(x), N)
            a = x - n
            w = WIDTHS[n] if n >= N else WIDTHS[n] + (WIDTHS[n + 1] - WIDTHS[n]) * a
            w *= 1 - 0.3 * c
            g = VGroup()
            for k in range(4):
                op = 1.0 if k == 0 else op4.get_value()
                if op < 0.005:
                    continue
                q = base @ rot(ROT + k * np.pi / 2).T
                pts = np.column_stack([CENTER[0] + (q[:, 0] - c0[0]) * sc,
                                       CENTER[1] + (q[:, 1] - c0[1]) * sc,
                                       np.zeros(len(q))])
                kk = min(K, len(pts) - 1)
                edges = np.linspace(0, len(pts) - 1, kk + 1).astype(int)
                for i in range(kk):
                    piece = VMobject()
                    piece.set_points_as_corners(pts[edges[i]: edges[i + 1] + 1])
                    piece.set_stroke(colors[k][i * K // kk], width=w, opacity=op)
                    piece.set_fill(opacity=0)
                    g.add(piece)
            return g

        curve = always_redraw(make_curve)
        curve.set_z_index(3)

        # ---------------- Contador de pliegues (= vértices con giro) ----------------
        def make_counter():
            x = lv.get_value()
            n = int(round(x))                        # cambia a mitad de cada pliegue
            t = Text(f"Pliegues: {2 ** n - 1:,}".replace(",", "."),
                     font_size=52, weight=BOLD, color=GREEN_C)
            return fit_width(t).move_to(UP * STAT_Y)

        counter = always_redraw(make_counter)

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
        # 1. GANCHO: título en grande
        # =============================================================
        title = Text("Dobla una tira de papel\nmuchas veces…\ny desdóblala", font_size=58,
                     weight=BOLD, color=TXT_BASE, line_spacing=1.3)
        fit_width(title).move_to(ORIGIN)
        self.play(Write(title), run_time=2.6)
        self.wait(1.5)
        self.play(FadeOut(title), run_time=0.9)

        # =============================================================
        # 2. LA TIRA (nivel 0)
        # =============================================================
        self.add(curve)
        self.play(*swap_caption("Una tira de papel\nsin doblar"),
                  FadeIn(counter),
                  draw.animate.set_value(1.0), run_time=1.8, rate_func=linear)
        self.wait(0.8)

        # =============================================================
        # 3. PRIMEROS PLIEGUES, DESPACIO
        # =============================================================
        self.play(*swap_caption("Dobla la tira:\nun ángulo recto"),
                  lv.animate.set_value(1.0), run_time=2.8, rate_func=linear)
        self.wait(0.8)
        self.play(*swap_caption("Dóblala otra vez…"),
                  lv.animate.set_value(2.0), run_time=2.8, rate_func=linear)
        self.wait(0.5)
        self.play(lv.animate.set_value(3.0), run_time=2.5, rate_func=linear)
        self.wait(0.3)

        # =============================================================
        # 4. SIGUE DOBLANDO: sin pausas hasta el nivel N
        # =============================================================
        self.play(*swap_caption("Y sigue doblando…"), lv.animate.set_value(4.0),
                  run_time=2.2, rate_func=linear)
        for n, rt in [(5, 2.0), (6, 1.8), (7, 1.7), (8, 1.6), (9, 1.5),
                      (10, 1.5), (11, 1.5), (12, 1.5), (13, 1.5), (14, 1.5)]:
            self.play(lv.animate.set_value(float(n)), run_time=rt, rate_func=linear)
        self.wait(0.8)

        # =============================================================
        # 5. NOMBRE
        # =============================================================
        self.play(*swap_caption("Esta es la\ncurva del dragón", size=44, color=COLOR_RESULT),
                  run_time=1.2)
        self.wait(2.8)

        # =============================================================
        # 6. CUATRO DRAGONES
        # =============================================================
        self.play(*swap_caption("Cuatro dragones\nencajan sin solaparse", size=36),
                  FadeOut(counter),
                  cam.animate.set_value(1.0), op4.animate.set_value(1.0),
                  run_time=4.0, rate_func=smooth)
        self.wait(2.4)

        # =============================================================
        # 7. DIMENSIÓN DEL BORDE
        # =============================================================
        dim = Text("Dimensión del borde ≈ 1.52", font_size=54, weight=BOLD, color=COLOR_RESULT)
        fit_width(dim).move_to(UP * STAT_Y)
        self.play(FadeIn(dim, shift=UP * 0.2), run_time=1.1)
        self.wait(3.0)

        # =============================================================
        # 8. CIERRE Y LOGO
        # =============================================================
        curve.clear_updaters()
        self.play(FadeOut(VGroup(curve, dim, cap_holder[0])), run_time=1.2)
        logo = MathTex(r"F_{GC}", font_size=150, color=COLOR_LOGO).move_to(ORIGIN)
        self.play(FadeIn(logo, scale=0.7), run_time=1.6)
        self.wait(2.5)