from manim import *

class LaMagiaDelNueve(Scene):
    def construct(self):
        # Paleta de colores minimalista
        TXT_BASE = ManimColor("#E1E1D5") 
        COLOR_NUEVE = PURPLE_B
        COLOR_SUMA = GREEN_C
        COLOR_LOGO = BLUE_C

        # =============================================================
        # EL GANCHO INICIAL - EL 9 GIGANTE
        # =============================================================
        gancho_txt = Text("La magia del", font_size=50, color=TXT_BASE)
        gancho_num = MathTex("9", font_size=300, color=COLOR_NUEVE)
        gancho_grupo = VGroup(gancho_txt, gancho_num).arrange(DOWN, buff=0.5)

        # Aparece el texto y se dibuja el 9 gigante
        self.play(FadeIn(gancho_txt, shift=UP*0.5), Write(gancho_num), run_time=1.5)
        
        # Un pequeño "latido" (pulso) para darle vida mientras terminas de hablar
        self.play(gancho_num.animate.scale(1.1), rate_func=there_and_back, run_time=0.8)
        self.wait(2.5) # Pausa para que termines tu frase introductoria

        # Se desvanece colapsando hacia el centro para dar paso a la tabla
        self.play(FadeOut(gancho_grupo, scale=0.8), run_time=1)

        # =============================================================
        # DESARROLLO - LA TABLA DEL 9
        # =============================================================
        multiplos = VGroup()
        
        for i in range(1, 11):
            res_str = f"{9 * i:02d}" 
            d1, d2 = res_str[0], res_str[1]
            
            eq = VGroup(
                MathTex(f"9 \\times {i} =", color=TXT_BASE),
                MathTex(d1, color=TXT_BASE),
                MathTex(d2, color=TXT_BASE),
                MathTex(r"\rightarrow", color=GRAY),
                MathTex(d1, color=COLOR_NUEVE),
                MathTex("+", color=TXT_BASE),
                MathTex(d2, color=COLOR_NUEVE),
                MathTex("=", color=TXT_BASE),
                MathTex("9", color=COLOR_SUMA, font_size=69) 
            ).arrange(RIGHT, buff=0.2)
            
            multiplos.add(eq)

        # Escala grande y centrada para formato vertical
        multiplos.arrange(DOWN, aligned_edge=LEFT, buff=0.35).scale(1.15).move_to(ORIGIN)

        # Animación con pausas para que puedas dictar las sumas
        for eq in multiplos:
            self.play(FadeIn(eq[0:3], shift=RIGHT*0.2), run_time=0.6)
            self.wait(0.3) 
            
            self.play(FadeIn(eq[3:7], shift=RIGHT*0.1), run_time=0.6)
            self.play(Write(eq[7:]), run_time=0.6)
            
            self.wait(1.8) 

        self.wait(1.9)
        self.play(FadeOut(multiplos, shift=DOWN), run_time=1.9)

 # =============================================================
        # OUTRO / EL RETO
        # =============================================================
        pregunta = Text("¿Por qué pasa esto?", font_size=45, weight=BOLD, color=TXT_BASE).move_to(UP * 1.5)
        cta1 = Text("Si sabes la respuesta, déjala en los comentarios.", font_size=26, color=GRAY).next_to(pregunta, DOWN, buff=0.6)
        cta2 = Text("Si quieres saberla, sígueme.", font_size=26, color=GRAY).next_to(cta1, DOWN, buff=0.3)
        
        logo = MathTex(r"F_{GC}", font_size=90, color=COLOR_LOGO).next_to(cta2, DOWN, buff=1.2)
        
        self.play(Write(pregunta), run_time=1.0)
        
        self.play(
            FadeIn(cta1, shift=UP*0.2),
            FadeIn(cta2, shift=UP*0.2),
            run_time=1.2
        )
        
        self.play(FadeIn(logo, scale=0.8), run_time=1.5)
        self.wait(3)