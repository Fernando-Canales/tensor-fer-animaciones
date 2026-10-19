from manim import *
import numpy as np

# ---------------------------------------------------------------
# FORMATO: cuadro vertical 9:16 (1080x1920), igual que los otros shorts.
# Pon PORTRAIT = False para renderizar horizontal.
# ---------------------------------------------------------------
PORTRAIT = True
if PORTRAIT:
    config.pixel_width = 1080
    config.pixel_height = 1920
    config.frame_width = 6.0
    config.frame_height = 6.0 * 16 / 9


class KochShort(Scene):
    def construct(self):
        # ---------------- Paleta ----------------
        TXT_BASE = ManimColor("#E1E1D5")
        COLOR_RESULT = YELLOW_D
        COLOR_LOGO = BLUE_C
        COLOR_LINE = BLUE_C
        COLOR_FILL = BLUE_E

        W = config.frame_width
        H = config.frame_height

        # ---------------- Parámetros ----------------
        R = 2.5                                    # radio del círculo que rodea la figura
        N = 6                                      # iteraciones que se muestran en el crecimiento
        ZL = 3                                     # ciclos de zoom (cada uno es ×3): 3^3 = ×27
        ZOOM_TIME_PER_LEVEL = 2.6                  # segundos por cada ×3
        NZ = N + ZL                                # profundidad máxima que se precalcula
        CENTER = np.array([0.0, 0.7, 0.0])
        S = R * np.sqrt(3)                         # lado del triángulo inicial
        AREA0 = np.sqrt(3) / 4 * S ** 2

        def fit_width(m, frac=0.93):
            if m.width > W * frac:
                m.scale(W * frac / m.width)
            return m

        # ---------------- Curva de Koch con numpy ----------------
        def koch_step(P, alpha):
            Q = np.roll(P, -1, axis=0)
            d = Q - P
            a = P + d / 3
            b = P + 2 * d / 3
            mid = (a + b) / 2
            L = np.linalg.norm(d, axis=1, keepdims=True)
            normal = np.stack([d[:, 1], -d[:, 0]], axis=1) / L
            tip = mid + normal * (np.sqrt(3) / 6) * L * alpha
            out = np.empty((len(P) * 4, 2))
            out[0::4], out[1::4], out[2::4], out[3::4] = P, a, tip, b
            return out

        ang = np.radians([90, 210, 330])
        P0 = CENTER[:2] + R * np.stack([np.cos(ang), np.sin(ang)], axis=1)
        P_list = [P0]
        for _ in range(NZ):
            P_list.append(koch_step(P_list[-1], 1.0))

        V0 = P0[0]

        def koch_step_open(pts, alpha):
            d = pts[1:] - pts[:-1]
            a = pts[:-1] + d / 3
            b = pts[:-1] + 2 * d / 3
            L = np.linalg.norm(d, axis=1, keepdims=True)
            normal = np.stack([d[:, 1], -d[:, 0]], axis=1) / L
            tip = (a + b) / 2 + normal * (np.sqrt(3) / 6) * L * alpha
            body = np.stack([pts[:-1], a, tip, b], axis=1).reshape(-1, 2)
            return np.vstack([body, pts[-1:]])

        def zoom_points(z):
            z = min(max(z, 0.0), float(ZL))
            k = int(z)
            t = z - k
            n = N + k
            Pn = P_list[n]
            M = len(Pn)
            if k == 0:
                line = koch_step_open(np.vstack([Pn, Pn[:1]]), t)
            else:
                m = 4 ** (n - k + 1)
                pre = koch_step_open(Pn[:m + 1], t)
                suf = koch_step_open(np.vstack([Pn[M - m:], Pn[:1]]), t)
                line = np.vstack([suf, pre[1:]])
            Q = V0 + (line - V0) * (3.0 ** z)
            inside = (np.abs(Q[:, 0]) < W / 2 + 0.4) & (np.abs(Q[:, 1]) < H / 2 + 0.4)
            idx = np.flatnonzero(inside)
            if len(idx) < 2:
                return Q[:2]
            return Q[idx[0]: idx[-1] + 1]

        def shape_points(x):
            n = min(int(x), N)
            a = x - n
            if n >= N or a < 1e-9:
                return P_list[min(n, N)]
            return koch_step(P_list[n], a)

        def stats(x):
            pts = shape_points(x)
            nxt = np.roll(pts, -1, axis=0)
            per = np.linalg.norm(nxt - pts, axis=1).sum() / S
            area = 0.5 * abs(np.sum(pts[:, 0] * nxt[:, 1] - nxt[:, 0] * pts[:, 1])) / AREA0
            return per, area

        prog = ValueTracker(0.0)

        def make_shape():
            x = prog.get_value()
            pts = shape_points(x)
            pts3 = np.column_stack([pts, np.zeros(len(pts))])
            m = VMobject()
            m.set_points_as_corners(np.vstack([pts3, pts3[:1]]))
            m.set_stroke(COLOR_LINE, width=max(1.6, 4.5 - 0.5 * x))
            m.set_fill(COLOR_FILL, opacity=0.35)
            return m

        shape = always_redraw(make_shape)

        STAT_Y = [-2.75, -3.45]

        def make_stat(which):
            def f():
                per, area = stats(prog.get_value())
                if which == 0:
                    t = Text(f"Perímetro: {per:.2f}", font_size=50, weight=BOLD, color=COLOR_LINE)
                else:
                    t = Text(f"Área: {area:.2f}×", font_size=50, weight=BOLD, color=GREEN_C)
                return fit_width(t).move_to(UP * STAT_Y[which])
            return f

        stat_per = always_redraw(make_stat(0))
        # stat_area se evaluará de forma estática en la revelación final

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
        # 2. TRIÁNGULO INICIAL
        # =============================================================
        self.play(
            FadeIn(shape, scale=0.85),
            *swap_caption("Empieza con\nun triángulo"),
            run_time=1.2
        )
        Pn0 = np.roll(P0, -1, axis=0)
        side_labels = VGroup()
        for p, q in zip(P0, Pn0):
            mid = (p + q) / 2
            out = (mid - CENTER[:2]) / np.linalg.norm(mid - CENTER[:2])
            lab = Text("1", font_size=60, weight=BOLD, color=YELLOW)
            lab.move_to(np.array([*(mid + out * 0.38), 0.0]))
            side_labels.add(lab)
            
        # AQUÍ SOLO MOSTRAMOS EL PERÍMETRO (SIN EL ÁREA)
        self.play(FadeIn(stat_per), FadeIn(side_labels, scale=1.4), run_time=0.7)
        self.wait(1.2)

        # =============================================================
        # 3. PRIMER PASO, DESPACIO
        # =============================================================
        Pn = np.roll(P0, -1, axis=0)
        d0 = Pn - P0
        a_pts = P0 + d0 / 3
        b_pts = P0 + 2 * d0 / 3
        to3 = lambda p: np.array([p[0], p[1], 0.0])
        thirds = VGroup(*[Dot(to3(p), radius=0.08, color=YELLOW) for p in np.vstack([a_pts, b_pts])])
        mids = VGroup(*[Line(to3(a), to3(b), color=YELLOW, stroke_width=9)
                        for a, b in zip(a_pts, b_pts)])
        thirds.set_z_index(5)
        mids.set_z_index(5)

        self.play(*swap_caption("Divide cada lado\nen tres partes"),
                  FadeIn(thirds, scale=2), FadeOut(side_labels), run_time=1.0)
        self.wait(1.0)
        self.play(*swap_caption("Construye un triángulo\nen el tercio central"),
                  Create(mids), run_time=1.0)
        self.wait(0.8)
        self.play(prog.animate.set_value(1.0), FadeOut(thirds), FadeOut(mids),
                  run_time=2.8, rate_func=smooth)
        self.wait(1.2)

        # =============================================================
        # 4. REPETIR
        # =============================================================
        self.play(*swap_caption("Y repite…"),
                  prog.animate.set_value(2.0), run_time=2.2, rate_func=smooth)
        self.wait(0.4)
        for n, rt in [(3, 1.6), (4, 1.3), (5, 1.1), (6, 1.1)]:
            self.play(prog.animate.set_value(float(n)), run_time=rt, rate_func=smooth)
            self.wait(0.35)
        self.wait(0.6)

        # =============================================================
        # 5. REVELACIÓN: Título superior + Perímetro infinito + APARECE EL ÁREA
        # =============================================================
        shape.clear_updaters()
        stat_per.clear_updaters()
        
        per_inf = Text("Perímetro: ∞", font_size=58, weight=BOLD, color=COLOR_RESULT)
        area_fin = Text("Área: 1.6× original", font_size=48, weight=BOLD, color=COLOR_RESULT)
        
        fit_width(per_inf).move_to(UP * STAT_Y[0])
        fit_width(area_fin).move_to(UP * STAT_Y[1])

        # El título aparece arriba y simultáneamente el perímetro se vuelve infinito y surge el área finita abajo
        self.play(
            *swap_caption("Copo de nieve de Koch", size=56, color=COLOR_RESULT),
            Transform(stat_per, per_inf), 
            FadeIn(area_fin, shift=UP * 0.2), 
            run_time=1.5
        )
        self.wait(2.2)

        # =============================================================
        # 6. ...Y CABE EN UN CÍRCULO
        # =============================================================
        circle = Circle(radius=R, color=YELLOW_D, stroke_width=5).move_to(CENTER)
        self.play(Create(circle), run_time=2.0)
        self.wait(2.4)

        # =============================================================
        # 7. ZOOM INFINITO DIRECTO HACIA EL LOGO
        # =============================================================
        zt = ValueTracker(0.0)
        zop = ValueTracker(1.0)

        def make_zoom():
            pts = zoom_points(zt.get_value())
            m = VMobject()
            m.set_points_as_corners(np.column_stack([pts, np.zeros(len(pts))]))
            m.set_stroke(COLOR_LINE, width=3.4, opacity=zop.get_value())
            m.set_fill(opacity=0)
            return m

        zoom_curve = always_redraw(make_zoom)
        zoom_curve.set_z_index(2)
        self.add(zoom_curve)

        T = ZOOM_TIME_PER_LEVEL * ZL
        old_cap = cap_holder[0]

        # Desvanecemos gradualmente el título superior al final del zoom para dar paso limpio al logo
        zop.add_updater(lambda m: m.set_value(1.0 if zt.get_value() < (ZL - 0.5) else max(0.0, 1.0 - (zt.get_value() - (ZL - 0.5)) * 2)))
        self.add(zop)

        self.play(AnimationGroup(
            zt.animate(run_time=T, rate_func=linear).set_value(float(ZL)),
            FadeOut(VGroup(shape, circle, stat_per, area_fin, old_cap), run_time=0.8),
            lag_ratio=0,
        ))
        
        zoom_curve.clear_updaters()
        self.remove(zoom_curve)
        zop.clear_updaters()

        # =============================================================
        # 8. CIERRE Y LOGO
        # =============================================================
        logo = MathTex(r"F_{GC}", font_size=150, color=COLOR_LOGO).move_to(ORIGIN)
        self.play(FadeIn(logo, scale=0.7), run_time=1.2)
        self.wait(2.5)