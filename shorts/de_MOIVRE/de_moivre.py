from manim import *

# ---------------------------------------------------------------
# FORMATO DEL VIDEO
# Por defecto Manim renderiza en 16:9 (horizontal, 14.2 x 8 unidades). En un
# video horizontal la escena solo puede crecer hasta el alto de 8 unidades y
# el ancho queda vacío. Con PORTRAIT = True el script fuerza un cuadro
# vertical 9:16 de 6 x 10.67 unidades (1080x1920 px), el formato del short.
# Ponlo en False si quieres renderizar horizontal.
# ---------------------------------------------------------------
PORTRAIT = True
if PORTRAIT:
    config.pixel_width = 1080
    config.pixel_height = 1920
    config.frame_width = 6.0
    config.frame_height = 6.0 * 16 / 9


class EulerDeMoivreShort(Scene):
    def construct(self):
        # Paleta de colores de alto contraste
        TXT_BASE = ManimColor("#E1E1D5")
        COLOR_COS = BLUE_D
        COLOR_SIN = GREEN_D
        COLOR_MATH = BLUE_C
        COLOR_RESULT = YELLOW_D
        COLOR_LOGO = BLUE_C

        W = config.frame_width
        H = config.frame_height

        # ---------------------------------------------------------
        # Utilidades de layout (evitan que las cosas se empalmen)
        # ---------------------------------------------------------
        def fit_width(m, frac=0.92):
            """Reduce el objeto solo si se saldría del cuadro."""
            if m.width > W * frac:
                m.scale(W * frac / m.width)
            return m

        def step(label, body, gap=1.0):
            """Etiqueta arriba + cuerpo abajo, separados y centrados en pantalla."""
            g = VGroup(label, body).arrange(DOWN, buff=gap)
            fit_width(g)
            return g.move_to(ORIGIN)

        # =============================================================
        # 1. GANCHO INICIAL (SIN TÍTULO): pregunta + Euler en grande
        # =============================================================
        hook_q = Text(
            "¿De dónde sale?",
            font_size=62,
            weight=BOLD,
            color=TXT_BASE
        )
        hook_euler = MathTex(r"e^{i\pi} + 1 = 0", font_size=130, color=COLOR_RESULT)
        hook = VGroup(hook_q, hook_euler).arrange(DOWN, buff=0.9)
        fit_width(hook)
        hook.move_to(ORIGIN)

        self.play(Write(hook), run_time=1.4)
        self.wait(1.5)

        # =============================================================
        # 2. CONSTRUCCIÓN DEL LAYOUT (todo apilado con huecos medidos)
        # =============================================================
        UNIT = 1.3                      # 1 unidad del círculo
        WAVE_H = 1.3                    # alto de cada eje de onda

        # --- Título y fórmula de De Moivre ---
        title_moivre = Text(
            # En cuadros altos (9:16) el título va en 2 líneas: así es menos ancho
            # y toda la escena puede crecer más
            "Identidad de\nDe Moivre" if H / W > 1.4 else "Identidad de De Moivre",
            font_size=54 if H / W > 1.4 else 46,
            weight=BOLD,
            color=TXT_BASE,
            line_spacing=0.9
        )
        moivre_l1 = MathTex(r"(\cos \theta + i \sin \theta)^n", font_size=60, color=COLOR_MATH)
        moivre_l2 = MathTex(r"= \cos(n\theta) + i \sin(n\theta)", font_size=60, color=COLOR_MATH)
        formula_moivre = VGroup(moivre_l1, moivre_l2).arrange(DOWN, buff=0.25)

        # --- Círculo unitario (el radio coincide con la unidad de los ejes) ---
        circle_axes = Axes(
            x_range=[-1.25, 1.25, 1],
            y_range=[-1.25, 1.25, 1],
            x_length=2.5 * UNIT,
            y_length=2.5 * UNIT,
            axis_config={"color": TXT_BASE, "stroke_width": 2}
        )
        circle = Circle(radius=UNIT, color=TXT_BASE, stroke_width=2).move_to(circle_axes.c2p(0, 0))

        label_re = Text("Re", font_size=34, weight=BOLD, color=COLOR_COS).next_to(
            circle_axes.x_axis.get_end(), UP, buff=0.12
        )
        label_im = Text("Im", font_size=34, weight=BOLD, color=COLOR_SIN).next_to(
            circle_axes.y_axis.get_end(), RIGHT, buff=0.12
        )
        label_circle = Text(
            "Círculo\nunitario", font_size=34, color=TXT_BASE, line_spacing=0.9
        ).next_to(circle_axes, LEFT, buff=0.1).shift(UP * 1.0)

        circle_block = VGroup(circle_axes, circle, label_re, label_im, label_circle)

        # --- Onda de coseno (Real) ---
        wave_axes_cos = Axes(
            x_range=[0, 3*PI, PI],
            y_range=[-1.2, 1.2, 1],
            x_length=5.8,
            y_length=WAVE_H,
            axis_config={"color": TXT_BASE, "stroke_width": 2}
        )
        label_cos_axis = Text(
            "Coseno (Real)", font_size=36, color=COLOR_COS, weight=BOLD
        ).next_to(wave_axes_cos, UP, buff=0.15)
        cos_block = VGroup(wave_axes_cos, label_cos_axis)

        # --- Onda de seno (Imaginario) ---
        wave_axes_sin = Axes(
            x_range=[0, 3*PI, PI],
            y_range=[-1.2, 1.2, 1],
            x_length=5.8,
            y_length=WAVE_H,
            axis_config={"color": TXT_BASE, "stroke_width": 2}
        )
        label_sin_axis = Text(
            "Seno (Imaginario)", font_size=36, color=COLOR_SIN, weight=BOLD
        ).next_to(wave_axes_sin, UP, buff=0.15)
        sin_block = VGroup(wave_axes_sin, label_sin_axis)

        # --- Apilado vertical con huecos que reparten el espacio libre ---
        blocks = [title_moivre, formula_moivre, circle_block, cos_block, sin_block]
        keys = [title_moivre, formula_moivre, circle_axes, wave_axes_cos, wave_axes_sin]
        min_gaps = [0.45, 0.4, 0.4, 0.45]   # título→fórmula→círculo→coseno→seno

        avail_h = H - 0.8                   # margen arriba y abajo
        avail_w = W - 0.4                   # margen a los lados
        MAX_ZOOM = 1.8                      # tope de ampliación

        def stack(gaps):
            """Apila los bloques de arriba abajo, cada eje centrado en x = 0."""
            title_moivre.to_edge(UP, buff=0.0)
            title_moivre.shift(LEFT * title_moivre.get_center()[0])
            for i in range(1, len(blocks)):
                blocks[i].next_to(blocks[i - 1], DOWN, buff=gaps[i - 1])
                blocks[i].shift(LEFT * keys[i].get_center()[0])

        # 1) Apilado compacto y ampliación uniforme hasta llenar el cuadro
        #    (al ampliar todo por igual, nada puede empalmarse)
        stack(min_gaps)
        layout = VGroup(*blocks)
        k = min(avail_h / layout.height, avail_w / layout.width, MAX_ZOOM)
        layout.scale(k, about_point=np.array([0, layout.get_top()[1], 0]))

        # 2) Si sobra alto, se reparte entre los huecos (hasta 0.9 extra cada uno)
        scaled_gaps = [g * k for g in min_gaps]
        extra = avail_h - (sum(b.height for b in blocks) + sum(scaled_gaps))
        bonus = max(0.0, min(extra / 4, 0.9))
        stack([g + bonus for g in scaled_gaps])
        VGroup(*blocks).to_edge(UP, buff=0.4)

        # Grosor/tamaño de los trazos animados acompaña a la ampliación
        S = max(1.0, k)

        # =============================================================
        # 3. FÓRMULA DE EULER
        # =============================================================
        eu_label = Text(
            "Todo parte de la\nfórmula de Euler",
            font_size=52, weight=BOLD, color=COLOR_COS, line_spacing=1.1
        )
        eu_math = MathTex(r"e^{i\theta} = \cos\theta + i\sin\theta", font_size=76, color=COLOR_RESULT)
        eu_box = SurroundingRectangle(eu_math, color=COLOR_RESULT, buff=0.4, corner_radius=0.25)
        euler_screen = step(eu_label, VGroup(eu_box, eu_math), gap=1.2)

        self.play(FadeOut(hook), FadeIn(euler_screen, shift=UP * 0.2), run_time=1.0)
        self.wait(2.8)

        # =============================================================
        # 4. PASO 2: Evaluando con \theta = \pi
        # =============================================================
        label_2 = MathTex(r"\text{Evaluando con } \theta = \pi", font_size=58, color=COLOR_COS)
        math_2 = MathTex(r"e^{i\pi} = \cos(\pi) + i \sin(\pi)", font_size=75, color=COLOR_MATH)
        step2_group = step(label_2, math_2, gap=1.2)

        self.play(FadeOut(euler_screen), FadeIn(step2_group, scale=0.8), run_time=1.2)
        self.wait(2.2)

        # =============================================================
        # 5. PASO 3: Sustituyendo valores
        # =============================================================
        label_3 = MathTex(r"\text{Sustituyendo valores}", font_size=58, color=COLOR_COS)
        math_3 = MathTex(r"e^{i\pi} + 1 = 0", font_size=80, color=TXT_BASE)
        step3_group = step(label_3, math_3, gap=1.2)

        self.play(Transform(step2_group, step3_group), run_time=1.5)
        self.wait(2.2)

        # =============================================================
        # 6. RESULTADO FINAL GIGANTE
        # =============================================================
        res_math = MathTex(r"e^{i\pi} + 1 = 0", font_size=90, color=COLOR_RESULT)
        resultado_box = SurroundingRectangle(res_math, color=COLOR_RESULT, buff=0.5, corner_radius=0.3)
        grupo_final = VGroup(resultado_box, res_math).move_to(ORIGIN)

        self.play(Transform(step2_group, grupo_final), run_time=1.5)
        self.wait(3.0)

        # =============================================================
        # 7. "POR CIERTO": de Euler también se deduce la identidad de De Moivre
        #    (título + fórmula, y enseguida la animación del círculo)
        # =============================================================
        self.play(
            FadeOut(step2_group),
            FadeIn(title_moivre, shift=DOWN * 0.2),
            FadeIn(formula_moivre, shift=DOWN * 0.2),
            run_time=1.0
        )
        self.wait(1.2)

        # Tracker para animar el ángulo theta
        theta_tracker = ValueTracker(0.0)

        vector = always_redraw(lambda: Line(
            circle_axes.c2p(0, 0),
            circle_axes.c2p(np.cos(theta_tracker.get_value()), np.sin(theta_tracker.get_value())),
            color=YELLOW_D,
            stroke_width=4 * S
        ))

        dot = always_redraw(lambda: Dot(
            circle_axes.c2p(np.cos(theta_tracker.get_value()), np.sin(theta_tracker.get_value())),
            color=YELLOW_D,
            radius=0.1 * S
        ))

        cos_wave = always_redraw(lambda: wave_axes_cos.plot(
            lambda x: np.cos(x),
            x_range=[0, max(0.01, theta_tracker.get_value())],
            color=COLOR_COS,
            stroke_width=3.5 * S
        ))

        sin_wave = always_redraw(lambda: wave_axes_sin.plot(
            lambda x: np.sin(x),
            x_range=[0, max(0.01, theta_tracker.get_value())],
            color=COLOR_SIN,
            stroke_width=3.5 * S
        ))

        # Líneas punteras de proyección (tenues para no ensuciar los labels)
        pointer_cos = always_redraw(lambda: DashedLine(
            circle_axes.c2p(np.cos(theta_tracker.get_value()), np.sin(theta_tracker.get_value())),
            wave_axes_cos.c2p(theta_tracker.get_value(), np.cos(theta_tracker.get_value())),
            color=COLOR_COS,
            stroke_width=1.2 * S,
            stroke_opacity=0.6,
            dash_length=0.06 * S
        ))

        pointer_sin = always_redraw(lambda: DashedLine(
            circle_axes.c2p(np.cos(theta_tracker.get_value()), np.sin(theta_tracker.get_value())),
            wave_axes_sin.c2p(theta_tracker.get_value(), np.sin(theta_tracker.get_value())),
            color=COLOR_SIN,
            stroke_width=1.2 * S,
            stroke_opacity=0.6,
            dash_length=0.06 * S
        ))

        anim_group = VGroup(
            circle_block, cos_block, sin_block,
            vector, dot, cos_wave, sin_wave,
            pointer_cos, pointer_sin
        )

        self.play(FadeIn(anim_group, shift=UP * 0.2), run_time=1.2)

        # Giro hasta θ = π (misma velocidad que el giro completo: 3π en 5 s)
        self.play(theta_tracker.animate.set_value(PI), run_time=5.0 / 3, rate_func=linear)

        # ---- PAUSA EN θ = π: se resalta lo que se va a usar después ----
        ring = Circle(radius=0.3 * S, color=COLOR_RESULT, stroke_width=5 * S).move_to(circle_axes.c2p(-1, 0))
        mark_cos = Dot(wave_axes_cos.c2p(PI, -1), color=COLOR_COS, radius=0.14 * S)
        mark_sin = Dot(wave_axes_sin.c2p(PI, 0), color=COLOR_SIN, radius=0.14 * S)

        # Cada etiqueta va pegada al punto que describe (así no necesita un
        # recuadro aparte y se puede ver grande aunque el cuadro sea angosto)
        lab_theta = MathTex(r"\theta = \pi", font_size=46, color=COLOR_RESULT)
        lab_theta.next_to(circle_axes, RIGHT, buff=0.3).shift(DOWN * 0.6)
        lab_cos = MathTex(r"\cos \pi = -1", font_size=46, color=COLOR_COS)
        lab_cos.next_to(mark_cos, RIGHT, buff=0.35)
        lab_sin = MathTex(r"\sin \pi = 0", font_size=46, color=COLOR_SIN)
        lab_sin.next_to(mark_sin, UP + RIGHT, buff=0.1)

        # Que ninguna se salga del cuadro
        for lab in (lab_theta, lab_cos, lab_sin):
            room = W / 2 - 0.15 - lab.get_left()[0]
            if lab.width > room:
                lab.scale(room / lab.width, about_point=lab.get_left())
        readout = VGroup(lab_theta, lab_cos, lab_sin)

        self.play(
            Create(ring),
            FadeIn(mark_cos, scale=2),
            FadeIn(mark_sin, scale=2),
            Write(readout),
            run_time=1.0
        )
        self.wait(1.8)
        self.play(FadeOut(VGroup(ring, mark_cos, mark_sin, readout)), run_time=0.6)

        # Seguimos hasta la vuelta y media (3π) para mostrar la periodicidad
        self.play(theta_tracker.animate.set_value(3 * PI), run_time=10.0 / 3, rate_func=linear)
        self.wait(0.8)

        # Limpiamos TODO lo anterior de golpe
        self.play(FadeOut(VGroup(title_moivre, formula_moivre, anim_group)), run_time=1.0)

        # =============================================================
        # 5. CIERRE Y LOGO
        # =============================================================
        logo = MathTex(r"F_{GC}", font_size=150, color=COLOR_LOGO).move_to(ORIGIN)
        self.play(FadeIn(logo, scale=0.7), run_time=1.2)
        self.wait(2.5)