from manim import *

class BannerCanal(Scene):
    def construct(self):
        # Bajamos la curva de luz para que su línea base no cruce el texto
        curva_transito = FunctionGraph(
            lambda x: -1.0 * np.exp(-(x**2/2)),
            color=BLUE,
            x_range=[-8, 8],
            stroke_width=3
        ).shift(DOWN * 0.2)
        
        # Subimos el título principal para abrir espacio
        titulo = Tex(r"\textbf{@tensor-fer}", font_size=75).shift(UP * 0.5)
        
        # El subtítulo ahora descansa en la franja vacía entre el título y la curva
        subtitulo = Tex(r"Astrofísica $\cdot$ Datos $\cdot$ Matemáticas", font_size=36, color=LIGHT_GREY).next_to(titulo, DOWN, buff=0.16)
        
        # Firma discreta en la esquina
        firma = MathTex(r"F_{GC}", font_size=24, color=DARK_GRAY).to_corner(DR)
        
        self.add(curva_transito, titulo, subtitulo, firma)
