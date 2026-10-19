from manim import *

class AcertijoAguaHorizontal(Scene):
    def construct(self):
        # Paleta de colores de alto contraste
        COLOR_5L = BLUE_D
        COLOR_3L = GREEN_D
        COLOR_WATER = BLUE_E
        TXT_BASE = ManimColor("#E1E1D5")
        COLOR_LOGO = BLUE_C

        # =============================================================
        # 1. INTRO / GANCHO INICIAL (Título + Recipientes vacíos + Pregunta)
        # =============================================================
        try:
            imagen_inicio = ImageMobject("icono_acertijo.png").scale(0.8)
            has_image = True
        except:
            has_image = False

        texto_titulo = Text(
            "El Acertijo de los 4 Litros",
            font_size=42,
            weight=BOLD,
            color=COLOR_WATER
        )

        if has_image:
            grupo_titulo = VGroup(imagen_inicio, texto_titulo).arrange(RIGHT, buff=0.4)
        else:
            grupo_titulo = texto_titulo

        grupo_titulo.to_edge(UP, buff=0.5)

        # Recipientes vacíos para la intro
        w_jug = 1.4
        h_5l = 3.5
        h_3l = 2.1

        jug_5_intro = Rectangle(width=w_jug, height=h_5l, color=TXT_BASE, stroke_width=3)
        label_5_intro = MathTex(r"\text{Recipiente 5L}", color=TXT_BASE, font_size=26).next_to(jug_5_intro, DOWN, buff=0.2)
        grupo_5_intro = VGroup(jug_5_intro, label_5_intro)

        jug_3_intro = Rectangle(width=w_jug, height=h_3l, color=TXT_BASE, stroke_width=3)
        label_3_intro = MathTex(r"\text{Recipiente 3L}", color=TXT_BASE, font_size=26).next_to(jug_3_intro, DOWN, buff=0.2)
        grupo_3_intro = VGroup(jug_3_intro, label_3_intro)

        grupo_jugs_intro = VGroup(grupo_5_intro, grupo_3_intro).arrange(RIGHT, buff=3.0, aligned_edge=DOWN)
        grupo_jugs_intro.move_to(ORIGIN).shift(DOWN * 0.3)

        texto_hook = Text(
            "¿Cómo medir 4 Litros exactos?",
            font_size=36,
            color=TXT_BASE,
            weight=BOLD
        ).to_edge(UP, buff=1.6)

        # Animación de entrada de la intro
        if has_image:
            self.play(FadeIn(imagen_inicio, shift=LEFT*0.3), Write(texto_titulo), run_time=1.5)
        else:
            self.play(Write(texto_titulo), run_time=1.5)

        self.play(
            FadeIn(grupo_jugs_intro, shift=UP*0.3),
            Write(texto_hook),
            run_time=1.8
        )
        self.wait(4.0)

        # Desvanecer todo el bloque de la intro para limpiar la pantalla
        animaciones_salida = [
            FadeOut(grupo_jugs_intro, shift=DOWN*0.3),
            FadeOut(texto_hook, shift=UP*0.3),
            FadeOut(texto_titulo, shift=UP*0.3)
        ]
        if has_image:
            animaciones_salida.append(FadeOut(imagen_inicio, shift=UP*0.3))

        self.play(*animaciones_salida, run_time=1.2)
        self.wait(0.8)

        # =============================================================
        # 2. CONFIGURACIÓN DE RECIPIENTES PARA EL TUTORIAL (Alineados en el suelo)
        # =============================================================
        jug_5 = Rectangle(width=w_jug, height=h_5l, color=TXT_BASE, stroke_width=3)
        label_5 = MathTex(r"\text{Recipiente 5L}", color=TXT_BASE, font_size=26).next_to(jug_5, DOWN, buff=0.2)
        grupo_5 = VGroup(jug_5, label_5)

        jug_3 = Rectangle(width=w_jug, height=h_3l, color=TXT_BASE, stroke_width=3)
        label_3 = MathTex(r"\text{Recipiente 3L}", color=TXT_BASE, font_size=26).next_to(jug_3, DOWN, buff=0.2)
        grupo_3 = VGroup(jug_3, label_3)

        grupo_jugs = VGroup(grupo_5, grupo_3).arrange(RIGHT, buff=3.0, aligned_edge=DOWN)
        grupo_jugs.move_to(ORIGIN).shift(DOWN * 0.3)

        self.play(FadeIn(grupo_jugs, shift=UP*0.3), run_time=1.5)
        self.wait(0.8)

        # Funciones auxiliares para agua y etiquetas de litros en tiempo real
        def crear_agua(jug, litros, max_litros):
            altura_max = jug.height - 0.1
            altura_agua = (litros / max_litros) * altura_max
            agua = Rectangle(
                width=jug.width - 0.1,
                height=max(0.01, altura_agua),
                color=COLOR_WATER,
                fill_opacity=0.6
            ).set_stroke(width=0)
            agua.align_to(jug, DOWN).align_to(jug, LEFT)
            agua.shift(UP * 0.05 + RIGHT * 0.05)
            return agua

        def obtener_indicador_litros(jug, litros):
            return Text(f"{litros} L", color=COLOR_WATER, font_size=32, weight=BOLD).next_to(jug, UP, buff=0.3)

        # Inicializamos agua en 0 y etiquetas superiores
        agua_5 = crear_agua(jug_5, 0, 5)
        agua_3 = crear_agua(jug_3, 0, 3)
        self.add(agua_5, agua_3)

        indicador_5 = obtener_indicador_litros(jug_5, 0)
        indicador_3 = obtener_indicador_litros(jug_3, 0)
        self.play(FadeIn(indicador_5), FadeIn(indicador_3), run_time=1.0)

        # Cuadro de texto explicativo inferior
        def mostrar_paso(texto_str):
            return Text(texto_str, font_size=24, color=TXT_BASE).to_edge(DOWN, buff=0.5)

        paso_actual = None

        def actualizar_estado(l_5, l_6, texto_str):
            nonlocal agua_5, agua_3, indicador_5, indicador_3, paso_actual
            
            nuevo_agua_5 = crear_agua(jug_5, l_5, 5)
            nuevo_agua_3 = crear_agua(jug_3, l_6, 3)
            
            nuevo_ind_5 = obtener_indicador_litros(jug_5, l_5)
            nuevo_ind_3 = obtener_indicador_litros(jug_3, l_6)

            nuevo_texto = mostrar_paso(texto_str)

            animaciones = [
                Transform(agua_5, nuevo_agua_5),
                Transform(agua_3, nuevo_agua_3),
                Transform(indicador_5, nuevo_ind_5),
                Transform(indicador_3, nuevo_ind_3)
            ]

            if paso_actual is not None:
                animaciones.append(FadeOut(paso_actual, run_time=1.0))
            
            animaciones.append(Write(nuevo_texto, run_time=1.2))
            
            self.play(*animaciones, run_time=2.0)
            paso_actual = nuevo_texto

        # =============================================================
        # 3. SECUENCIA DE PASOS DE LA SOLUCIÓN
        # =============================================================

        # PASO 1
        actualizar_estado(5, 0, "Paso 1: Llenar por completo el recipiente de 5 litros.")
        self.wait(3.5)

        # PASO 2
        actualizar_estado(2, 3, "Paso 2: Verter agua del de 5L al de 3L hasta llenarlo (quedan 2L).")
        self.wait(3.5)

        # PASO 3
        actualizar_estado(2, 0, "Paso 3: Vaciar por completo el recipiente de 3 litros.")
        self.wait(3.0)

        # PASO 4
        actualizar_estado(0, 2, "Paso 4: Pasar los 2 litros restantes al recipiente pequeño.")
        self.wait(3.5)

        # PASO 5
        actualizar_estado(5, 2, "Paso 5: Volver a llenar por completo el recipiente de 5 litros.")
        self.wait(3.5)

        # PASO 6
        actualizar_estado(4, 3, "Paso 6: Llenar el de 3L (le falta 1L). ¡Quedan exactos 4L en el grande!")
        self.wait(4.5)

        # =============================================================
        # 4. CIERRE Y LOGO
        # =============================================================
        self.play(
            FadeOut(grupo_jugs, run_time=1.5),
            FadeOut(agua_5, run_time=1.5),
            FadeOut(agua_3, run_time=1.5),
            FadeOut(indicador_5, run_time=1.5),
            FadeOut(indicador_3, run_time=1.5),
            FadeOut(paso_actual, run_time=1.5),
            run_time=1.5
        )

        logo = MathTex(r"F_{GC}", font_size=100, color=COLOR_LOGO).move_to(ORIGIN)
        self.play(FadeIn(logo, scale=0.7), run_time=1.8)
        self.wait(4.0)