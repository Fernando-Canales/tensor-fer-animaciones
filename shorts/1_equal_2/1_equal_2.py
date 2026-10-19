from manim import *

class DemostracionFalsa(Scene):
    def construct(self):
        # Paleta de colores de alto contraste
        TXT_BASE = ManimColor("#E1E1D5")
        COLOR_DESTACADO = YELLOW
        COLOR_LOGO = BLUE_C

        # =============================================================
        # HOOK INICIAL
        # =============================================================
        titulo = Text(
            "¿Eres capaz de encontrar\nel error?", 
            font_size=42, 
            weight=BOLD, 
            color=COLOR_DESTACADO,
            line_spacing=0.8
        ).to_edge(UP, buff=0.4)
        
        self.play(Write(titulo), run_time=1.2)
        self.wait(4.5)

        # =============================================================
        # PASOS DE LA DEMOSTRACIÓN (Lentos, pausados y limpios)
        # =============================================================
        paso1 = MathTex("x = y", color=TXT_BASE)
        paso2 = MathTex("x^2 = xy", color=TXT_BASE)
        paso3 = MathTex("x^2 - y^2 = xy - y^2", color=TXT_BASE)
        
        # Paso 4 con color base uniforme (sin dar pistas de color)
        paso4 = MathTex("(x + y)", "(x - y)", " = y", "(x - y)", color=TXT_BASE)

        paso5 = MathTex("x + y = y", color=TXT_BASE)
        paso6 = MathTex("y + y = y", color=TXT_BASE)
        paso7 = MathTex("2y = y", color=TXT_BASE)
        paso8 = MathTex("2 = 1", color=RED_B, font_size=80) # El absurdo final en rojo

        demostracion = VGroup(
            paso1, paso2, paso3, paso4, paso5, paso6, paso7, paso8
        ).arrange(DOWN, buff=0.35).scale(1.15).next_to(titulo, DOWN, buff=0.6)

        # 1. Empezamos con x = y
        self.play(FadeIn(paso1, shift=UP*0.2), run_time=0.6)
        self.wait(3.5)

        # 2. Multiplicamos por x
        self.play(FadeIn(paso2, shift=UP*0.2), run_time=0.6)
        self.wait(3.0)

        # 3. Restamos y^2
        self.play(FadeIn(paso3, shift=UP*0.2), run_time=0.6)
        self.wait(3.0)

        # 4. Factorizamos
        self.play(FadeIn(paso4, shift=UP*0.2), run_time=0.8)
        self.wait(7.5)

        # Línea de cancelación simple y neutral (sin estridencias)
        linea1 = Line(paso4[1].get_corner(DL), paso4[1].get_corner(UR), color=TXT_BASE, stroke_width=2.5)
        linea2 = Line(paso4[3].get_corner(DL), paso4[3].get_corner(UR), color=TXT_BASE, stroke_width=2.5)
        self.play(Create(linea1), Create(linea2), run_time=0.8)
        self.wait(3)

        # 5. x + y = y
        self.play(FadeIn(paso5, shift=UP*0.2), run_time=0.6)
        self.wait(3)

        # 6. y + y = y
        self.play(FadeIn(paso6, shift=UP*0.2), run_time=0.6)
        self.wait(2.5)

        # 7. 2y = y
        self.play(FadeIn(paso7, shift=UP*0.2), run_time=0.6)
        self.wait(3.0)

        # 8. Resultado absurdo: 2 = 1
        self.play(Write(paso8), run_time=1.0)
        self.wait(4.5)

        # =============================================================
        # OUTRO / RETO FINAL
        # =============================================================
        self.play(
            FadeOut(titulo), FadeOut(demostracion), FadeOut(linea1), FadeOut(linea2),
            run_time=1.0
        )

        pregunta_final = Text(
            "¿En qué paso falló\nla lógica?", 
            font_size=52, 
            weight=BOLD, 
            color=TXT_BASE,
            line_spacing=0.8
        ).move_to(UP * 1.5)
        
        cta1 = Text("Escribe la solución en los comentarios", font_size=35, color=GRAY).next_to(pregunta_final, DOWN, buff=0.5)
        cta2 = Text("Sígueme para saber la respuesta", font_size=35, color=GRAY).next_to(cta1, DOWN, buff=0.25)
        
        logo = MathTex(r"F_{GC}", font_size=90, color=COLOR_LOGO).next_to(cta2, DOWN, buff=1.0)

        self.play(Write(pregunta_final), run_time=1.0)
        self.play(
            FadeIn(cta1, shift=UP*0.2),
            FadeIn(cta2, shift=UP*0.2),
            run_time=1.2
        )
        self.play(FadeIn(logo, scale=0.8), run_time=1.2)
        self.wait(3.5)