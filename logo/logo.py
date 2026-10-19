from manim import *

class LogoAvatar(Scene):
    def construct(self):
        # Renderizar las iniciales con tipografía matemática
        texto_logo = MathTex(r"F_{GC}")
        
        # Escalar el texto para que llene bien el espacio del avatar
        texto_logo.scale(6)
        
        # Opcional: Agregar un círculo sutil para enmarcarlo
        marco = Circle(radius=3.5, color=WHITE, stroke_width=2)
        
        # Añadir a la escena
        self.add(marco, texto_logo)
