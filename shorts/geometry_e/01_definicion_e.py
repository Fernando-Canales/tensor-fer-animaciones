import numpy as np
from manim import *

class DefinicionGeometricaE(MovingCameraScene):
    def construct(self):

        # ============================================================
        # 1. HOOK 
        # ============================================================
        sym_pi = MathTex(r"\pi", font_size=80, color=BLUE_C).to_edge(LEFT, buff=2.5)
        sym_e = MathTex(r"e", font_size=80, color=YELLOW).to_edge(RIGHT, buff=2.5)
        
        intro_group = VGroup(sym_pi, sym_e)
        
        self.play(FadeIn(intro_group, shift=UP * 0.5), run_time=1)
        self.wait(2.5) 

        pi_eq = MathTex(r"\pi = \frac{\text{Circunferencia}}{\text{Diámetro}}", font_size=34)
        e_q = MathTex(r"e = \text{¿Qué figura es?}", font_size=38, color=BLUE_B)
        
        hook_text_group = VGroup(pi_eq, e_q).arrange(DOWN, buff=0.5).shift(UP * 2.5)

        self.play(
            FadeOut(intro_group, shift=UP),
            Write(pi_eq),
            run_time=1.5
        )
        self.wait(1.5) 
        
        self.play(Write(e_q))
        self.wait(2)
        
        self.play(FadeOut(hook_text_group))

        # ============================================================
        # 2. ESPIRAL VISUAL Y ECUACIÓN GLOBAL
        # ============================================================
        center = DOWN * 1.0

        def spiral_visual(t):
            r = 0.45 * np.exp(0.18 * t)
            return center + np.array([r * np.cos(t), r * np.sin(t), 0])

        espiral_visual = ParametricFunction(
            spiral_visual,
            t_range=[-8 * PI, 3 * PI],
            color=BLUE_C,
            stroke_width=3
        )

        self.play(Create(espiral_visual), run_time=4)
        
        eq_espiral = MathTex(r"r(\theta)=a e^\theta", font_size=42).to_edge(UP, buff=1.0)
        self.play(Write(eq_espiral))
        self.wait(1.5)

        # ============================================================
        # 3. ZOOM DE LA CÁMARA E INTERPOLACIÓN DE LA ECUACIÓN
        # ============================================================
        # CORRECCIÓN: El zoom va directamente al origen (center)
        zoom_point = center 

        self.play(
            self.camera.frame.animate.move_to(zoom_point).set(width=5.5),
            eq_espiral.animate.scale(24/42).move_to(zoom_point + UP * 1.3),
            run_time=2
        )
        self.wait(1)

        # ============================================================
        # 4. ESPIRAL MATEMÁTICA REAL
        # ============================================================
        a = 1.0
        def spiral_func(t):
            r = a * np.exp(t)
            return center + np.array([r * np.cos(t), r * np.sin(t), 0])

        espiral_math = ParametricFunction(
            spiral_func,
            t_range=[-10, 1.3], 
            color=BLUE_C,
            stroke_width=3 
        )

        self.play(FadeOut(espiral_visual), FadeIn(espiral_math), run_time=1.5)
        self.wait(0.5)

        # ============================================================
        # 5. PRIMER PUNTO (r0) Y SU LÍNEA
        # ============================================================
        t0 = -0.5
        t1 = t0 + 1.0
        
        p0 = spiral_func(t0)
        p1 = spiral_func(t1)

        dot0 = Dot(p0, color=YELLOW, radius=0.04) 
        label_r0 = MathTex(r"r_0", font_size=22, color=YELLOW).next_to(dot0, UR, buff=0.08)

        linea_r0 = Line(center, p0, color=YELLOW, stroke_width=3)

        self.play(FadeIn(dot0), Write(label_r0), Create(linea_r0))
        self.wait(1)

        # ============================================================
        # 6. SEGUNDO PUNTO SE MUEVE EXACTAMENTE 1 RADIÁN (r1)
        # ============================================================
        dot1 = Dot(p0, color=GREEN, radius=0.04)
        self.add(dot1)

        moving_path = ParametricFunction(
            spiral_func, 
            t_range=[t0, t1],
            stroke_width=0
        )

        self.play(MoveAlongPath(dot1, moving_path), run_time=2)
        self.wait(0.3)

        label_r1 = MathTex(r"r_1", font_size=22, color=GREEN).next_to(dot1, UL, buff=0.08)
        linea_r1 = Line(center, p1, color=GREEN, stroke_width=3)

        self.play(Write(label_r1), Create(linea_r1))
        self.wait(1)

        # ============================================================
        # 7. ARCO DEL ÁNGULO THETA = 1 RAD 
        # ============================================================
        arco_theta = Arc(
            radius=0.4, 
            start_angle=t0,
            angle=1.0,
            arc_center=center,
            color=WHITE,
            stroke_width=2
        )
        label_theta = MathTex(r"1\ \mathrm{rad}", font_size=18).next_to(arco_theta, UP, buff=0.05).shift(LEFT * 0.25)

        self.play(Create(arco_theta), Write(label_theta))
        self.wait(2.5)

        # ============================================================
        # 8. DESARROLLO MATEMÁTICO 
        # ============================================================
        pos_ecuaciones = zoom_point + DOWN * 1.0
        
        ratio = MathTex(r"\frac{r_1}{r_0}", font_size=32).move_to(pos_ecuaciones)
        self.play(Write(ratio))
        self.wait(1.5)

        ratio_exp1 = MathTex(r"\frac{a e^{\theta_1}}{a e^{\theta_0}}", font_size=32).move_to(pos_ecuaciones)
        self.play(TransformMatchingTex(ratio, ratio_exp1))
        self.wait(1)

        def_theta = MathTex(r"\theta_1 = \theta_0 + 1", font_size=24, color=LIGHT_GREY).next_to(ratio_exp1, RIGHT, buff=0.4)
        self.play(FadeIn(def_theta, shift=LEFT))
        self.wait(1.5)

        ratio_exp2 = MathTex(r"\frac{a e^{\theta_0+1}}{a e^{\theta_0}}", font_size=32).move_to(pos_ecuaciones)
        self.play(
            TransformMatchingTex(ratio_exp1, ratio_exp2),
            FadeOut(def_theta, shift=RIGHT)
        )
        self.wait(1)

        ratio_one = MathTex(r"e^1", font_size=32).move_to(pos_ecuaciones)
        self.play(TransformMatchingTex(ratio_exp2, ratio_one), run_time=1.2)
        self.wait(1.2)

        resultado_e = MathTex(r"e", font_size=42, color=YELLOW).move_to(pos_ecuaciones)
        self.play(TransformMatchingTex(ratio_one, resultado_e), run_time=1.2)
        self.wait(1.5)

        valor_e = MathTex(r"e \approx 2.71828\ldots", font_size=24, color=YELLOW).next_to(resultado_e, UP, buff=0.15)
        self.play(Write(valor_e), run_time=1.2)
        self.wait(3)

        # ============================================================
        # 9. OUTRO Y REGRESO DE CÁMARA
        # ============================================================
        self.play(
            FadeOut(
                VGroup(
                    espiral_math, linea_r0, linea_r1, dot0, dot1,
                    label_r0, label_r1, arco_theta, label_theta,
                    eq_espiral, resultado_e, valor_e,
                )
            )
        )

        self.play(self.camera.frame.animate.move_to(ORIGIN).set(width=14.22), run_time=1)

        marca = MathTex(r"F_{GC}", font_size=72, color=BLUE)
        canal = Text("@tensorfer", font_size=36, color=WHITE).next_to(marca, DOWN, buff=0.4)

        self.play(Write(marca))
        self.play(FadeIn(canal))
        self.wait(1.5)