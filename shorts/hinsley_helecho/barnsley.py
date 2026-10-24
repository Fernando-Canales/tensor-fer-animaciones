from manim import *
import numpy as np

# ---------------------------------------------------------------
# FORMATO: cuadro vertical 9:16 (1080x1920), igual que los otros shorts.
# Pon PORTRAIT = False para renderizar horizontal.
# Render: manim -qh --fps 60 barnsley_short.py BarnsleyShort
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
# Helecho de Barnsley: sistema de funciones iteradas (IFS) con 4 transformaciones
# afines  f_j(p) = A_j p + b_j  y probabilidades P_j.
IFS_A = np.array([
    [[0.00, 0.00], [0.00, 0.16]],       # f1: tallo
    [[0.85, 0.04], [-0.04, 0.85]],      # f2: hoja principal (copia 85 %, girada y subida)
    [[0.20, -0.26], [0.23, 0.22]],      # f3: hoja izquierda
    [[-0.15, 0.28], [0.26, 0.24]],      # f4: hoja derecha
])
IFS_B = np.array([[0.0, 0.0], [0.0, 1.6], [0.0, 1.6], [0.0, 0.44]])
IFS_P = np.array([0.01, 0.85, 0.07, 0.07])


def chaos_game(n, rng, forced=()):
    """Juego del caos: n puntos del helecho y la regla que generó cada uno.
    (0, 0) ya pertenece al helecho (es el punto fijo de f1), así que no hace falta descartar nada.
    forced: reglas impuestas para los primeros pasos (para explicarlos en pantalla)."""
    idx = rng.choice(4, size=n, p=IFS_P)
    idx[:len(forced)] = forced
    pts = np.zeros((n + 1, 2))
    for k in range(n):
        j = idx[k]
        pts[k + 1] = IFS_A[j] @ pts[k] + IFS_B[j]
    return pts, idx


def view_map(P, t, A=IFS_A[2], b=IFS_B[2]):
    """Cámara que se acerca a la hoja izquierda: interpola entre la identidad (t=0) y
    f3^-1 (t=1). Con t=1, la imagen f3(helecho) se ve exactamente como el helecho entero."""
    Pinv = (P - b) @ np.linalg.inv(A).T
    return (1 - t) * P + t * Pinv
# END-GEOM


