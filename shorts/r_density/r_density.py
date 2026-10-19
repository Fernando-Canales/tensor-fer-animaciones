from manim import *

class DensidadDeLosReales(MovingCameraScene):

    def construct(self):
        # -------------------------------------------------------------
        # ESCENA 1: NEGRO (0:00 - 0:04)
        # -------------------------------------------------------------
        self.wait(4)

        # -------------------------------------------------------------
        # ESCENA 2: R Y RECTA NUMÉRICA (0:04 - 0:08)
        # -------------------------------------------------------------
        simbolo_r = MathTex(r"\mathbb{R}", font_size=120, color=BLUE_B)
        recta_base = NumberLine(
            x_range=[-5, 5, 1],
            length=10,
            color=WHITE,
            include_numbers=True,
            font_size=24
        ).shift(DOWN * 2)

        self.play(FadeIn(simbolo_r, scale=0.5), run_time=1.5)
        self.play(Create(recta_base), run_time=2)
        self.wait(0.5)

        # -------------------------------------------------------------
        # ESCENA 3: ZOOM INICIAL AL NÚMERO 2 (0:08 - 0:16)
        # -------------------------------------------------------------
        self.play(FadeOut(simbolo_r), run_time=1)
        
        punto_dos = recta_base.n2p(2)
        
        self.play(
            self.camera.frame.animate.set(width=4).move_to(punto_dos + UP * 0.5),
            run_time=4
        )
        
        interrogacion = MathTex("?", color=YELLOW, font_size=60).next_to(punto_dos, UP * 2)
        self.play(Write(interrogacion), run_time=1.5)
        self.wait(1)

        # -------------------------------------------------------------
        # ESCENA 4 y 5: LISTA DE NÚMEROS (reemplaza el zoom) (0:16 - 0:32)
        # -------------------------------------------------------------
        self.play(
            FadeOut(interrogacion),
            self.camera.frame.animate.set(width=8).move_to(ORIGIN),
            run_time=2
        )

        n1 = MathTex("2.", "1", font_size=44)
        n2 = MathTex("2.", "0", "1", font_size=44)
        n3 = MathTex("2.", "00", "1", font_size=44)
        n4 = MathTex("2.", "0000000", r"\ldots", font_size=44)
        for n in (n1, n2, n3, n4):
            n[1].set_color(YELLOW)
        puntos = MathTex(r"\vdots", font_size=44, color=YELLOW)

        lista = VGroup(n1, n2, n3, n4, puntos).arrange(DOWN, buff=0.28, aligned_edge=LEFT)
        lista.move_to(UP * 0.4)

        self.play(Write(n1), run_time=1)
        self.wait(1.5)
        self.play(Write(n2), run_time=1)
        self.wait(1.5)
        self.play(Write(n3), run_time=1)
        self.wait(1.5)
        self.play(Write(n4), run_time=1)
        self.wait(2)
        self.play(FadeIn(puntos), run_time=1)
        self.wait(2)

        # -------------------------------------------------------------
        # ESCENA 6: "NO EXISTE" Y REGRESO DE CÁMARA (0:32 - 0:45)  [igual que antes]
        # -------------------------------------------------------------
        no_existe = Text("NO EXISTE", font_size=40, weight=BOLD, color=RED).next_to(punto_dos, UP * 2)

        self.play(
            FadeOut(lista),
            self.camera.frame.animate.set(width=4).move_to(punto_dos + UP * 0.5),
            run_time=1.5
        )
        
        self.play(Write(no_existe), run_time=2)
        self.wait(1.5)
        
        int_izq = MathTex("?", color=RED, font_size=40).next_to(punto_dos, LEFT * 0.8 + UP * 0.5)
        int_der = MathTex("?", color=RED, font_size=40).next_to(punto_dos, RIGHT * 0.8 + UP * 0.5)
        
        self.play(FadeIn(int_izq), FadeIn(int_der), run_time=2)
        self.wait(4.5)

        # -------------------------------------------------------------
        # ESCENA 7: DENSIDAD (0:45 - 0:50)
        # -------------------------------------------------------------
        self.play(
            FadeOut(no_existe), FadeOut(int_izq), FadeOut(int_der),
            self.camera.frame.animate.set(width=8).move_to(ORIGIN),
            run_time=1.5
        )
        
        txt_densidad = Text("DENSIDAD", font_size=50, weight=BOLD, color=BLUE).move_to(UP * 1.5)
        self.play(Write(txt_densidad), run_time=1.5)
        self.wait(2)

        # -------------------------------------------------------------
        # ESCENA 8: PUNTOS MEDIOS RECURSIVOS (0:50 - 1:05)
        # -------------------------------------------------------------
        self.play(FadeOut(txt_densidad), FadeOut(recta_base), run_time=1)
        
        pos_a = LEFT * 3
        pos_b = RIGHT * 3
        
        recta_ab = Line(pos_a, pos_b, color=WHITE).shift(DOWN * 0.5)
        dot_a = Dot(recta_ab.get_start(), color=GREEN)
        dot_b = Dot(recta_ab.get_end(), color=GREEN)
        lbl_a = MathTex("a", font_size=36).next_to(dot_a, DOWN)
        lbl_b = MathTex("b", font_size=36).next_to(dot_b, DOWN)

        self.play(Create(recta_ab), FadeIn(dot_a), FadeIn(dot_b), Write(lbl_a), Write(lbl_b), run_time=2)

        # 1er Punto Medio (Amarillo) en x = 0
        pos_m1 = recta_ab.get_center()
        dot_m1 = Dot(pos_m1, color=YELLOW)
        
        brace = Brace(recta_ab, UP, color=GRAY_B)
        lbl_m1 = MathTex(r"\frac{a+b}{2}", font_size=36, color=YELLOW).next_to(brace, UP, buff=0.35)

        self.play(Create(brace), FadeIn(dot_m1), Write(lbl_m1), run_time=2.5)
        self.wait(1)

        # 2do Punto Medio (Naranja) exactamente a la mitad entre 'a' y 'm1'
        pos_m2 = (recta_ab.get_start() + pos_m1) / 2
        dot_m2 = Dot(pos_m2, color=ORANGE)

        self.play(
            self.camera.frame.animate.set(width=4.5).move_to(pos_m2 + UP * 0.3),
            run_time=2.5
        )
        self.play(FadeIn(dot_m2, scale=1.3), run_time=1)
        self.wait(1)

        # 3er Punto Medio (Azul) exactamente a la mitad entre 'a' y 'm2'
        pos_m3 = (recta_ab.get_start() + pos_m2) / 2
        dot_m3 = Dot(pos_m3, color=BLUE_B)

        self.play(
            self.camera.frame.animate.set(width=2.5).move_to(pos_m3 + UP * 0.2),
            run_time=2.5
        )
        self.play(FadeIn(dot_m3, scale=1.3), run_time=1)
        self.wait(1.5)

        # -------------------------------------------------------------
        # ESCENA 9: ZOOM OUT Y CIERRE CON LOGO CENTRADO (1:05 - 1:15)
        # -------------------------------------------------------------
        self.play(
            self.camera.frame.animate.set(width=8).move_to(ORIGIN),
            run_time=2.5
        )
        
        frase_final = Text("Sin huecos... sin vecinos.", font_size=36, color=WHITE).move_to(UP * 2)
        self.play(Write(frase_final), run_time=2)
        self.wait(1.5)

        # Desvanecimiento completo antes de mostrar el logo
        elementos_a_limpiar = VGroup(
            recta_ab, dot_a, dot_b, lbl_a, lbl_b,
            dot_m1, dot_m2, dot_m3, brace, lbl_m1, frase_final
        )
        self.play(FadeOut(elementos_a_limpiar), run_time=1.5)

        # Logo final centrado
        logo = MathTex(r"F_{GC}", font_size=80, color=BLUE_A).move_to(ORIGIN)
        self.play(FadeIn(logo, scale=0.7), run_time=2)
        self.wait(2)
        