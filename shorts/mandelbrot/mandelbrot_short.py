from manim import *
import numpy as np

# ---------------------------------------------------------------
# FORMATO: cuadro vertical 9:16 (1080x1920)
# Render: manim -qh --fps 60 mandelbrot_short.py MandelbrotDeepDiveShort
# (el zoom recalcula una imagen en cada fotograma, pero es rápido: ~0.1 s por fotograma)
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
PAL_POS = np.array([0.0, 0.25, 0.5, 0.75, 1.0])
PAL_RGB = np.array([[22, 34, 110], [88, 196, 221], [120, 220, 180], [252, 214, 98], [22, 34, 110]],
                   dtype=float)


def mandelbrot_mu(cx, cy, hw, nx, ny, maxit=100, R=16.0):
    """Conjunto de Mandelbrot: para cada c de la ventana (centro cx+i·cy, semilado hw) se itera
    z -> z^2 + c desde z = 0. Devuelve el 'tiempo de escape suavizado' mu (>= 0), o -1 si
    no escapó en maxit pasos (dentro del conjunto)."""
    xs = cx - hw + (np.arange(nx) + 0.5) * (2 * hw / nx)          # centro de cada píxel
    ys = cy + hw - (np.arange(ny) + 0.5) * (2 * hw / ny)
    c = (xs[None, :] + 1j * ys[:, None]).ravel()
    z = np.zeros_like(c)
    idx = np.arange(c.size)
    res = np.full(c.size, -1.0)
    for n in range(maxit):
        z = z * z + c
        mag2 = z.real ** 2 + z.imag ** 2
        esc = mag2 > R * R
        if esc.any():
            m = n + 1 - np.log(np.log(np.sqrt(mag2[esc]))) / np.log(2.0)   # suavizado
            res[idx[esc]] = np.maximum(m, 0.0)
            keep = ~esc
            z, c, idx = z[keep], c[keep], idx[keep]                         # solo seguimos con los que no han escapado
            if z.size == 0:
                break
    return res.reshape(ny, nx)


def colorize(mu, period=24.0):
    """Dentro del conjunto: negro. Fuera: paleta cíclica según el tiempo de escape."""
    t = (mu / period) % 1.0
    rgb = np.stack([np.interp(t, PAL_POS, PAL_RGB[:, k]) for k in range(3)], axis=-1)
    rgb[mu < 0] = 0.0
    return rgb


def orbit(c, n):
    """z_0 = 0, z_{k+1} = z_k^2 + c."""
    z = 0j
    out = [z]
    for _ in range(n):
        z = z * z + c
        out.append(z)
    return out
# END-GEOM


