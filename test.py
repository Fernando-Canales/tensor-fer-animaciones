from manim import *

class Test(Scene):
    def construct(self):
        self.play(Write(MathTex(r"F_{GC}", color=BLUE)))
        self.wait()
