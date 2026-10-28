from manim import *
import numpy as np

# ---------------------------------------------------------------
# SHORT SIN PALABRAS: la misma función en coordenadas rectangulares y polares
# FORMATO: cuadro vertical 9:16 (1080x1920)
# Render: manim -qh --fps 60 trig_pairs_short.py TrigPairsShort
# ---------------------------------------------------------------
PORTRAIT = True
if PORTRAIT:
    config.pixel_width = 1080
    config.pixel_height = 1920
    config.frame_width = 6.0
    config.frame_height = 6.0 * 16 / 9


# ===============================================================
# GEOMETRÍA (numpy puro; se puede probar sin Manim)
# ===============================================================
# BEGIN-GEOM
# Disposición (unidades de Manim; el cuadro mide 6.0 x 10.667)
RECT_CX, RECT_CY = 0.0, 2.9      # gráfica rectangular (arriba)
RECT_W, RECT_H = 5.0, 2.3
POL_CX, POL_CY = 0.0, -1.35      # gráfica polar (abajo)
POL_R = 2.3

PI = np.pi
SPECS = [
    # r = cos(3θ): rosa de 3 pétalos (se cierra en θ = π)
    dict(f=lambda t: np.cos(3 * t), T=PI, ymin=-1.0, ymax=1.0, rmax=1.0,
         color="#58C4DD", tex=r"r=\cos 3\theta", xstep=PI / 2),
    # r = 1 + cos(θ): cardioide (r nunca es negativo)
    dict(f=lambda t: 1 + np.cos(t), T=2 * PI, ymin=0.0, ymax=2.0, rmax=2.0,
         color="#F4D35E", tex=r"r=1+\cos\theta", xstep=PI),
    # r = cos(5θ/2): rosa que sólo se cierra tras dos vueltas (θ de 0 a 4π)
    dict(f=lambda t: np.cos(2.5 * t), T=4 * PI, ymin=-1.0, ymax=1.0, rmax=1.0,
         color="#78DCB4", tex=r"r=\cos\tfrac{5\theta}{2}", xstep=PI),
]


def samples(spec):
    """θ y r = f(θ) en una malla fina: 360 puntos por cada π de recorrido."""
    n = int(round(360 * spec["T"] / PI)) + 1
    th = np.linspace(0.0, spec["T"], n)
    return th, spec["f"](th)


def rect_xy(spec, th, val):
    """(θ, f) -> posición en la gráfica rectangular (con un margen vertical del 15 %)."""
    span = spec["ymax"] - spec["ymin"]
    pad = 0.15 * span
    lo, hi = spec["ymin"] - pad, spec["ymax"] + pad
    x = RECT_CX - RECT_W / 2 + np.asarray(th) / spec["T"] * RECT_W
    y = RECT_CY - RECT_H / 2 + (np.asarray(val) - lo) / (hi - lo) * RECT_H
    return x, y


def polar_xy(spec, th, val):
    """(θ, r) -> posición en la gráfica polar (r < 0 se dibuja al lado opuesto del rayo)."""
    u = POL_R / spec["rmax"]
    th = np.asarray(th)
    val = np.asarray(val)
    return POL_CX + u * val * np.cos(th), POL_CY + u * val * np.sin(th)
# END-GEOM


