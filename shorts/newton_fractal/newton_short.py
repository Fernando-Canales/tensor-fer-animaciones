from manim import *
import numpy as np

# ---------------------------------------------------------------
# FORMATO: cuadro vertical 9:16 (1080x1920), igual que los otros shorts.
# Pon PORTRAIT = False para renderizar horizontal.
# Render: manim -qh --fps 60 newton_short.py NewtonShort
# (el zoom recalcula una imagen en cada fotograma: tarda unos minutos)
# ---------------------------------------------------------------
PORTRAIT = True
if PORTRAIT:
    config.pixel_width = 1080
    config.pixel_height = 1920
    config.frame_width = 6.0
    config.frame_height = 6.0 * 16 / 9


# ===============================================================
# MATEMÁTICAS (numpy puro)
# ===============================================================
# BEGIN-GEOM
# Método de Newton para f(z) = z^3 - 1:   z  ->  z - f(z)/f'(z) = (2 z^3 + 1) / (3 z^2)
ROOTS = np.array([1.0 + 0j, -0.5 + 0.8660254037844386j, -0.5 - 0.8660254037844386j])
ROOT_RGB = np.array([[88, 196, 221], [252, 214, 98], [252, 98, 85]], dtype=float)   # azul, amarillo, rojo


def newton_image(cx, cy, hh, nx, ny, aspect, maxit=40):
    """Cuencas de atracción de Newton para z^3 - 1.
    Cada píxel es un punto de partida z0 de la ventana (centro cx+icy, semialtura hh).
    Color = a qué raíz converge; brillo = cuántos pasos tarda (más oscuro = más lento)."""
    hw = hh * aspect
    xs = cx - hw + (np.arange(nx) + 0.5) * (2 * hw / nx)      # centro de cada píxel
    ys = cy + hh - (np.arange(ny) + 0.5) * (2 * hh / ny)
    Z = xs[None, :] + 1j * ys[:, None]
    idx = np.full(Z.shape, -1, dtype=np.int8)
    it = np.full(Z.shape, float(maxit))
    with np.errstate(all="ignore"):
        for k in range(maxit):
            z2 = Z * Z
            Z = Z - (Z * z2 - 1.0) / (3.0 * z2)
            for r in range(3):
                hit = (idx < 0) & (np.abs(Z - ROOTS[r]) < 1e-6)
                idx[hit] = r
                it[hit] = k
    shade = 0.30 + 0.70 * np.exp(-0.17 * (it - 2.0))
    rgb = np.zeros(Z.shape + (3,))
    ok = idx >= 0
    rgb[ok] = ROOT_RGB[idx[ok]] * shade[ok][:, None]
    return rgb, idx


def newton_orbit(z0, tol=1e-3, maxsteps=30):
    """Trayectoria de Newton desde z0 hasta acercarse a una raíz. Devuelve (puntos, índice de raíz)."""
    z = complex(z0)
    path = [z]
    for _ in range(maxsteps):
        z = z - (z ** 3 - 1) / (3 * z ** 2)
        path.append(z)
        d = np.abs(z - ROOTS)
        if d.min() < tol:
            return np.array(path), int(d.argmin())
    return np.array(path), -1

PALETTE_RGB = np.array([[88, 196, 221], [252, 214, 98], [252, 98, 85],
                        [120, 214, 130], [186, 140, 240], [250, 150, 70]], dtype=float)


