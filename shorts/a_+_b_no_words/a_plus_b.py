from manim import *

class DemostracionSinPalabrasFinal(Scene):
    def construct(self):
        # Paleta de colores de alto contraste
        COLOR_A = BLUE_D
        COLOR_B = GREEN_D
        COLOR_AB = YELLOW_D
        TXT_BASE = ManimColor("#E1E1D5")
        COLOR_LOGO = BLUE_C

        # Factor de escalado global equilibrado para evitar choques
        FACTOR_GRANDE = 1.45

        # =============================================================
        # 1. TÍTULO INICIAL
        # =============================================================
        titulo = Text(
            "Demostración sin palabras",
            font_size=42,
            weight=BOLD,
            color=COLOR_AB

        ).scale(FACTOR_GRANDE).to_edge(UP, buff=0.5)

        subtitulo = MathTex(
            "(a + b)^2 = a^2 + 2ab + b^2",
            color=COLOR_B,
            font_size=40
        ).scale(FACTOR_GRANDE).next_to(titulo, DOWN, buff=0.15)

        # =============================================================
        # 2. GEOMETRÍA Y ELEMENTOS CENTRALES
        # =============================================================
        a_val = 2.8
        b_val = 1.2
        
        sq_a = Square(side_length=a_val, color=COLOR_A, fill_opacity=0.35).set_stroke(COLOR_A, width=4)
        sq_b = Square(side_length=b_val, color=COLOR_B, fill_opacity=0.35).set_stroke(COLOR_B, width=4)
        rect_ab1 = Rectangle(width=a_val, height=b_val, color=COLOR_AB, fill_opacity=0.35).set_stroke(COLOR_AB, width=4)
        rect_ab2 = Rectangle(width=b_val, height=a_val, color=COLOR_AB, fill_opacity=0.35).set_stroke(COLOR_AB, width=4)

        # Posicionamiento de piezas
        sq_a.move_to(ORIGIN, aligned_edge=DL)
        rect_ab1.next_to(sq_a, UP, buff=0)
        sq_b.next_to(rect_ab1, RIGHT, buff=0)
        rect_ab2.next_to(sq_a, RIGHT, buff=0)

        figura_completa = VGroup(sq_a, rect_ab1, sq_b, rect_ab2)

        # Acotaciones
        brace_a_bottom = Brace(sq_a, DOWN, buff=0.1, color=TXT_BASE)
        label_a_bottom = brace_a_bottom.get_tex("a", buff=0.1)
        brace_b_bottom = Brace(rect_ab2, DOWN, buff=0.1, color=TXT_BASE)
        label_b_bottom = brace_b_bottom.get_tex("b", buff=0.1)
        brace_a_left = Brace(sq_a, LEFT, buff=0.1, color=TXT_BASE)
        label_a_left = brace_a_left.get_tex("a", buff=0.1)
        brace_b_left = Brace(rect_ab1, LEFT, buff=0.1, color=TXT_BASE)
        label_b_left = brace_b_left.get_tex("b", buff=0.1)

        # Etiquetas de Área Interna
        label_a2 = MathTex("a^2", color=COLOR_A, font_size=46).move_to(sq_a.get_center())
        label_ab1 = MathTex("ab", color=COLOR_AB, font_size=46).move_to(rect_ab1.get_center())
        label_ab2 = MathTex("ab", color=COLOR_AB, font_size=46).move_to(rect_ab2.get_center())
        label_b2 = MathTex("b^2", color=COLOR_B, font_size=46).move_to(sq_b.get_center())

        # Agrupamos y desplazamos la geometría un poco más abajo para dejar espacio arriba
        objects_centrales = VGroup(
            figura_completa,
            brace_a_bottom, label_a_bottom, brace_b_bottom, label_b_bottom, 
            brace_a_left, label_a_left, brace_b_left, label_b_left,
            label_a2, label_ab1, label_ab2, label_b2
        )
        objects_centrales.scale(FACTOR_GRANDE).move_to(ORIGIN).shift(DOWN * 0.45)

        # =============================================================
        # 3. FÓRMULA FINAL (Con colores explícitos por partes)
        # =============================================================
        formula = MathTex(
            "(a + b)^2 = ",  # 0
            "a^2",            # 1 -> Azul
            " + ",            # 2
            "2ab",            # 3 -> Amarillo
            " + ",            # 4
            "b^2",            # 5 -> Verde
            font_size=42
        )
        formula[0].set_color(TXT_BASE)
        formula[1].set_color(COLOR_A)
        formula[2].set_color(TXT_BASE)
        formula[3].set_color(COLOR_AB)
        formula[4].set_color(TXT_BASE)
        formula[5].set_color(COLOR_B)

        formula.scale(FACTOR_GRANDE).to_edge(UP, buff=0.15)

        # =============================================================
        # 4. LOGO FINAL (En el CENTRO de la pantalla)
        # =============================================================
        logo = MathTex(r"F_{GC}", font_size=90, color=COLOR_LOGO).move_to(ORIGIN)

        # =============================================================
        # SECUENCIA DE ANIMACIONES
        # =============================================================

        # Paso 0: Título inicial y su desvanecimiento
        self.play(Write(titulo), run_time=1.5)
        self.wait(2.0)

        self.play(Write(subtitulo), run_time=1.5)
        self.wait(3.0)
        self.play(FadeOut(titulo, shift=UP*0.3), run_time=0.8)
        self.play(FadeOut(subtitulo, shift=UP*0.2), run_time=0.8)

        # Paso 1: Cuadrado base (a^2) y sus acotaciones
        self.play(FadeIn(sq_a, shift=UP*0.2), run_time=1.2)
        self.play(
            Create(brace_a_bottom), Write(label_a_bottom), 
            Create(brace_a_left), Write(label_a_left), 
            run_time=1.2
        )
        self.wait(3.0)

        # Paso 2: Rectángulos (ab) y sus acotaciones
        self.play(FadeIn(rect_ab1, shift=LEFT*0.2), FadeIn(rect_ab2, shift=DOWN*0.2), run_time=1.4)
        self.play(
            Create(brace_b_left), Write(label_b_left), 
            Create(brace_b_bottom), Write(label_b_bottom), 
            run_time=1.2
        )
        self.wait(2.0)

        # Paso 3: Cuadrado pequeño (b^2)
        self.play(FadeIn(sq_b, shift=DOWN*0.2), run_time=1.2)
        self.wait(2.0)

        # Paso 4: Rellenar áreas internas
        self.play(
            Write(label_a2),
            Write(label_ab1),
            Write(label_ab2),
            Write(label_b2),
            run_time=1.8
        )
        self.wait(3.0)

        # Paso 5: Revelar la fórmula completa arriba
        self.play(Write(formula), run_time=1.8)
        self.wait(3.0)

        # Paso 6: Desvanecer TODO lo que está en pantalla
        self.play(
            FadeOut(objects_centrales, shift=DOWN*0.3),
            FadeOut(formula, shift=UP*0.3),
            run_time=1.2
        )
        self.wait(0.5)

        # Paso 7: Hacer aparecer el logo centrado
        self.play(FadeIn(logo, scale=0.7), run_time=1.5)
        self.wait(4.0)