# ===============================================================
# ESCENA
# ===============================================================
class TrigPairsShort(Scene):
    def construct(self):
        COLOR_AXIS = GREY_B
        COLOR_GRID = GREY_D
        COLOR_LOGO = BLUE_C

        # ---------- utilidades ----------
        def P3(x, y):
            return np.array([float(x), float(y), 0.0])

        def pts3(x, y):
            return np.column_stack([x, y, np.zeros_like(x)])

        def x_tex(k):
            """Etiqueta de un múltiplo de π/2."""
            m = int(round(k * 2))          # k en unidades de π -> m en unidades de π/2
            if m == 1:
                return r"\tfrac{\pi}{2}"
            if m % 2 == 0:
                return r"\pi" if m == 2 else r"%d\pi" % (m // 2)
            return r"\tfrac{%d\pi}{2}" % m

        def build_static(spec, labels=True, curves=False):
            """Ejes + cuadrícula de las dos gráficas (y, si curves, las curvas completas)."""
            g = VGroup()       # parte rectangular
            gp = VGroup()      # parte polar
            th, r = samples(spec)
            # --- rectangular ---
            x0, y0 = rect_xy(spec, 0.0, 0.0)
            x1, _ = rect_xy(spec, spec["T"], 0.0)
            ax_x = Line(P3(x0 - 0.1, y0), P3(x1 + 0.1, y0), color=COLOR_AXIS, stroke_width=2.5)
            _, ytop = rect_xy(spec, 0.0, spec["ymax"] + 0.15 * (spec["ymax"] - spec["ymin"]))
            _, ybot = rect_xy(spec, 0.0, spec["ymin"] - 0.15 * (spec["ymax"] - spec["ymin"]))
            ax_y = Line(P3(x0, ybot), P3(x0, ytop), color=COLOR_AXIS, stroke_width=2.5)
            g.add(ax_x, ax_y)
            # marcas en x (múltiplos de xstep)
            k = 1
            while k * spec["xstep"] <= spec["T"] + 1e-9:
                tx, _ = rect_xy(spec, k * spec["xstep"], 0.0)
                g.add(Line(P3(tx, y0 - 0.06), P3(tx, y0 + 0.06), color=COLOR_AXIS, stroke_width=2.5))
                if labels:
                    g.add(MathTex(x_tex(k * spec["xstep"] / PI), font_size=26, color=COLOR_AXIS)
                          .move_to(P3(tx, y0 - 0.28)))
                k += 1
            # marcas en y (enteros distintos de cero)
            for v in range(int(np.floor(spec["ymin"])), int(np.ceil(spec["ymax"])) + 1):
                if v == 0:
                    continue
                _, ty = rect_xy(spec, 0.0, float(v))
                g.add(Line(P3(x0 - 0.06, ty), P3(x0 + 0.06, ty), color=COLOR_AXIS, stroke_width=2.5))
                if labels:
                    g.add(MathTex(str(v), font_size=26, color=COLOR_AXIS).move_to(P3(x0 - 0.25, ty)))
            if labels:
                g.add(MathTex(r"\theta", font_size=30, color=COLOR_AXIS).move_to(P3(x1 + 0.24, y0)))
            # --- polar ---
            c = P3(POL_CX, POL_CY)
            for frac in (0.5, 1.0):
                gp.add(Circle(radius=POL_R * frac, color=COLOR_GRID if frac < 1 else COLOR_AXIS,
                             stroke_width=1.8 if frac < 1 else 2.5).move_to(c))
            for a in np.arange(12) * PI / 6:
                gp.add(Line(c, c + POL_R * P3(np.cos(a), np.sin(a)), color=COLOR_GRID, stroke_width=1.2)
                      .set_opacity(0.6))
            gp.add(Line(c - P3(POL_R + 0.1, 0), c + P3(POL_R + 0.1, 0), color=COLOR_AXIS, stroke_width=2.5))
            gp.add(Line(c - P3(0, POL_R + 0.1), c + P3(0, POL_R + 0.1), color=COLOR_AXIS, stroke_width=2.5))
            if curves:
                rx, ry = rect_xy(spec, th, r)
                px, py = polar_xy(spec, th, r)
                g.add(VMobject(color=spec["color"], stroke_width=5).set_points_as_corners(pts3(rx, ry)))
                gp.add(VMobject(color=spec["color"], stroke_width=5).set_points_as_corners(pts3(px, py)))
            return VGroup(g, gp)       # [0] = rectangular, [1] = polar

        def shrink(grp, s, center):
            """Escala un grupo y su grosor de línea (Manim no escala el trazo por sí solo)."""
            grp.scale(s)
            for m in grp.family_members_with_points():
                if m.get_stroke_width() > 0:
                    m.set_stroke(width=m.get_stroke_width() * s)
            grp.move_to(center)
            return grp

        # ---------- un par: dibujo sincronizado ----------
        def play_pair(spec, dur):
            th_arr, r_arr = samples(spec)
            rx, ry = rect_xy(spec, th_arr, r_arr)
            px, py = polar_xy(spec, th_arr, r_arr)
            RP, PP = pts3(rx, ry), pts3(px, py)
            N = len(th_arr)
            T = spec["T"]
            col = spec["color"]

            static = build_static(spec)
            formula = MathTex(spec["tex"], font_size=44, color=col).move_to(P3(0, 4.5))
            self.play(FadeIn(static), Write(formula), run_time=1.5)

            tr = ValueTracker(0.0)

            def state():
                t = tr.get_value()
                i = int(np.floor(t / T * (N - 1)))
                i = max(0, min(i, N - 2))
                v = float(spec["f"](t))
                return t, i, v

            def rect_trace():
                t, i, v = state()
                ex, ey = rect_xy(spec, t, v)
                pts = np.vstack([RP[: i + 1], P3(ex, ey)])
                return VMobject(color=col, stroke_width=5).set_points_as_corners(pts).set_z_index(3)

            def polar_trace():
                t, i, v = state()
                ex, ey = polar_xy(spec, t, v)
                pts = np.vstack([PP[: i + 1], P3(ex, ey)])
                return VMobject(color=col, stroke_width=5).set_points_as_corners(pts).set_z_index(3)

            def rect_dot():
                t, i, v = state()
                ex, ey = rect_xy(spec, t, v)
                return Dot(P3(ex, ey), radius=0.095, color=WHITE).set_z_index(6)

            def polar_dot():
                t, i, v = state()
                ex, ey = polar_xy(spec, t, v)
                return Dot(P3(ex, ey), radius=0.095, color=WHITE).set_z_index(6)

            def connector():
                t, i, v = state()
                ax_, ay_ = rect_xy(spec, t, v)
                bx_, by_ = polar_xy(spec, t, v)
                return Line(P3(ax_, ay_), P3(bx_, by_), color=WHITE, stroke_width=2).set_opacity(0.3).set_z_index(2)

            def droplines():
                t, i, v = state()
                ex, ey = rect_xy(spec, t, v)
                _, y0 = rect_xy(spec, t, 0.0)
                return Line(P3(ex, y0), P3(ex, ey), color=col, stroke_width=2).set_opacity(0.45).set_z_index(2)

            def theta_ray():
                t, i, v = state()
                c = P3(POL_CX, POL_CY)
                return Line(c, c + POL_R * P3(np.cos(t), np.sin(t)), color=WHITE, stroke_width=2) \
                    .set_opacity(0.28).set_z_index(2)

            def radius_seg():
                t, i, v = state()
                ex, ey = polar_xy(spec, t, v)
                return Line(P3(POL_CX, POL_CY), P3(ex, ey), color=col, stroke_width=4).set_z_index(4)

            dyn = [always_redraw(f) for f in
                   (connector, droplines, theta_ray, radius_seg, rect_trace, polar_trace, rect_dot, polar_dot)]
            self.add(*dyn)
            self.play(tr.animate.set_value(T), run_time=dur, rate_func=linear)
            self.wait(1.0)
            for m in dyn:                      # sin actualizadores, para que FadeOut pueda atenuarlos
                m.clear_updaters()
            self.play(FadeOut(Group(*dyn, static, formula)), run_time=0.8)
            self.remove(*dyn)

        # =============================================================
        # TRES PARES (sin palabras)
        # =============================================================
        # --- título ---
        title = Text("Funciones\ntrigonométricas", font_size=60, line_spacing=0.9, color=WHITE).move_to(P3(0, 0.9))
        if title.width > 5.2:
            title.scale_to_fit_width(5.2)
        wave = ParametricFunction(lambda t: P3(t, 0.32 * np.sin(2.5 * t)), t_range=[-2.2, 2.2],
                                  color=BLUE_C, stroke_width=6).move_to(P3(0, -0.9))
        wave.set_color_by_gradient("#58C4DD", "#F4D35E", "#78DCB4")
        self.play(Write(title), Create(wave), run_time=1.8)
        self.wait(1.8)
        self.play(FadeOut(Group(title, wave)), run_time=0.8)

        play_pair(SPECS[0], 6.5)
        play_pair(SPECS[1], 6.5)
        play_pair(SPECS[2], 11.0)

        # =============================================================
        # TRÍPTICO FINAL: los tres pares juntos
        # =============================================================
        # tres filas apiladas en vertical; en cada fila, la rectangular a la izquierda y la polar a la derecha
        tri = []
        for spec, yc in zip(SPECS, (2.85, 0.15, -2.55)):
            st = build_static(spec, labels=False, curves=True)
            rg, pg = st[0], st[1]
            shrink(rg, 0.46, P3(-1.25, yc))
            shrink(pg, 0.46, P3(1.35, yc))
            tri.append(VGroup(rg, pg))
        self.play(LaggedStart(*[FadeIn(g, scale=0.9) for g in tri], lag_ratio=0.35), run_time=2.2)
        self.wait(2.5)

        # =============================================================
        # CIERRE Y LOGO
        # =============================================================
        self.play(FadeOut(Group(*tri)), run_time=1.0)
        logo = MathTex(r"F_{GC}", font_size=150, color=COLOR_LOGO).move_to(ORIGIN)
        self.play(FadeIn(logo, scale=0.7), run_time=1.2)
        self.wait(2.5)