def newton_poly_image(coeffs, cx, cy, hh, nx, ny, aspect, maxit=50):
    """Fractal de Newton de un polinomio cualquiera (coeficientes de mayor a menor grado).
    Color = raíz a la que converge (hasta 6 colores); negro = no converge a ninguna raíz
    (por ejemplo, si el método cae en un ciclo)."""
    coeffs = np.asarray(coeffs, dtype=float)
    roots = np.roots(coeffs)
    dcoeffs = np.polyder(coeffs)
    hw = hh * aspect
    xs = cx - hw + (np.arange(nx) + 0.5) * (2 * hw / nx)
    ys = cy + hh - (np.arange(ny) + 0.5) * (2 * hh / ny)
    Z = xs[None, :] + 1j * ys[:, None]
    idx = np.full(Z.shape, -1, dtype=np.int8)
    it = np.full(Z.shape, float(maxit))
    with np.errstate(all="ignore"):
        for k in range(maxit):
            Z = Z - np.polyval(coeffs, Z) / np.polyval(dcoeffs, Z)
            for r in range(len(roots)):
                hit = (idx < 0) & (np.abs(Z - roots[r]) < 1e-6)
                idx[hit] = r
                it[hit] = k
    shade = 0.30 + 0.70 * np.exp(-0.17 * (it - 2.0))
    rgb = np.zeros(Z.shape + (3,))
    ok = idx >= 0
    rgb[ok] = PALETTE_RGB[idx[ok] % len(PALETTE_RGB)] * shade[ok][:, None]
    return rgb, idx
# END-GEOM


