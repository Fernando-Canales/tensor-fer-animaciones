import numpy as np
from manim import *

# Configuración del formato vertical (9:16) para Shorts/TikTok
config.pixel_width = 1080
config.pixel_height = 1920
config.frame_width = 9.0
config.frame_height = 16.0


class AlgebraModular(Scene):

  def construct(self):
    # ==============================================================
    # ESCENA 1: Las 4 operaciones y la Operación Módulo
    # ==============================================================
    ops = MathTex(r"+", r"-", r"\times", r"\div", font_size=120)
    ops.arrange(RIGHT, buff=1.0).move_to(UP * 2)

    self.play(FadeIn(ops, shift=UP * 0.5, lag_ratio=0.3), run_time=2)
    self.wait(8)

    # Ahora incluye la palabra "mod"
    mod_sym = MathTex(r"\% \quad \text{mod}", font_size=180, color=YELLOW).move_to(DOWN * 1.5)
    self.play(Write(mod_sym), run_time=1.5)
    self.wait(1)

    self.play(FadeOut(ops), FadeOut(mod_sym))

    # ==============================================================
    # ESCENA 2: Definición y División en Galera
    # ==============================================================
    
    # Texto introductorio y expresión general
    def_title = Text("Módulo = Residuo de la división", font_size=40).move_to(UP * 3.8)
    general_eq = MathTex(r"a \pmod{b}", font_size=90, color=YELLOW).next_to(def_title, DOWN, buff=0.8)
    
    self.play(Write(def_title), run_time=1.2)
    self.play(Write(general_eq), run_time=1.2)
    self.wait(1.5)

    # Transición al ejemplo específico (15 mod 12)
    mod_eq = MathTex(r"15 \pmod{12}", font_size=90, color=YELLOW).move_to(UP * 3.5)
    
    self.play(
        FadeOut(def_title),
        ReplacementTransform(general_eq, mod_eq)
    )
    self.wait(0.5)

    # Inicia la división (relativa al dividendo)
    dividend = MathTex("15", font_size=90).move_to(UP * 1.0 + RIGHT * 0.5)
    divisor = MathTex("12", font_size=90).next_to(dividend, LEFT, buff=0.6)

    # Galera con dos líneas rectas (L-invertida)
    v_line = Line(
        divisor.get_right() + RIGHT * 0.2 + DOWN * 0.5,
        divisor.get_right() + RIGHT * 0.2 + UP * 0.6,
        stroke_width=5,
    )
    h_top = Line(
        v_line.get_top(),
        dividend.get_right() + RIGHT * 0.3 + UP * 0.6,
        stroke_width=5,
    )
    galera_symbol = VGroup(v_line, h_top)

    quotient = (
        MathTex("1", font_size=90)
        .next_to(h_top, UP, buff=0.2)
        .align_to(dividend[0][-1], RIGHT)
    )
    minus_12 = (
        MathTex("-12", font_size=90)
        .next_to(dividend, DOWN, buff=0.35)
        .align_to(dividend, RIGHT)
    )

    y_line = minus_12.get_bottom()[1] - 0.15
    line_left = np.array([minus_12.get_left()[0] - 0.2, y_line, 0])
    line_right = np.array([minus_12.get_right()[0] + 0.2, y_line, 0])
    h_line = Line(line_left, line_right, stroke_width=5)

    residuo = (
        MathTex("3", font_size=90)
        .next_to(h_line, DOWN, buff=0.3)
        .align_to(dividend[0][-1], RIGHT)
    )

    self.play(
        Write(divisor), Create(galera_symbol), Write(dividend), run_time=1.5
    )
    self.wait(1)
    self.play(Write(quotient), run_time=0.8)
    self.play(Write(minus_12), run_time=0.8)
    self.play(Create(h_line), Write(residuo), run_time=0.8)

    lbl_residuo = Text(
        "¡Este es el módulo!", font_size=36, color=YELLOW
    ).next_to(residuo, DOWN, buff=1.0)
    arrow = Arrow(
        lbl_residuo.get_top(),
        residuo.get_bottom() + DOWN * 0.15,
        color=YELLOW,
        stroke_width=6,
    )

    self.play(Write(lbl_residuo), GrowArrow(arrow))
    self.wait(3)

    # Limpiamos pantalla
    self.play(
        FadeOut(mod_eq), FadeOut(dividend), FadeOut(divisor), FadeOut(galera_symbol),
        FadeOut(quotient), FadeOut(minus_12), FadeOut(h_line),
        FadeOut(residuo), FadeOut(lbl_residuo), FadeOut(arrow),
    )
    self.wait(0.5)

    # ==============================================================
    # ESCENA 3: Aplicaciones y Formato de 24 horas
    # ==============================================================
    app1 = Text("Criptografía", font_size=45).move_to(UP * 3.5)
    app2 = Text("Formas modulares", font_size=45).move_to(UP * 1.5)
    app3 = Text("Números primos", font_size=45).move_to(DOWN * 0.5)

    self.play(
        FadeIn(app1, shift=UP), FadeIn(app2, shift=UP), FadeIn(app3, shift=UP),
        lag_ratio=0.3,
    )
    self.wait(1)

    conv = Text(
        "24 hr  ➔  12 hr", font_size=65, color=YELLOW, weight=BOLD
    ).move_to(DOWN * 3)
    self.play(Write(conv))
    self.wait(2)

    self.play(FadeOut(app1), FadeOut(app2), FadeOut(app3), FadeOut(conv))

    # ==============================================================
    # ESCENA 4: Recta Numérica a Reloj
    # ==============================================================
    line = NumberLine(
        x_range=[1, 12, 1], length=7.5, color=BLUE, include_numbers=False
    ).move_to(UP * 3.5)

    nums = VGroup()
    for i in range(1, 13):
      n = MathTex(str(i), font_size=36).next_to(line.n2p(i), UP, buff=0.3)
      nums.add(n)

    self.play(Create(line), FadeIn(nums), run_time=1.5)
    self.wait(1)

    clock_center = UP * 2.2
    radius = 2.1
    clock_circle = Circle(radius=radius, color=BLUE_B, stroke_width=6).move_to(
        clock_center
    )

    target_nums = VGroup()
    for i in range(1, 13):
      angle = PI / 2 - (i * TAU / 12)
      pos = clock_center + np.array(
          [np.cos(angle), np.sin(angle), 0]
      ) * (radius + 0.45)
      n_target = MathTex(str(i), font_size=42).move_to(pos)
      target_nums.add(n_target)

    self.play(
        ReplacementTransform(line, clock_circle),
        ReplacementTransform(nums, target_nums),
        run_time=2,
    )

    # ==============================================================
    # ESCENA 5: La Manecilla Dando la Vuelta Inicial
    # ==============================================================
    hand = Line(
        clock_center,
        clock_center + UP * (radius - 0.35),
        color=YELLOW,
        stroke_width=8,
    )
    center_dot = Dot(clock_center, radius=0.15, color=YELLOW)
    self.play(FadeIn(hand, center_dot))

    # Da la vuelta entera
    self.play(
        Rotate(
            hand,
            angle=-TAU,
            about_point=clock_center,
            run_time=6.0,
            rate_func=linear,
        )
    )
    
    # Se queda 2 segundos en el 12
    self.wait(2.0)

    # ==============================================================
    # ESCENA 6: Colocar números 13 al 24 con ritmo dinámico
    # ==============================================================
    extra_nums = VGroup()
    for i in range(13, 25):
      idx = i % 12
      if idx == 0:
        idx = 12

      angle = PI / 2 - (idx * TAU / 12)
      outer_pos = clock_center + np.array(
          [np.cos(angle), np.sin(angle), 0]
      ) * (radius + 1.0)
      extra_num = MathTex(str(i), font_size=38, color=ORANGE).move_to(outer_pos)
      extra_nums.add(extra_num)

      if i <= 15:
        self.play(
            Rotate(
                hand,
                angle=-TAU / 12,
                about_point=clock_center,
                run_time=0.5,
                rate_func=smooth,
            )
        )
        self.play(FadeIn(extra_num, shift=UP * 0.05), run_time=0.5)
        self.wait(1.0)
      else:
        self.play(
            Rotate(
                hand,
                angle=-TAU / 12,
                about_point=clock_center,
                run_time=0.35,
                rate_func=linear,
            ),
            FadeIn(extra_num, shift=UP * 0.05, run_time=0.35),
        )

    self.wait(1)

    # ==============================================================
    # ESCENA 7: Aparición posterior de Ecuaciones y Conclusión
    # ==============================================================
    eq_list = [
        MathTex(rf"{num} \pmod{{12}} = \mathbf{{{num % 12}}}", font_size=42)
        for num in [13, 14, 15]
    ]
    eq_list.append(MathTex(r"\vdots", font_size=42))
    
    eqs = VGroup(*eq_list).arrange(DOWN, buff=0.35).move_to(DOWN * 2.8)

    self.play(Write(eqs), run_time=2.5)
    self.wait(1)

    conclusion = Paragraph(
        "Esta es la razón por la cual",
        "las 15:00 son las 3:00 PM",
        alignment="center",
        font_size=30,
        color=YELLOW,
    ).next_to(eqs, DOWN, buff=0.5)

    self.play(Write(conclusion))
    self.wait(4)

    # ==============================================================
    # ESCENA 8: Cortinilla Final (Logo)
    # ==============================================================
    self.play(
        *[FadeOut(mob) for mob in self.mobjects]
    )
    self.wait(0.5)
    
    logo = MathTex(r"F_{GC}", font_size=180, color=WHITE)
    self.play(Write(logo), run_time=1.5)
    self.wait(2.5)
    self.play(FadeOut(logo))
    self.wait(1)