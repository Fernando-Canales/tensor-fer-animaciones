from manim import *
import numpy as np

# ---------------------------------------------------------------
# FORMATO: cuadro vertical 9:16 (1080x1920), igual que el short de Euler.
# Pon PORTRAIT = False para renderizar horizontal.
# ---------------------------------------------------------------
PORTRAIT = True
if PORTRAIT:
    config.pixel_width = 1080
    config.pixel_height = 1920
    config.frame_width = 6.0
    config.frame_height = 6.0 * 16 / 9


class SierpinskiShort(Scene):
    def construct(self):
        # ---------------- Paleta ----------------
        TXT_BASE = ManimColor("#E1E1D5")
        COLOR_RESULT = YELLOW_D
        COLOR_LOGO = BLUE_C
        VCOLORS = [BLUE_C, GREEN_C, RED_C]        # arriba, abajo-izq, abajo-der

        W = config.frame_width
        H = config.frame_height

        # ---------------- Parámetros ----------------
        SIDE = 5.2                                 # lado del triángulo
        N_DEMO = 5                                 # pasos lentos explicados
        N_TOTAL = 30000                            # puntos del fractal final
        POINT_SIZE = 3                             # tamaño de cada punto (px aprox.)
        RAMP_TIME = 8.5                            # segundos de la aceleración
        DEMO_ROLLS = [0, 2, 1, 2, 0]               # esquinas de los 5 primeros pasos
        ZOOM_LEVELS = 3                            # duplicaciones de zoom (2^3 = x8)
        ZOOM_POINTS = 600_000                      # puntos precalculados para el zoom
        ZOOM_TIME_PER_LEVEL = 2.6                  # segundos por cada duplicación
        rng = np.random.default_rng(7)             # semilla fija: mismo video siempre

        def fit_width(m, frac=0.93):
            if m.width > W * frac:
                m.scale(W * frac / m.width)
            return m

        # ---------------- Geometría ----------------
        height = SIDE * np.sqrt(3) / 2
        TOP_Y = 2.9
        V = np.array([
            [0.0,        TOP_Y,          0.0],     # 0: arriba
            [-SIDE / 2,  TOP_Y - height, 0.0],     # 1: abajo-izquierda
            [SIDE / 2,   TOP_Y - height, 0.0],     # 2: abajo-derecha
        ])
        bary0 = np.array([0.15, 0.60, 0.25])       # punto inicial (dentro del triángulo)
        start = bary0 @ V

        # ---------------- Juego del caos (todo con numpy) ----------------
        idx = rng.integers(0, 3, N_TOTAL)
        idx[:N_DEMO] = DEMO_ROLLS
        pts = np.zeros((N_TOTAL + 1, 3))
        pts[0] = start
        for k in range(N_TOTAL):
            pts[k + 1] = (pts[k] + V[idx[k]]) / 2

        vc_rgba = np.array([color_to_rgba(c) for c in VCOLORS])
        rgbas_all = vc_rgba[idx]                   # cada punto toma el color de su esquina

        # =============================================================
        # 1. GANCHO
        # =============================================================
        hook = Text(
            "¿Puede el azar\ncrear un fractal?",
            font_size=62, weight=BOLD, color=TXT_BASE, line_spacing=1.3
        )
        fit_width(hook).move_to(ORIGIN)
        self.play(Write(hook), run_time=1.4)
        self.wait(1.2)
        self.play(FadeOut(hook), run_time=0.6)

        # =============================================================
        # 2. TRIÁNGULO, ESQUINAS Y PUNTO INICIAL
        # =============================================================
        outline = Polygon(*V, color=TXT_BASE, stroke_width=3)
        vdots = VGroup(*[Dot(V[j], radius=0.17, color=VCOLORS[j]) for j in range(3)])
        for d in vdots:
            d.set_z_index(4)

        cap_holder = [None]

        def make_caption(text, size=50, color=TXT_BASE):
            c = Text(text, font_size=size, weight=BOLD, color=color, line_spacing=1.1)
            fit_width(c).move_to(UP * 4.1)
            return c

        def swap_caption(text, **kw):
            """Devuelve las animaciones que cambian el texto de arriba."""
            new = make_caption(text, **kw)
            old = cap_holder[0]
            cap_holder[0] = new
            if old is None:
                return [FadeIn(new, shift=DOWN * 0.2)]
            return [FadeOut(old, shift=UP * 0.2), FadeIn(new, shift=DOWN * 0.2)]

        self.play(Create(outline), run_time=1.2)
        self.play(
            FadeIn(vdots, scale=1.5),
            *swap_caption("Un triángulo y\nun punto cualquiera"),
            run_time=0.8
        )

        cursor = Dot(start, radius=0.14, color=YELLOW)
        cursor.set_z_index(6)
        self.play(FadeIn(cursor, scale=3), run_time=0.7)
        self.wait(0.8)

        # =============================================================
        # 3. LOS PRIMEROS PASOS, DESPACIO
        # =============================================================
        plotted = VGroup()
        captions = {
            0: "Elige una esquina\nal azar",
            1: "Avanza hasta la\nmitad del camino",
            2: "Marca el punto\ny repite",
        }
        for k in range(N_DEMO):
            j = int(idx[k])
            vc = VCOLORS[j]
            slow = k < 2                           # los dos primeros pasos, bien explicados
            cur_pos, new_pos = pts[k], pts[k + 1]

            # --- (a) Elegir esquina: se recorren las otras dos y cae en la elegida ---
            if slow:
                others = [(j + 1) % 3, (j + 2) % 3]
                first_caption = swap_caption(captions[0]) if k == 0 else []
                self.play(Indicate(vdots[others[0]], scale_factor=1.6, color=WHITE),
                          *first_caption, run_time=0.5)
                self.play(Indicate(vdots[others[1]], scale_factor=1.6, color=WHITE),
                          run_time=0.5)
                self.play(Indicate(vdots[j], scale_factor=2.0, color=WHITE), run_time=1.0)
                self.wait(1.0 if k == 0 else 0.6)      # tiempo para leer y asimilar
            else:
                extra = swap_caption(captions[2]) if k == 2 else []
                self.play(Indicate(vdots[j], scale_factor=1.9, color=WHITE),
                          *extra, run_time=0.45)

            # --- (b) Trazar la línea hacia esa esquina ---
            line = DashedLine(cur_pos, V[j], color=vc, stroke_width=5, dash_length=0.13)
            extra = swap_caption(captions[1]) if k == 0 else []
            self.play(Create(line), *extra, run_time=1.6 if slow else 0.5)
            if k == 0:
                self.wait(1.0)
            elif k == 1:
                self.wait(0.4)

            # --- (c) Marcar el punto medio y mover el cursor ---
            new_dot = Dot(new_pos, radius=0.07, color=vc)
            new_dot.set_z_index(3)
            self.play(FadeIn(new_dot, scale=3), run_time=0.7 if slow else 0.25)
            plotted.add(new_dot)

            self.play(cursor.animate.move_to(new_pos), FadeOut(line),
                      run_time=1.0 if slow else 0.35)
            if slow:
                self.wait(0.3)

        # =============================================================
        # 4. ACELERACIÓN: miles de puntos
        # =============================================================
        tracker = ValueTracker(N_DEMO)
        fade_tracker = ValueTracker(1.0)           # 1 = visible, 0 = negro

        def update_cloud(m):
            n = int(tracker.get_value())
            m.points = pts[1:1 + n]
            rgba = rgbas_all[:n].copy()
            rgba[:, :3] *= fade_tracker.get_value()
            m.rgbas = rgba

        cloud = PMobject(stroke_width=POINT_SIZE)
        cloud.add_updater(update_cloud)

        counter = always_redraw(
            lambda: Text(
                f"{int(tracker.get_value()):,}",
                font_size=84, weight=BOLD, color=COLOR_RESULT
            ).move_to(DOWN * 3.5)
        )
        counter_label = Text("puntos", font_size=44, color=TXT_BASE).move_to(DOWN * 4.45)

        self.play(
            FadeOut(VGroup(cursor, plotted)),
            *swap_caption("Ahora, miles\nde veces más…"),
            run_time=0.6
        )
        self.add(cloud)
        update_cloud(cloud)
        self.play(FadeIn(counter), FadeIn(counter_label), run_time=0.5)

        N0, N1 = N_DEMO, N_TOTAL

        def ramp(t):
            # crecimiento exponencial: 10 → 100 → 1,000 → 10,000 con el mismo tiempo cada uno
            return (N0 * (N1 / N0) ** t - N0) / (N1 - N0)

        self.play(tracker.animate.set_value(N1), run_time=RAMP_TIME, rate_func=ramp)
        self.wait(1.0)

        # =============================================================
        # 5. REVELACIÓN: triángulo de Sierpinski
        # =============================================================
        self.play(*swap_caption("Triángulo de\nSierpinski", size=58, color=COLOR_RESULT),
                  run_time=0.8)
        self.wait(1.4)

        # Autosemejanza: tres copias de sí mismo
        def sub_triangle(j):
            a = V[j]
            b = (V[j] + V[(j + 1) % 3]) / 2
            c = (V[j] + V[(j + 2) % 3]) / 2
            return Polygon(a, b, c, color=VCOLORS[j], stroke_width=6)

        subs = VGroup(*[sub_triangle(j) for j in range(3)])
        self.play(
            *swap_caption("Tres copias\nde sí mismo"),
            LaggedStart(*[Create(s) for s in subs], lag_ratio=0.3),
            run_time=1.8
        )
        self.wait(1.6)

        # Dato de cierre: la dimensión
        dim_a = Text("Dimensión ≈ 1.585", font_size=56, weight=BOLD, color=COLOR_RESULT)
        dim = VGroup(fit_width(dim_a)).arrange(DOWN, buff=0.35)
        dim.move_to(DOWN * 3.9)
        self.play(
            FadeOut(VGroup(counter, counter_label)),
            FadeOut(subs),
            FadeIn(dim, shift=UP * 0.2),
            run_time=1.0
        )
        self.wait(2.2)

        # =============================================================
        # 6. ZOOM HACIA LA ESQUINA DE ARRIBA
        #    El triángulo es autosemejante: al duplicar el zoom hacia una
        #    esquina vuelve a verse exactamente la misma figura.
        #    Para que no se vacíe de puntos al acercarnos, se precalculan
        #    muchos más (ZOOM_POINTS) con "direcciones" de dígitos 0/1/2:
        #    cada punto = suma de V[d_j] / 2^j (equivale al juego del caos).
        # =============================================================
        m_dig = 24                                  # dígitos por punto (precisión ~1e-7)
        n_arr = np.arange(30, N_TOTAL + 1)          # puntos del juego del caos ya mostrados
        # dígito j del punto n = esquina elegida j pasos atrás (d_1 = la más reciente)
        D_chaos = np.stack([idx[n_arr - j] for j in range(1, m_dig + 1)], axis=1).astype(np.int8)
        rng2 = np.random.default_rng(11)
        M_extra = ZOOM_POINTS - len(n_arr)
        D_extra = rng2.integers(0, 3, (M_extra, m_dig)).astype(np.int8)
        D = np.vstack([D_chaos, D_extra])
        is_extra = np.concatenate([np.zeros(len(n_arr), bool), np.ones(M_extra, bool)])

        pos = np.zeros((len(D), 3))
        key = np.zeros(len(D), dtype=np.int64)
        for jj in range(m_dig):
            pos += V[D[:, jj]] * 0.5 ** (jj + 1)
            key = key * 3 + D[:, jj]                # d_1 es el dígito más significativo

        # Orden por dirección: los puntos con los primeros k dígitos = 0 quedan
        # al inicio (son los de la zona a la que hacemos zoom).
        order = np.argsort(key, kind="stable")
        Ps, Ds, ex, ks = pos[order], D[order], is_extra[order], key[order]
        counts = [int(np.searchsorted(ks, 3 ** (m_dig - lv))) for lv in range(ZOOM_LEVELS + 1)]
        VC3 = np.array([color_to_rgba(c)[:3] for c in VCOLORS])
        A = V[0]

        zoom_tracker = ValueTracker(0.0)            # z: nivel de zoom, escala = 2^z
        extra_fade = ValueTracker(0.0)              # los puntos nuevos aparecen con fundido

        def update_zoom(m):
            z = zoom_tracker.get_value()
            k = int(z)
            t = z - k
            cnt = counts[max(0, k - 1)]             # incluye la zona vecina (nivel k-1)
            Q = A + (Ps[:cnt] - A) * (2.0 ** z)
            keep = np.nonzero(
                (np.abs(Q[:, 0]) < W / 2 + 0.2) & (np.abs(Q[:, 1]) < H / 2 + 0.2)
            )[0]
            # color: mezcla continua entre el dígito actual y el siguiente
            rgb = (1 - t) * VC3[Ds[keep, k]] + t * VC3[Ds[keep, k + 1]]
            gain = np.where(ex[keep], extra_fade.get_value(), 1.0) * fade_tracker.get_value()
            rgb = rgb * gain[:, None]
            m.points = Q[keep]
            m.rgbas = np.concatenate([rgb, np.ones((len(keep), 1))], axis=1)

        cloud.clear_updaters()
        cloud.add_updater(update_zoom)
        update_zoom(cloud)                          # zoom 0 = misma imagen que ya se ve

        # Se retiran los elementos fijos y los puntos extra completan la figura
        self.play(
            FadeOut(VGroup(outline, vdots, dim)),
            extra_fade.animate.set_value(1.0),
            *swap_caption("Hagamos zoom…"),
            run_time=1.2
        )

        self.play(zoom_tracker.animate.set_value(1.0),
                  run_time=ZOOM_TIME_PER_LEVEL, rate_func=linear)
        self.play(*swap_caption("La misma figura,\nuna y otra vez"), run_time=0.6)
        self.play(zoom_tracker.animate.set_value(float(ZOOM_LEVELS)),
                  run_time=ZOOM_TIME_PER_LEVEL * (ZOOM_LEVELS - 1), rate_func=linear)

        self.play(*swap_caption("Cada parte es\ncopia del todo", size=56, color=COLOR_RESULT),
                  run_time=0.8)
        self.wait(2.2)

        # =============================================================
        # 7. CIERRE Y LOGO
        # =============================================================
        # La nube de puntos (PMobject) no cabe en un VGroup y no se desvanece con
        # FadeOut: la oscurecemos hasta negro con fade_tracker (el fondo es negro)
        self.play(
            FadeOut(cap_holder[0]),
            fade_tracker.animate.set_value(0.0),
            run_time=1.0
        )
        cloud.clear_updaters()
        self.remove(cloud)

        logo = MathTex(r"F_{GC}", font_size=150, color=COLOR_LOGO).move_to(ORIGIN)
        self.play(FadeIn(logo, scale=0.7), run_time=1.2)
        self.wait(2.5)