class BarnsleyShort(Scene):
    def construct(self):
        # ---------------- Paleta ----------------
        TXT_BASE = ManimColor("#E1E1D5")
        COLOR_RESULT = YELLOW_D
        COLOR_LOGO = BLUE_C
        RULE_COLORS = [ORANGE, GREEN_C, BLUE_C, RED_C]       # tallo, principal, izq., der.
        FERN_GREEN = GREEN_C

        W = config.frame_width

        # ---------------- Parámetros ----------------
        N_TOTAL = 50_000                           # puntos del helecho
        N_DEMO = 6                                 # pasos lentos explicados
        DEMO_ROLLS = [1, 2, 1, 3, 1, 0]            # f2, f3, f2, f4, f2, f1
        POINT_SIZE = 3
        RAMP_TIME = 9.0
        S = 0.58                                   # escala: el helecho mide 10 unidades de alto
        XMID, Y0 = 0.24, -2.5                      # centrado horizontal y base del helecho
        rng = np.random.default_rng(5)

        def fit_width(m, frac=0.93):
            if m.width > W * frac:
                m.scale(W * frac / m.width)
            return m

        def to_screen(P):
            return np.column_stack([(P[:, 0] - XMID) * S, Y0 + P[:, 1] * S, np.zeros(len(P))])

        def pt(p):
            return np.array([(p[0] - XMID) * S, Y0 + p[1] * S, 0.0])

        # ---------------- Datos ----------------
        pts, idx = chaos_game(N_TOTAL, rng, DEMO_ROLLS)
        Q_all = pts @ IFS_A[2].T + IFS_B[2]        # f3(helecho): la hoja izquierda, entera
        rule_rgb = np.array([color_to_rgba(c)[:3] for c in RULE_COLORS])
        GREEN_RGB = np.array(color_to_rgba(FERN_GREEN)[:3])
        BLUE_RGB = np.array(color_to_rgba(RULE_COLORS[2])[:3])

        # ---------------- Estado animable ----------------
        tracker = ValueTracker(1)                  # puntos del juego del caos visibles
        gmix = ValueTracker(0.0)                   # 0: color por regla · 1: todo verde
        main_op = ValueTracker(1.0)                # brillo del helecho
        leaf_op = ValueTracker(0.0)                # brillo de la hoja ampliada (f3 del helecho)
        leaf_green = ValueTracker(0.0)             # la hoja pasa de azul a verde
        zt = ValueTracker(0.0)                     # zoom hacia la hoja (0 a 1)
        fade_tracker = ValueTracker(0.0)           # 0: negro · 1: visible
        rule_gain = [ValueTracker(1.0) for _ in range(4)]   # brillo de cada parte (por regla)

        def update_cloud(m):
            n = max(1, int(tracker.get_value()))
            g, fd, t = gmix.get_value(), fade_tracker.get_value(), zt.get_value()
            mo, lo, lg = main_op.get_value(), leaf_op.get_value(), leaf_green.get_value()
            P_parts, C_parts = [], []
            if mo * fd > 0.002:
                gains = np.array([r.get_value() for r in rule_gain])
                col = (1 - g) * rule_rgb[idx[:n]] + g * GREEN_RGB
                col = col * gains[idx[:n]][:, None]
                P_parts.append(pts[1:1 + n])
                C_parts.append(col * (mo * fd))
            if lo * fd > 0.002:
                col = ((1 - lg) * BLUE_RGB + lg * GREEN_RGB) * (lo * fd)
                P_parts.append(Q_all[1:])
                C_parts.append(np.tile(col, (len(Q_all) - 1, 1)))
            if not P_parts:
                m.points = np.zeros((1, 3))
                m.rgbas = np.array([[0.0, 0.0, 0.0, 1.0]])
                return
            P = np.vstack(P_parts)
            C = np.vstack(C_parts)
            if t > 1e-6:
                P = view_map(P, t)
            m.points = to_screen(P)
            m.rgbas = np.concatenate([C, np.ones((len(C), 1))], axis=1)

        cloud = PMobject(stroke_width=POINT_SIZE)
        cloud.add_updater(update_cloud)

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
        # 1. GANCHO: el helecho terminado, en verde
        # =============================================================
        gmix.set_value(1.0)
        tracker.set_value(N_TOTAL)
        self.add(cloud)
        update_cloud(cloud)
        self.play(fade_tracker.animate.set_value(1.0),
                  *swap_caption("¿Naturaleza…\no una fórmula?", size=38),
                  run_time=1.8)
        self.wait(2.4)
        self.play(fade_tracker.animate.set_value(0.0), FadeOut(cap_holder[0]), run_time=1.0)
        cap_holder[0] = None
        tracker.set_value(1)
        gmix.set_value(0.0)
        main_op.set_value(0.0)                     # el helecho vuelve a empezar de cero
        fade_tracker.set_value(1.0)
        update_cloud(cloud)

        # =============================================================
        # 2. LAS CUATRO REGLAS
        # =============================================================
        names = ["tallo", "principal", "izquierda", "derecha"]
        pcts = ["1 %", "85 %", "7 %", "7 %"]
        chips = VGroup()
        for j in range(4):
            dot = Dot(radius=0.27, color=RULE_COLORS[j])
            pct = Text(pcts[j], font_size=40, weight=BOLD, color=TXT_BASE)
            nm = Text(names[j], font_size=28, color=TXT_BASE)
            chips.add(VGroup(dot, pct, nm).arrange(DOWN, buff=0.12))
        chips.arrange(RIGHT, buff=0.42)
        fit_width(chips, 0.95)
        chips.move_to(DOWN * 3.5)

        # El helecho terminado, con cada parte del color de su regla.
        # Cada regla se ilumina cuando aparece su círculo: así se ve qué parte dibuja.
        for r in rule_gain:
            r.set_value(0.12)
        tracker.set_value(N_TOTAL)
        main_op.set_value(1.0)
        gmix.set_value(0.0)
        fade_tracker.set_value(0.0)
        update_cloud(cloud)
        self.play(fade_tracker.animate.set_value(1.0),
                  *swap_caption("Cada regla dibuja\nuna parte del helecho"),
                  run_time=1.4)
        for j in range(4):
            anims = [FadeIn(chips[j], shift=UP * 0.2), rule_gain[j].animate.set_value(1.0)]
            if j > 0:
                anims.append(rule_gain[j - 1].animate.set_value(0.35))
            self.play(*anims, run_time=0.9)
            self.wait(1.1)
        self.play(*[r.animate.set_value(1.0) for r in rule_gain],
                  *swap_caption("Cuatro reglas,\ncada una con su probabilidad"), run_time=1.0)
        self.wait(1.4)
        self.play(fade_tracker.animate.set_value(0.0), run_time=0.9)
        tracker.set_value(1)                       # el helecho vuelve a empezar de cero
        main_op.set_value(0.0)
        fade_tracker.set_value(1.0)
        update_cloud(cloud)

        # =============================================================
        # 3. LOS PRIMEROS PASOS, DESPACIO
        # =============================================================
        cursor = Dot(pt(pts[0]), radius=0.12, color=YELLOW)
        cursor.set_z_index(6)
        self.play(*swap_caption("Empieza en un punto:\nel origen"),
                  FadeIn(cursor, scale=3), run_time=1.0)
        self.wait(0.8)

        plotted = VGroup()
        steps_caps = {0: "Elige una regla\nal azar", 1: "Aplícala al punto\ny márcalo", 2: "Y repite…"}
        for k in range(N_DEMO):
            j = int(idx[k])
            slow = k < 2
            cap = swap_caption(steps_caps[k]) if k in steps_caps else []
            self.play(Indicate(chips[j], scale_factor=1.25), *cap,
                      run_time=1.2 if slow else 0.5)
            if slow:
                self.wait(0.6)
            new_dot = Dot(pt(pts[k + 1]), radius=0.06, color=RULE_COLORS[j])
            new_dot.set_z_index(3)
            self.play(cursor.animate.move_to(pt(pts[k + 1])), FadeIn(new_dot, scale=3),
                      run_time=1.0 if slow else 0.4)
            plotted.add(new_dot)
            if slow:
                self.wait(0.5)

        # =============================================================
        # 4. ACELERACIÓN: miles de puntos
        # =============================================================
        counter = always_redraw(
            lambda: Text(f"{int(tracker.get_value()):,}".replace(",", "."),
                         font_size=84, weight=BOLD, color=COLOR_RESULT).move_to(DOWN * 3.5)
        )
        counter_label = Text("puntos", font_size=44, color=TXT_BASE).move_to(DOWN * 4.45)

        main_op.set_value(1.0)
        tracker.set_value(N_DEMO)
        update_cloud(cloud)
        self.play(FadeOut(VGroup(cursor, plotted)), FadeOut(chips),
                  *swap_caption("Ahora, miles\nde veces más…"), run_time=0.7)
        self.play(FadeIn(counter), FadeIn(counter_label), run_time=0.5)

        N0, N1 = N_DEMO, N_TOTAL

        def ramp(t):
            return (N0 * (N1 / N0) ** t - N0) / (N1 - N0)

        self.play(tracker.animate.set_value(N1), run_time=RAMP_TIME, rate_func=ramp)
        self.wait(1.0)

        # =============================================================
        # 5. REVELACIÓN: helecho de Barnsley, todo verde
        # =============================================================
        self.play(*swap_caption("Helecho de\nBarnsley", size=38, color=COLOR_RESULT),
                  gmix.animate.set_value(1.0),
                  FadeOut(VGroup(counter, counter_label)), run_time=1.6)
        self.wait(1.8)

        # =============================================================
        # 6. AUTOSEMEJANZA: la hoja izquierda es el helecho entero
        # =============================================================
        self.play(*swap_caption("Fíjate en\nesta hoja…"),
                  AnimationGroup(main_op.animate(run_time=1.2).set_value(0.25),
                                 leaf_op.animate(run_time=1.2).set_value(1.0),
                                 lag_ratio=0))
        self.wait(1.2)

        self.play(
            *swap_caption("…es una copia\ndel helecho entero"),
            AnimationGroup(
                zt.animate(run_time=4.2, rate_func=smooth).set_value(1.0),
                main_op.animate(run_time=1.5).set_value(0.0),
                leaf_green.animate(run_time=1.5, rate_func=linear).set_value(1.0),
                lag_ratio=0))
        self.wait(1.6)
        self.play(*swap_caption("Cada parte es\ncopia del todo", size=36, color=COLOR_RESULT),
                  run_time=0.8)
        self.wait(2.4)

        # =============================================================
        # 7. CIERRE Y LOGO
        # =============================================================
        self.play(FadeOut(cap_holder[0]), fade_tracker.animate.set_value(0.0), run_time=1.0)
        cloud.clear_updaters()
        self.remove(cloud)
        logo = MathTex(r"F_{GC}", font_size=150, color=COLOR_LOGO).move_to(ORIGIN)
        self.play(FadeIn(logo, scale=0.7), run_time=1.2)
        self.wait(2.5)