class MandelbrotDeepDiveShort(Scene):
    def construct(self):
        # ---------------- Paleta ----------------
        TXT_BASE = ManimColor("#E1E1D5")
        COLOR_MATH = BLUE_C
        COLOR_RESULT = YELLOW_D
        COLOR_LOGO = BLUE_C
        COLOR_ORBIT = GREEN_C
        COLOR_EXPLODE = RED_C

        W = config.frame_width

        # ---------------- Parámetros ----------------
        RC = np.array([0.0, 0.2])                    # centro del plano en pantalla
        S = 5.0                                      # lado del plano en pantalla
        NPIX = 576                                   # resolución de la imagen (bájala si va lento)
        C_A = complex(-0.4, 0.4)                     # caso 1: dentro del conjunto (cardioide principal)
        C_B = complex(0.4, 0.5)                      # caso 2: se escapa
        M_CEN, M_HW = -0.6 + 0j, 1.5                 # ventana del conjunto completo
        TARGET = complex(-1.7549, 0.0)               # copia pequeña del conjunto (isla de periodo 3)
        ZOOM = 45.0
        ZOOM_T = 12.0

        def fit_width(m, frac=0.93):
            if m.width > W * frac:
                m.scale(W * frac / m.width)
            return m

        def P(z, cen, hw):
            """Número complejo -> posición en pantalla, para una ventana de centro cen y semilado hw."""
            return np.array([RC[0] + (z.real - cen.real) / hw * S / 2,
                             RC[1] + (z.imag - cen.imag) / hw * S / 2, 0.0])

        def lab(tex, pos, size=30, color=TXT_BASE):
            m = MathTex(tex, font_size=size, color=color)
            m.move_to(pos)
            m.set_z_index(6)
            return m

        def make_plane(cen, hw, re_ticks, im_ticks):
            """Plano complejo con marco, ejes, marcas y etiquetas Re / Im."""
            g = VGroup()
            frame = Square(side_length=S, color=TXT_BASE, stroke_width=4).move_to(np.array([*RC, 0.0]))
            frame.set_z_index(5)
            axes = VGroup()
            if abs(cen.imag) < hw:
                axes.add(Line(P(complex(cen.real - hw, 0), cen, hw), P(complex(cen.real + hw, 0), cen, hw),
                              color=TXT_BASE, stroke_width=2, stroke_opacity=0.5))
            if abs(cen.real) < hw:
                axes.add(Line(P(complex(0, cen.imag - hw), cen, hw), P(complex(0, cen.imag + hw), cen, hw),
                              color=TXT_BASE, stroke_width=2, stroke_opacity=0.5))
            labels = VGroup(
                lab(r"\mathrm{Re}", P(complex(cen.real + hw, 0), cen, hw) + LEFT * 0.35 + UP * 0.28),
                lab(r"\mathrm{Im}", P(complex(0, cen.imag + hw), cen, hw) + RIGHT * 0.35 + DOWN * 0.25),
            )
            for v in re_ticks:
                p = P(complex(v, 0), cen, hw)
                axes.add(Line(p + DOWN * 0.07, p + UP * 0.07, color=TXT_BASE, stroke_width=2.5))
                labels.add(lab(str(v).replace("-", "-"), p + DOWN * 0.3, 28))
            for v in im_ticks:
                p = P(complex(0, v), cen, hw)
                axes.add(Line(p + LEFT * 0.07, p + RIGHT * 0.07, color=TXT_BASE, stroke_width=2.5))
                tex = ("%si" % ("" if abs(v) == 1 else abs(v))) if v > 0 else ("-%si" % ("" if abs(v) == 1 else abs(v)))
                labels.add(lab(tex, p + RIGHT * 0.32, 28))
            return frame, VGroup(axes, labels)

        def upsample(rgb):
            """Bloques nítidos: repite cada celda hasta NPIX x NPIX."""
            r = (np.arange(NPIX) * rgb.shape[0]) // NPIX
            c = (np.arange(NPIX) * rgb.shape[1]) // NPIX
            return rgb[r][:, c]

        def to_mobject(rgb):
            m = ImageMobject(np.clip(rgb, 0, 255).astype(np.uint8))
            m.stretch_to_fit_width(S)
            m.stretch_to_fit_height(S)
            m.move_to(np.array([*RC, 0.0]))
            m.set_z_index(1)
            return m

        def rgb_to_manim(c):
            return ManimColor("#%02x%02x%02x" % tuple(int(round(v)) for v in c))

        # ---------------- Subtítulos ----------------
        cap_holder = [None]

        def make_caption(text, size=48, color=TXT_BASE):
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
        # 1. GANCHO / TÍTULO INICIAL
        # =============================================================
        titulo = Text("¿Cómo nace el fractal\nmás famoso del mundo?", font_size=52, weight=BOLD,
                      color=TXT_BASE, line_spacing=1.3)
        fit_width(titulo).move_to(ORIGIN)
        self.play(Write(titulo), run_time=1.8)
        self.wait(1.5)
        self.play(FadeOut(titulo), run_time=0.8)

        # =============================================================
        # 2. LA REGLA
        # =============================================================
        math_eq = MathTex(r"z_{n+1} = z_n^2 + c", font_size=84, color=TXT_BASE).move_to(UP * 0.3)
        fit_width(math_eq)
        self.play(Write(math_eq), *swap_caption("La regla de oro\n(partiendo de z₀ = 0)", color=COLOR_MATH),
                  run_time=1.8)
        self.wait(2.0)
        self.play(*swap_caption("z y c son números complejos:\npuntos del plano"), run_time=1.0)
        self.wait(2.4)
        self.play(FadeOut(math_eq), run_time=0.8)

        # =============================================================
        # 3. CASO 1: EL PUNTO ATRAPADO  (c = -0.4 + 0.4i, dentro del conjunto)
        # =============================================================
        HW_A = 1.2
        frame_a, axes_a = make_plane(0j, HW_A, [-1, 1], [-1, 1])
        PA = lambda z: P(z, 0j, HW_A)
        c_dot_a = Dot(PA(C_A), color=YELLOW, radius=0.1).set_z_index(7)
        c_lab_a = lab("c", PA(C_A) + UP * 0.32 + LEFT * 0.15, 40, YELLOW)
        self.play(*swap_caption("Caso 1: c = −0.4 + 0.4i", color=COLOR_ORBIT),
                  Create(frame_a), FadeIn(axes_a), run_time=1.4)
        self.play(FadeIn(c_dot_a, scale=2), FadeIn(c_lab_a), run_time=0.8)

        orb_a = orbit(C_A, 45)
        z_line_y = RC[1] - S / 2 - 0.55

        def z_text(tex, color):
            m = MathTex(tex, font_size=40, color=color).move_to(np.array([0.0, z_line_y, 0.0]))
            return fit_width(m)

        def cstr(z):
            return f"{z.real:.2f}{'+' if z.imag >= 0 else '-'}{abs(z.imag):.2f}i"

        z_cur = z_text(r"z_0=0", COLOR_ORBIT)
        origin_a = Dot(PA(0j), color=COLOR_ORBIT, radius=0.09).set_z_index(7)
        self.play(FadeIn(origin_a, scale=2), FadeIn(z_cur), run_time=0.8)
        self.wait(0.6)

        trail_a = VGroup(origin_a)
        prev = PA(0j)
        for k in range(1, 5):
            nxt = PA(orb_a[k])
            ln = Line(prev, nxt, color=COLOR_ORBIT, stroke_width=3.5).set_z_index(6)
            dt = Dot(nxt, color=COLOR_ORBIT, radius=0.08).set_z_index(7)
            z_new = z_text("z_{%d}=%s" % (k, cstr(orb_a[k])), COLOR_ORBIT)
            self.play(Create(ln), FadeIn(dt, scale=0.5), FadeOut(z_cur), FadeIn(z_new), run_time=1.0)
            self.wait(0.5)
            z_cur = z_new
            trail_a.add(ln, dt)
            prev = nxt

        z_new = z_text(r"\dots\ \text{y se repite decenas de veces}", COLOR_ORBIT)
        self.play(FadeOut(z_cur), FadeIn(z_new), run_time=0.8)
        z_cur = z_new
        rest = VGroup()
        for k in range(5, len(orb_a)):
            nxt = PA(orb_a[k])
            rest.add(Line(prev, nxt, color=COLOR_ORBIT, stroke_width=2).set_opacity(0.8).set_z_index(6),
                     Dot(nxt, color=COLOR_ORBIT, radius=0.05).set_opacity(0.8).set_z_index(7))
            prev = nxt
        self.play(Create(rest), run_time=2.6, rate_func=linear)
        z_new = z_text(r"\text{se queda cerca del origen}", COLOR_ORBIT)
        self.play(*swap_caption("¡Atrapado para siempre!", color=COLOR_ORBIT),
                  FadeOut(z_cur), FadeIn(z_new), run_time=1.0)
        z_cur = z_new
        self.wait(2.0)

        self.play(FadeOut(VGroup(frame_a, axes_a, c_dot_a, c_lab_a, trail_a, rest, z_cur)), run_time=0.8)

        # =============================================================
        # 4. CASO 2: EL FUGITIVO  (c = 0.4 + 0.5i, se escapa)
        # =============================================================
        HW_B = 2.5
        frame_b, axes_b = make_plane(0j, HW_B, [-2, -1, 1, 2], [-2, -1, 1, 2])
        PB = lambda z: P(z, 0j, HW_B)
        c_dot_b = Dot(PB(C_B), color=YELLOW, radius=0.1).set_z_index(7)
        c_lab_b = lab("c", PB(C_B) + UP * 0.3 + RIGHT * 0.22, 40, YELLOW)
        radius2 = PB(2 + 0j)[0] - PB(0j)[0]
        circ = DashedVMobject(Circle(radius=radius2, color=COLOR_EXPLODE, stroke_width=3.5), num_dashes=48)
        circ.move_to(PB(0j)).set_z_index(4)
        circ_lab = lab(r"|z|=2", PB(complex(1.85, -2.1)), 34, COLOR_EXPLODE)   # fuera de la circunferencia, en la esquina
        self.play(*swap_caption("Caso 2: c = 0.4 + 0.5i", color=COLOR_EXPLODE),
                  Create(frame_b), FadeIn(axes_b), run_time=1.4)
        self.play(FadeIn(c_dot_b, scale=2), FadeIn(c_lab_b), Create(circ), FadeIn(circ_lab), run_time=1.4)

        orb_b = orbit(C_B, 12)
        z_cur = z_text(r"z_0=0", COLOR_EXPLODE)
        origin_b = Dot(PB(0j), color=COLOR_EXPLODE, radius=0.09).set_z_index(7)
        self.play(FadeIn(origin_b, scale=2), FadeIn(z_cur), run_time=0.8)
        self.wait(0.6)

        trail_b = VGroup(origin_b)
        prev = PB(0j)
        for k in range(1, 8):
            nxt = PB(orb_b[k])
            ln = Line(prev, nxt, color=COLOR_EXPLODE, stroke_width=3.5).set_z_index(6)
            dt = Dot(nxt, color=COLOR_EXPLODE, radius=0.08).set_z_index(7)
            z_new = z_text("z_{%d}=%s" % (k, cstr(orb_b[k])), COLOR_EXPLODE)
            slow = k <= 4
            self.play(Create(ln), FadeIn(dt, scale=0.5), FadeOut(z_cur), FadeIn(z_new),
                      run_time=1.0 if slow else 0.8)
            self.wait(0.5 if slow else 0.3)
            z_cur = z_new
            trail_b.add(ln, dt)
            prev = nxt
        # z_7 ya cruzó la circunferencia |z| = 2
        self.play(Flash(trail_b[-1], color=COLOR_EXPLODE, flash_radius=0.4),
                  *swap_caption("Cruzó la circunferencia:\n¡ya no vuelve!", color=COLOR_EXPLODE),
                  run_time=1.2)
        self.wait(1.0)
        # z_8 queda fuera del cuadro: flecha hasta el borde del plano
        z7, z8 = orb_b[7], orb_b[8]
        t_edge = (-HW_B - z7.imag) / (z8.imag - z7.imag)
        z_edge = z7 + (z8 - z7) * t_edge
        arr = Arrow(PB(z7), PB(z_edge), buff=0.1, color=COLOR_EXPLODE, stroke_width=5,
                    max_tip_length_to_length_ratio=0.12).set_z_index(6)
        grow = z_text(r"|z_8|\approx 6.8,\ \ |z_9|\approx 46,\ \dots", COLOR_EXPLODE)
        self.play(GrowArrow(arr), FadeOut(z_cur), FadeIn(grow), run_time=1.6)
        z_cur = grow
        self.play(*swap_caption("La distancia explota\nhacia el infinito", color=COLOR_EXPLODE), run_time=1.0)
        self.wait(2.2)

        self.play(FadeOut(VGroup(frame_b, axes_b, c_dot_b, c_lab_b, circ, circ_lab, trail_b, arr, z_cur)),
                  run_time=0.8)

        # =============================================================
        # 5. PINTAR CADA c: negro si se queda, color si escapa
        # =============================================================
        frame_m, axes_m = make_plane(M_CEN, M_HW, [-2, -1, 1], [-1, 1])
        PM = lambda z: P(z, M_CEN, M_HW)
        d1 = Dot(PM(C_A), color=YELLOW, radius=0.11).set_z_index(8)
        d2 = Dot(PM(C_B), color=YELLOW, radius=0.11).set_z_index(8)
        l1 = lab("c_1", PM(C_A) + UP * 0.35 + LEFT * 0.2, 38, YELLOW)
        l2 = lab("c_2", PM(C_B) + UP * 0.35 + RIGHT * 0.1, 38, YELLOW)
        self.play(*swap_caption("Cada punto c del plano\ntiene su propia historia"),
                  Create(frame_m), FadeIn(axes_m), run_time=1.4)
        self.play(FadeIn(d1, scale=2), FadeIn(l1), FadeIn(d2, scale=2), FadeIn(l2), run_time=1.0)
        self.wait(1.4)

        mu_b = mandelbrot_mu(C_B.real, C_B.imag, 1e-9, 1, 1, 200)[0, 0]
        col_b = rgb_to_manim(colorize(np.array([[mu_b]]))[0, 0])
        self.play(*swap_caption("Se pinta de negro si se queda;\nde color si escapa"),
                  d1.animate.set_fill(BLACK, 1.0).set_stroke(WHITE, 3),
                  d2.animate.set_fill(col_b, 1.0).set_stroke(WHITE, 3),
                  run_time=1.6)
        self.wait(2.0)

        # =============================================================
        # 6. TODOS LOS c: rejilla -> bloques -> más y más puntos
        # =============================================================
        GN = 9
        mu_g = mandelbrot_mu(M_CEN.real, M_CEN.imag, M_HW, GN, GN, 100)
        cw = 2 * M_HW / GN
        grid_dots, grid_cols = VGroup(), []
        for j in range(GN):
            for i in range(GN):
                z = complex(M_CEN.real - M_HW + (i + 0.5) * cw, M_CEN.imag + M_HW - (j + 0.5) * cw)
                dd = Dot(PM(z), radius=0.07, color=WHITE).set_z_index(7)
                grid_dots.add(dd)
                grid_cols.append(BLACK if mu_g[j, i] < 0 else rgb_to_manim(colorize(np.array([[mu_g[j, i]]]))[0, 0]))
        self.play(*swap_caption("Hagamos lo mismo\ncon muchos valores de c"),
                  FadeOut(VGroup(d1, d2, l1, l2)), FadeOut(axes_m),
                  LaggedStart(*[FadeIn(dd, scale=2) for dd in grid_dots], lag_ratio=0.02),
                  run_time=3.0)
        self.wait(0.8)
        self.play(*swap_caption("Cada uno: negro o color"),
                  *[dd.animate.set_fill(c).set_stroke(WHITE, 1.5) for dd, c in zip(grid_dots, grid_cols)],
                  run_time=1.8)
        self.wait(1.2)
        img0 = to_mobject(upsample(colorize(mu_g)))
        self.play(FadeIn(img0), run_time=1.4)
        self.wait(0.8)
        self.play(*swap_caption("Con más y más puntos…"), FadeOut(grid_dots), run_time=1.0)
        current = img0
        for n in (18, 36, 72, 144):
            mu_n = mandelbrot_mu(M_CEN.real, M_CEN.imag, M_HW, n, n, 100 + n)
            new = to_mobject(upsample(colorize(mu_n)))
            self.remove(current)
            self.add(new)
            current = new
            self.wait(0.9)
        mu_f = mandelbrot_mu(M_CEN.real, M_CEN.imag, M_HW, NPIX, NPIX, 200)
        final_img = to_mobject(colorize(mu_f))
        self.remove(current)
        self.add(final_img)
        self.wait(0.8)

        # =============================================================
        # 7. NOMBRE
        # =============================================================
        m1 = Dot(PM(C_A), color=BLACK, radius=0.11).set_stroke(WHITE, 3).set_z_index(8)
        m2 = Dot(PM(C_B), color=col_b, radius=0.11).set_stroke(WHITE, 3).set_z_index(8)
        self.play(*swap_caption("Negro: c se queda atrapado\nColor: c se escapa", size=44),
                  FadeIn(m1, scale=2), FadeIn(m2, scale=2), run_time=1.4)
        self.wait(2.4)
        self.play(*swap_caption("El conjunto de\nMandelbrot", size=56, color=COLOR_RESULT),
                  FadeOut(VGroup(m1, m2)), run_time=1.2)
        self.wait(2.4)

        # =============================================================
        # 8. ZOOM AL BORDE (un solo movimiento continuo)
        # =============================================================
        zu = ValueTracker(0.0)

        def window(u):
            """Centro y semilado de la ventana: el objetivo pasa de la vista completa a ocupar el centro."""
            s = u * u * (3 - 2 * u)
            hw = M_HW * ZOOM ** (-u)
            cen = TARGET + (M_CEN - TARGET) * (1 - s) * hw / M_HW
            return cen, hw

        def make_zoom():
            u = zu.get_value()
            cen, hw = window(u)
            mu = mandelbrot_mu(cen.real, cen.imag, hw, NPIX, NPIX, int(120 + 130 * u))
            return to_mobject(colorize(mu))

        zoom_img = always_redraw(make_zoom)
        zoom_counter = always_redraw(
            lambda: Text(f"Zoom ×{int(round(ZOOM ** zu.get_value())):,}".replace(",", "."),
                         font_size=56, weight=BOLD, color=GREEN_C).move_to(DOWN * 3.3)
        )
        self.remove(final_img)
        self.add(zoom_img, zoom_counter)

        FD = 0.7
        sched = [("Acerquémonos\nal borde…", 0.0, 4.2),
                 ("Cada vez más detalle,\nsin final", 4.2, 8.4),
                 ("…y aparece una copia\ndel conjunto completo", 8.4, 1e9)]

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
            zu.animate(run_time=ZOOM_T, rate_func=linear).set_value(1.0),
            FadeOut(old_cap, run_time=0.7),
            lag_ratio=0,
        ))
        zoom_img.clear_updaters()
        zoom_counter.clear_updaters()
        for c in timed[:-1]:
            self.remove(c)
        timed[-1].clear_updaters()
        timed[-1].set_opacity(1)
        cap_holder[0] = timed[-1]
        self.wait(2.6)

        self.play(*swap_caption("Su frontera tiene\ndimensión fractal 2", size=52, color=COLOR_RESULT),
                  run_time=1.0)
        self.wait(3.0)

        # =============================================================
        # 9. CIERRE Y LOGO
        # =============================================================
        self.play(FadeOut(Group(cap_holder[0], zoom_img, zoom_counter, frame_m)), run_time=1.2)
        logo = MathTex(r"F_{GC}", font_size=150, color=COLOR_LOGO).move_to(ORIGIN)
        self.play(FadeIn(logo, scale=0.7), run_time=1.2)
        self.wait(2.5)