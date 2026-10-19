from manim import *

class PotenciasDeTres(Scene):
    def construct(self):
        # Paleta de colores de alto contraste
        TXT_BASE = ManimColor("#E1E1D5")
        COLOR_DESTACADO = YELLOW
        COLOR_CICLO = YELLOW
        COLOR_LOGO = BLUE_C

        # =============================================================
        # HOOK INICIAL
        # =============================================================
        titulo = Text(
            "¿Te habías fijado\nen esto?", 
            font_size=46, 
            weight=BOLD, 
            color=COLOR_DESTACADO,
            line_spacing=0.8
        ).to_edge(UP, buff=0.4)
        
        self.play(Write(titulo), run_time=1.2)
        self.wait(5.5)

        # =============================================================
        # SECUENCIA DE POTENCIAS (Hasta 3^9 + Puntos suspensivos)
        # =============================================================
        p1 = MathTex("3^1 = ", "3", color=TXT_BASE)
        p2 = MathTex("3^2 = ", "9", color=TXT_BASE)
        p3 = MathTex("3^3 = 2", "7", color=TXT_BASE)
        p4 = MathTex("3^4 = 8", "1", color=TXT_BASE)
        p5 = MathTex("3^5 = 24", "3", color=TXT_BASE)
        p6 = MathTex("3^6 = 72", "9", color=TXT_BASE)
        p7 = MathTex("3^7 = 218", "7", color=TXT_BASE)
        p8 = MathTex("3^8 = 656", "1", color=TXT_BASE)
        p9 = MathTex("3^9 = 1968", "3", color=TXT_BASE)
        puntos = MathTex(r"\vdots", color=TXT_BASE)

        secuencia = VGroup(
            p1, p2, p3, p4, p5, p6, p7, p8, p9, puntos
        ).arrange(DOWN, buff=0.18).scale(1.05).next_to(titulo, DOWN, buff=0.3)

        potencias = [p1, p2, p3, p4, p5, p6, p7, p8, p9]
        
        # Tiempos de espera escalonados (crecen conforme los números se vuelven más largos de pronunciar)
        tiempos_espera = [1.4, 1.4, 1.6, 1.6, 1.8, 1.8, 2.1, 2.2, 2.5]

        for p, t_wait in zip(potencias, tiempos_espera):
            self.play(FadeIn(p, shift=UP*0.1), run_time=0.4)
            self.wait(t_wait)

        # Aparecen los puntos suspensivos
        self.play(FadeIn(puntos, shift=UP*0.1), run_time=0.5)
        self.wait(1.5)

        # =============================================================
        # RESALTAR LAS ÚLTIMAS CIFRAS Y EXPLICAR EL CICLO
        # =============================================================
        self.play(
            *(p[1].animate.set_color(COLOR_CICLO) for p in potencias),
            run_time=0.8
        )
        self.wait(8.5) # Pausa generosa para explicar el ciclo (3, 9, 7, 1...)

        # =============================================================
        # TRANSICIÓN: EJEMPLO DE 3^10
        # =============================================================
        self.play(FadeOut(secuencia), run_time=0.8)

        ejemplo_10 = MathTex("3^{10} = \\dots 9", color=TXT_BASE, font_size=50)
        ejemplo_10.set_color_by_tex("9", COLOR_CICLO)
        ejemplo_10.next_to(titulo, DOWN, buff=1.5)

        self.play(FadeIn(ejemplo_10, shift=UP*0.2), run_time=0.8)
        self.wait(4.0) # Espacio para: "Quizá no sepa cuánto vale 3 a la 10, pero sé que termina en 9"

        self.play(FadeOut(ejemplo_10), run_time=0.6)

        # =============================================================
        # OUTRO / RETO FINAL (3^100)
        # =============================================================
        self.play(FadeOut(titulo), run_time=0.6)

        pregunta_final = Text(
            "¿En qué cifra terminará\n3 elevado a la 100?", 
            font_size=40, 
            weight=BOLD, 
            color=TXT_BASE,
            line_spacing=0.8
        ).move_to(UP * 2.0)
        
        cta1 = Text("Escribe tu respuesta en los comentarios", font_size=24, color=GRAY).next_to(pregunta_final, DOWN, buff=0.4)
        cta2 = Text("Sígueme para más trucos", font_size=24, color=GRAY).next_to(cta1, DOWN, buff=0.2)
        
        logo = MathTex(r"F_{GC}", font_size=85, color=COLOR_LOGO).next_to(cta2, DOWN, buff=0.8)

        self.play(Write(pregunta_final), run_time=1.0)
        self.play(
            FadeIn(cta1, shift=UP*0.2),
            FadeIn(cta2, shift=UP*0.2),
            run_time=1.2
        )
        self.play(FadeIn(logo, scale=0.8), run_time=1.2)
        self.wait(4.0)