class NewtonShort(Scene):
    def construct(self):
        # ---------------- Paleta ----------------
        TXT_BASE = ManimColor("#E1E1D5")
        COLOR_RESULT = YELLOW_D
        COLOR_LOGO = BLUE_C
        ROOT_COLORS = [ManimColor('#%02x%02x%02x' % tuple(int(v) for v in c)) for c in ROOT_RGB]

        W = config.frame_width

        # ---------------- Parámetros ----------------
        RC = np.array([0.0, 0.3])                    # centro de la imagen en pantalla
        RW, RH = 5.6, 6.4                            # tamaño de la imagen en pantalla
        HH0 = 1.6                                    # semialtura de la ventana compleja inicial
        ASPECT = RW / RH
        U = RH / 2 / HH0                             # unidades de pantalla por unidad compleja (=2)
        NX, NY = 560, 640                            # resolución de la imagen (bájala si va lento)
        TARGET = complex(0.48, 0.44)                 # punto de la frontera al que hacemos zoom
        ZOOM = 250.0                                 # aumento final
        ZOOM_T = 11.5                                # segundos de zoom

        def fit_width(m, frac=0.93):
            if m.width > W * frac:
                m.scale(W * frac / m.width)
            return m

        def sc(z):
            """Número complejo -> posición en pantalla (ventana inicial)."""
            return np.array([RC[0] + z.real * U, RC[1] + z.imag * U, 0.0])

        def upsample(rgb):
            """Bloques nítidos: repite cada celda hasta la resolución final (NX x NY)."""
            r = (np.arange(NY) * rgb.shape[0]) // NY
            c = (np.arange(NX) * rgb.shape[1]) // NX
            return rgb[r][:, c]

        def to_mobject(rgb):
            arr = np.clip(rgb, 0, 255).astype(np.uint8)
            m = ImageMobject(arr)
            m.stretch_to_fit_width(RW)
            m.stretch_to_fit_height(RH)
            m.move_to(np.array([RC[0], RC[1], 0.0]))
            m.set_z_index(1)
            return m

        # ---------------- Subtítulos ----------------
        cap_holder = [None]

        def make_caption(text, size=36, color=TXT_BASE):
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
        # 1. GANCHO
        # =============================================================
        title = Text("¿Puede una ecuación\ndibujar un fractal?",
                     font_size=40, weight=BOLD, color=TXT_BASE, line_spacing=1.3)
        fit_width(title).move_to(ORIGIN)
        self.play(Write(title), run_time=2.6)
        self.wait(1.4)
        self.play(FadeOut(title), run_time=0.9)

        # =============================================================
        # 2. EL PLANO COMPLEJO: z es un número complejo, un punto del plano
        # =============================================================
        def lab(tex, pos, size=25, color=TXT_BASE):
            m = MathTex(tex, font_size=size, color=color)
            m.move_to(pos)
            m.set_z_index(6)
            return m

        border = Rectangle(width=RW, height=RH, color=TXT_BASE, stroke_width=4)
        border.move_to(np.array([RC[0], RC[1], 0.0])).set_z_index(5)
        ax_re = Line(sc(complex(-HH0 * ASPECT, 0)), sc(complex(HH0 * ASPECT, 0)),
                     color=TXT_BASE, stroke_width=2, stroke_opacity=0.5)
        ax_im = Line(sc(complex(0, -HH0)), sc(complex(0, HH0)),
                     color=TXT_BASE, stroke_width=2, stroke_opacity=0.5)
        unit = Circle(radius=U, color=TXT_BASE, stroke_width=2, stroke_opacity=0.25)
        unit.move_to(sc(0j))
        ticks = VGroup(*[Line(sc(z) - d * 0.08, sc(z) + d * 0.08, color=TXT_BASE, stroke_width=2.5)
                         for z, d in [(1 + 0j, UP), (-1 + 0j, UP), (1j, RIGHT), (-1j, RIGHT)]])
        axis_labels = VGroup(
            lab(r"\mathrm{Re}", sc(complex(1.2, 0)) + UP * 0.38),
            lab(r"\mathrm{Im}", sc(complex(0, 1.5)) + RIGHT * 0.38),
            lab("-1", sc(complex(-1, 0)) + DOWN * 0.55, 29),
            lab("i", sc(complex(0, 1)) + RIGHT * 0.3, 29),
            lab("-i", sc(complex(0, -1)) + RIGHT * 0.32, 29),
            lab("1", sc(complex(1, 0)) + DOWN * 0.55, 29),
        )
        axes_grp = VGroup(ax_re, ax_im, unit, ticks, axis_labels)
        root_dots = VGroup(*[Dot(sc(ROOTS[k]), radius=0.17, color=ROOT_COLORS[k]) for k in range(3)])
        root_dots.set_z_index(6)
        root_labels = VGroup(
            lab(r"-\tfrac12+\tfrac{\sqrt3}{2}i", sc(ROOTS[1]) + UP * 0.5, 31, ROOT_COLORS[1]),
            lab(r"-\tfrac12-\tfrac{\sqrt3}{2}i", sc(ROOTS[2]) + DOWN * 0.5, 31, ROOT_COLORS[2]),
        )

        self.play(Create(border), Create(ax_re), Create(ax_im), Create(unit),
                  *swap_caption("z es un número complejo:\nun punto del plano"), run_time=1.6)
        self.play(FadeIn(ticks), FadeIn(axis_labels), run_time=1.2)

        # un número complejo cualquiera: z = x + iy
        zd = complex(0.8, 1.0)
        zdot = Dot(sc(zd), radius=0.13, color=WHITE).set_z_index(7)
        dash_x = DashedLine(sc(zd), sc(complex(zd.real, 0)), color=TXT_BASE, stroke_width=3)
        dash_y = DashedLine(sc(zd), sc(complex(0, zd.imag)), color=TXT_BASE, stroke_width=3)
        lab_x = lab("x", sc(complex(zd.real, 0)) + DOWN * 0.32, 31, YELLOW)
        lab_y = lab("y", sc(complex(0, zd.imag)) + LEFT * 0.3, 31, YELLOW)
        lab_z = lab("z=x+iy", sc(zd) + UP * 0.42 + LEFT * 0.35, 36, WHITE)
        demo = VGroup(zdot, dash_x, dash_y, lab_x, lab_y, lab_z)
        self.play(FadeIn(zdot, scale=3), Create(dash_x), Create(dash_y),
                  FadeIn(lab_x), FadeIn(lab_y), FadeIn(lab_z), run_time=1.8)
        self.wait(2.4)

        self.play(FadeOut(demo), *swap_caption("Tomemos una ecuación:\nz³ = 1"), run_time=1.0)
        self.wait(2.2)
        self.play(*swap_caption("Sus tres soluciones\nen el plano complejo"),
                  LaggedStart(*[FadeIn(d, scale=2) for d in root_dots], lag_ratio=0.7),
                  run_time=3.2)
        self.play(FadeIn(root_labels), run_time=1.2)
        self.wait(3.0)

        # =============================================================
        # 3. MÉTODO DE NEWTON-RAPHSON: primero las cuentas, luego los puntos
        # =============================================================
        path, r_end = newton_orbit(complex(-0.404, 0.117))
        plane_all = VGroup(border, axes_grp, root_dots, root_labels)
        self.play(FadeOut(plane_all),
                  *swap_caption("Método de\nNewton–Raphson", size=36, color=COLOR_RESULT),
                  run_time=1.2)
        general = MathTex(r"z_{n+1}=z_n-\frac{f(z_n)}{f'(z_n)}", font_size=33, color=TXT_BASE)
        fit_width(general).move_to(UP * 2.95)
        self.play(Write(general), run_time=2.2)
        self.wait(1.6)
        formula = MathTex(r"z_{n+1}=z_n-\frac{z_n^3-1}{3\,z_n^2}", font_size=33, color=TXT_BASE)
        fit_width(formula).move_to(UP * 1.55)
        self.play(*swap_caption("Con f(z) = z³ − 1\ny su derivada f′(z) = 3z²"),
                  Write(formula), run_time=2.4)
        self.wait(1.4)

        def cstr(z):
            return f"{z.real:.2f}{'+' if z.imag >= 0 else '-'}{abs(z.imag):.2f}i"

        rows = VGroup()
        for k, z in enumerate(path):
            if k == len(path) - 1 and abs(z - 1) < 0.01:
                t = "z_{%d}\\approx 1" % k
            else:
                t = "z_{%d}=%s" % (k, cstr(z))
            rows.add(MathTex(t, font_size=36, color=TXT_BASE))
        ROW_Y = [0.65, -0.25, -0.95, -1.55, -2.15, -2.75, -3.35]   # z1 ocupa el hueco alto de la fórmula
        LEFT_X = -1.5
        for row, y in zip(rows, ROW_Y):
            row.move_to(np.array([0.0, y, 0.0])).align_to(np.array([LEFT_X, 0.0, 0.0]), LEFT)
        sym = MathTex(r"z_1=z_0-\frac{z_0^3-1}{3\,z_0^2}", font_size=33, color=YELLOW)
        sym.move_to(np.array([0.0, ROW_Y[1], 0.0])).align_to(np.array([LEFT_X, 0.0, 0.0]), LEFT)

        self.play(*swap_caption("Empieza con un número\ncomplejo cualquiera"),
                  FadeIn(rows[0], shift=UP * 0.15), run_time=1.2)
        self.wait(1.2)
        self.play(*swap_caption("Aplica la fórmula…"), FadeIn(sym, shift=UP * 0.15), run_time=1.2)
        self.wait(1.8)
        self.play(ReplacementTransform(sym, rows[1]), run_time=1.4)
        self.wait(1.0)
        self.play(*swap_caption("…y otra vez…"), run_time=0.8)
        for k in range(2, len(rows)):
            self.play(FadeIn(rows[k], shift=UP * 0.15), run_time=0.9)
            self.wait(0.6)
        self.wait(1.4)

        # ... y ahora, esos números como puntos del plano
        start = Dot(sc(path[0]), radius=0.13, color=WHITE)
        start.set_z_index(7)
        self.play(FadeOut(rows), FadeOut(formula), FadeOut(general),
                  *swap_caption("Cada número complejo\nes un punto del plano"), run_time=1.2)
        self.play(FadeIn(border), FadeIn(axes_grp), FadeIn(root_dots), run_time=1.4)
        self.wait(0.6)

        Z_LABEL_OFFSET = {1: (-0.30, 0.42), 2: (0.42, -0.15), 3: (-0.42, 0.12), 4: (0.42, -0.10)}

        def walk_path(p, labels=True, t_arrow=1.0, t_dot=0.5, t_wait=0.5):
            """Recorre la trayectoria de Newton paso a paso: flecha, punto (y etiqueta z_k)."""
            tr = VGroup()
            for k in range(len(p) - 1):
                a, b = sc(p[k]), sc(p[k + 1])
                step = Dot(b, radius=0.07, color=WHITE)
                step.set_z_index(6)
                if np.linalg.norm(b - a) < 0.25:           # pasos diminutos: solo el punto
                    self.play(FadeIn(step, scale=2), run_time=0.4)
                    tr.add(step)
                    continue
                arr = Arrow(a, b, buff=0.09, stroke_width=5, color=WHITE,
                            max_tip_length_to_length_ratio=0.2, max_stroke_width_to_length_ratio=8)
                arr.set_z_index(6)
                self.play(GrowArrow(arr), run_time=t_arrow)
                if labels and (k + 1) in Z_LABEL_OFFSET:   # z5 y z6 caen sobre la solución: sin etiqueta
                    off = Z_LABEL_OFFSET[k + 1]
                    lp = b + np.array([off[0], off[1], 0.0])
                    lp[0] = np.clip(lp[0], -RW / 2 + 0.3, RW / 2 - 0.3)
                    lp[1] = np.clip(lp[1], RC[1] - RH / 2 + 0.3, RC[1] + RH / 2 - 0.3)
                    zl = lab("z_%d" % (k + 1), lp, 31, WHITE)
                    self.play(FadeIn(step, scale=2), FadeIn(zl), run_time=t_dot)
                    tr.add(arr, step, zl)
                else:
                    self.play(FadeIn(step, scale=2), run_time=t_dot)
                    tr.add(arr, step)
                self.wait(t_wait)
            return tr

        zlab0 = lab("z_0", sc(path[0]) + UP * 0.38 + LEFT * 0.2, 31, WHITE)
        self.play(FadeIn(start, scale=3), FadeIn(zlab0), run_time=1.0)
        self.wait(0.8)
        trail = walk_path(path, labels=True, t_arrow=1.2, t_dot=0.6, t_wait=0.8)
        trail.add(zlab0)
        self.wait(0.8)

        names = ["la azul", "la amarilla", "la roja"]
        self.play(*swap_caption(f"Se acerca a una solución,\n{names[r_end]}: pinta el punto"),
                  start.animate.set_color(ROOT_COLORS[r_end]).scale(1.3),
                  FadeOut(trail), run_time=1.6)
        self.wait(0.8)

        # ojo: ¿era esa la solución más cercana? (se muestra DESPUÉS del proceso, para cada punto)
        def show_nearest(z0, r_final, dot, first=False):
            near = int(np.argmin(np.abs(ROOTS - z0)))
            if near == r_final:
                return
            nl = DashedLine(sc(z0), sc(ROOTS[near]), color=ROOT_COLORS[near], stroke_width=5)
            nl.set_z_index(6)
            self.play(*swap_caption(f"Estaba más cerca de {names[near]},\npero acabó en {names[r_final]}"),
                      Create(nl), run_time=1.8 if first else 1.3)
            self.wait(2.0 if first else 1.1)
            self.play(FadeOut(nl), run_time=0.6)

        show_nearest(path[0], r_end, start, first=True)
        self.wait(0.4)

        # otros dos puntos, más rápido
        painted = VGroup(start)
        extra_caps = ["Ahora, otro z₀ para\nla segunda solución", "Y otro z₀ para\nla tercera solución"]
        for z0, cap2 in zip((complex(0.167, -0.351), complex(0.497, 0.913)), extra_caps):
            p2, r2 = newton_orbit(z0)
            s2 = Dot(sc(p2[0]), radius=0.13, color=WHITE)
            s2.set_z_index(7)
            self.play(*swap_caption(cap2), FadeIn(s2, scale=3), run_time=1.2)
            self.wait(0.8)
            tr2 = walk_path(p2, labels=False, t_arrow=1.0, t_dot=0.5, t_wait=0.5)
            self.wait(0.4)
            self.play(s2.animate.set_color(ROOT_COLORS[r2]).scale(1.3), FadeOut(tr2), run_time=1.0)
            painted.add(s2)
            show_nearest(z0, r2, s2)
        self.wait(0.6)

        # =============================================================
        # 4. REPETIR CON TODOS LOS PUNTOS DEL PLANO
        # =============================================================
        # Una rejilla de puntos de partida (10 x 11 = 110): cada uno hace su recorrido y se pinta
        GX, GY = 10, 11
        rgb_g, idx_g = newton_image(0.0, 0.0, HH0, GX, GY, ASPECT, 40)
        cw, ch = 2 * HH0 * ASPECT / GX, 2 * HH0 / GY
        grid_dots = VGroup()
        real_colors = []
        for j in range(GY):
            for i in range(GX):
                z = complex(-HH0 * ASPECT + (i + 0.5) * cw, HH0 - (j + 0.5) * ch)
                d = Dot(sc(z), radius=0.065, color=WHITE)
                d.set_z_index(7)
                grid_dots.add(d)
                real_colors.append(ROOT_COLORS[int(idx_g[j, i])])
        self.play(*swap_caption("Haz lo mismo con\nmuchos puntos de partida"),
                  FadeOut(painted), FadeOut(axes_grp),
                  LaggedStart(*[FadeIn(d, scale=2) for d in grid_dots], lag_ratio=0.02),
                  run_time=3.0)
        self.wait(0.8)
        self.play(*swap_caption("Cada uno acaba en una solución:\nse pinta de su color"),
                  *[d.animate.set_fill(c) for d, c in zip(grid_dots, real_colors)],
                  run_time=1.8)
        self.wait(1.4)
        img0 = to_mobject(upsample(rgb_g))
        self.play(FadeIn(img0), run_time=1.4)                  # cada punto pinta su cuadrito
        self.wait(0.8)
        self.play(*swap_caption("Con más y más puntos…"), FadeOut(grid_dots), run_time=1.0)
        current = img0
        for nx, ny in [(14, 16), (28, 32), (56, 64), (112, 128), (280, 320)]:
            rgb, _ = newton_image(0.0, 0.0, HH0, nx, ny, ASPECT, 40)
            new = to_mobject(upsample(rgb))
            self.remove(current)
            self.add(new)
            current = new
            self.wait(0.8 if nx < 100 else 0.9)
        rgb, _ = newton_image(0.0, 0.0, HH0, NX, NY, ASPECT, 40)
        final_img = to_mobject(rgb)
        self.remove(current)
        self.add(final_img)
        self.play(FadeOut(root_dots), run_time=0.8)
        self.wait(0.6)

        # =============================================================
        # 5. NOMBRE
        # =============================================================
        self.play(*swap_caption("Fractal de Newton\nde la ecuación  z³ = 1", size=36, color=COLOR_RESULT),
                  run_time=1.2)
        self.wait(2.6)

        # =============================================================
        # 6. ZOOM A LA FRONTERA (un solo movimiento continuo)
        # =============================================================
        zu = ValueTracker(0.0)                       # progreso del zoom, 0 a 1

        def window(u):
            """Centro y semialtura de la ventana compleja. El objetivo se desplaza suavemente
            hacia el centro de la imagen mientras la ventana se encoge."""
            s = u * u * (3 - 2 * u)
            hh = HH0 * ZOOM ** (-u)
            c = TARGET - TARGET * (1 - s) * hh / HH0
            return c, hh

        def make_zoom():
            u = zu.get_value()
            c, hh = window(u)
            rgb, _ = newton_image(c.real, c.imag, hh, NX, NY, ASPECT, int(40 + 40 * u))
            return to_mobject(rgb)

        zoom_img = always_redraw(make_zoom)
        zoom_counter = always_redraw(
            lambda: Text(f"Zoom ×{int(round(ZOOM ** zu.get_value())):,}".replace(",", "."),
                         font_size=33, weight=BOLD, color=GREEN_C).move_to(DOWN * 3.55)
        )
        self.remove(final_img)
        self.add(zoom_img, zoom_counter)

        FD = 0.7
        sched = [
            ("Las fronteras no son rectas:\nson un fractal", 0.0, 3.8),
            ("Cerca de cualquier punto\nde la frontera…", 3.8, 7.6),
            ("…están los tres\ncolores a la vez", 7.6, 1e9),
        ]

        def win(t, a, b):
            fin = min(max((t - a) / FD, 0.0), 1.0)
            fout = min(max((t - b) / FD, 0.0), 1.0)
            return fin * (1.0 - fout)

        old_cap = cap_holder[0]
        timed = []
        for text, a_, b_ in sched:
            c = make_caption(text)
            c.set_opacity(0)
            c.add_updater(lambda m, a_=a_, b_=b_: m.set_opacity(win(zu.get_value() * ZOOM_T, a_, b_)))
            self.add(c)
            timed.append(c)

        self.play(AnimationGroup(
            zu.animate(run_time=ZOOM_T, rate_func=linear).set_value(1.0),   # un solo movimiento
            FadeOut(old_cap, run_time=0.7),
            lag_ratio=0,
        ))
        zoom_img.clear_updaters()                    # imagen congelada: el resto va rápido
        zoom_counter.clear_updaters()
        for c in timed[:-1]:
            self.remove(c)
        timed[-1].clear_updaters()
        timed[-1].set_opacity(1)
        cap_holder[0] = timed[-1]
        self.wait(2.2)

        # =============================================================
        # 7. HAY MUCHOS FRACTALES DE NEWTON: uno por cada ecuación
        # =============================================================
        specs = [([1, 0, 0, 0, -1], r"z^4-1", 1.6),
                 ([1, 0, 0, 0, 0, -1], r"z^5-1", 1.6),
                 ([1, 0, 0, 0, 0, 0, -1], r"z^6-1", 1.6),
                 ([1, 0, -2, 2], r"z^3-2z+2", 2.2)]
        pos = [(-1.5, 2.15), (1.5, 2.15), (-1.5, -1.0), (1.5, -1.0)]
        thumbs = Group()
        for (co, lab, hh), (px, py) in zip(specs, pos):
            rgb, _ = newton_poly_image(co, 0.0, 0.0, hh, 270, 270, 1.0, 50)
            im = ImageMobject(np.clip(rgb, 0, 255).astype(np.uint8))
            im.stretch_to_fit_width(2.3)
            im.stretch_to_fit_height(2.3)
            im.move_to(np.array([px, py, 0.0]))
            frame = Square(side_length=2.3, color=TXT_BASE, stroke_width=2.5).move_to(im.get_center())
            label = MathTex(lab, font_size=33, color=TXT_BASE).next_to(frame, DOWN, buff=0.2)
            thumbs.add(Group(im, frame, label))
        self.play(FadeOut(Group(zoom_img, border, zoom_counter)),
                  *swap_caption("Varias ecuaciones tienen\nsu propio fractal de Newton"),
                  run_time=1.2)
        self.play(LaggedStart(*[FadeIn(g) for g in thumbs], lag_ratio=0.3), run_time=2.4)
        self.wait(3.6)

        # =============================================================
        # 8. CIERRE Y LOGO
        # =============================================================
        self.play(FadeOut(Group(cap_holder[0], thumbs)), run_time=1.2)
        logo = MathTex(r"F_{GC}", font_size=150, color=COLOR_LOGO).move_to(ORIGIN)
        self.play(FadeIn(logo, scale=0.7), run_time=1.2)
        self.wait(2.5)