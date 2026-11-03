from manim import *
import numpy as np

# ---------------------------------------------------------------
# ESPIRAL DE TEODORO (sin título, sin voz): empieza directamente con dos catetos de longitud 1
# FORMATO: cuadro vertical 9:16 (1080x1920)
# Render: manim -qh --fps 60 theodorus_short.py TheodorusShort
# ---------------------------------------------------------------
PORTRAIT = True
if PORTRAIT:
    config.pixel_width = 1080
    config.pixel_height = 1920
    config.frame_width = 6.0
    config.frame_height = 6.0 * 16 / 9


# ===============================================================
# GEOMETRÍA (numpy puro; se puede probar sin Manim)
# ===============================================================
# BEGIN-GEOM
N_TRI = 16                 # 16 triángulos: la espiral llega a √17 y aún no se solapa consigo misma
FW_MIN = 3.2               # ancho del cuadro al empezar (el primer triángulo se ve grande)
FILL = 0.96                # fracción del cuadro que puede ocupar la figura (el margen de etiquetas ya va aparte)
LABEL_OFF = 0.32           # separación de la etiqueta (en unidades de pantalla)
UP_SHIFT = 0.02            # ligero desplazamiento hacia arriba (zona segura inferior)


def theodorus_points(n=N_TRI):
    """z[0] = O, z[1] = 1; cada nuevo punto está a distancia 1 del anterior y a 90° de la
    hipotenusa previa:  z[k+1] = z[k] + i·z[k]/|z[k]|   ->   |z[k]| = sqrt(k).
    El triángulo k tiene vértices O, z[k], z[k+1] (ángulo recto en z[k])."""
    z = [0j, 1 + 0j]
    for k in range(1, n + 1):
        z.append(z[k] + 1j * z[k] / abs(z[k]))
    return np.array(z)


def camera_target(z, k):
    """Ancho del cuadro y centro de cámara para ver todos los puntos hasta z[k+1] (más etiquetas)."""
    p = z[: k + 2]
    fw = FW_MIN
    for _ in range(4):                                   # punto fijo: el margen depende del ancho
        a = (LABEL_OFF + 0.25) * fw / 6.0
        x0, x1 = p.real.min() - a, p.real.max() + a
        y0, y1 = p.imag.min() - a, p.imag.max() + a
        fw = max(FW_MIN, (x1 - x0) / FILL, (y1 - y0) / (FILL * 16 / 9))
    fh = fw * 16 / 9
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2 - UP_SHIFT * fh
    return fw, complex(cx, cy)
# END-GEOM


# ===============================================================
# ESCENA
# ===============================================================
class TheodorusShort(MovingCameraScene):
    def construct(self):
        COLOR_LINE = WHITE
        COLOR_LOGO = BLUE_C
        PAL = color_gradient(["#58C4DD", "#78DCB4", "#F4D35E", "#F08A5D", "#C06C84"], N_TRI)

        z = theodorus_points()
        P = lambda k: np.array([z[k].real, z[k].imag, 0.0])
        cam = self.camera.frame

        def frame_scale():
            return cam.width / config.frame_width

        # cámara inicial: primer triángulo grande
        fw, c = camera_target(z, 1)
        cam.set(width=fw).move_to(np.array([c.real, c.imag, 0.0]))

        def make_label(tex, anchor, direction):
            """Etiqueta con tamaño constante en pantalla, a distancia constante del punto `anchor`."""
            lab = MathTex(tex, font_size=36, color=WHITE).set_z_index(6)
            h0 = lab.height
            d = np.array(direction, dtype=float)
            d = d / np.linalg.norm(d)

            def upd(m):
                s = frame_scale()
                m.set_height(h0 * s)
                m.move_to(anchor + d * LABEL_OFF * s)
            lab.add_updater(upd)
            upd(lab)
            return lab

        def right_angle(k):
            """Cuadradito del ángulo recto en z[k] (entre el cateto hacia O y el nuevo cateto)."""
            u = -P(k) / np.linalg.norm(P(k))                       # hacia O
            v = (P(k + 1) - P(k)) / np.linalg.norm(P(k + 1) - P(k))  # nuevo cateto
            m = 0.16
            return VMobject(color=WHITE, stroke_width=2).set_points_as_corners(
                [P(k) + m * u, P(k) + m * (u + v), P(k) + m * v]).set_z_index(3)

        def line(a, b, w=3.5):
            return Line(P(a), P(b), color=COLOR_LINE, stroke_width=w).set_z_index(2)

        def tri_poly(k):
            return Polygon(P(0), P(k), P(k + 1), fill_color=PAL[k - 1], fill_opacity=0.8,
                           stroke_width=0).set_z_index(0)

        polys, labels, ones = [], [], []

        # =============================================================
        # TRIÁNGULO 1: dos catetos de longitud 1 y la hipotenusa √2
        # =============================================================
        leg_a = line(0, 1)                 # O -> z1 (longitud 1)
        leg_b = line(1, 2)                 # z1 -> z2 (longitud 1), ángulo recto en z1
        hyp = line(0, 2)                   # hipotenusa √2
        la = make_label("1", (P(0) + P(1)) / 2, (0, -1, 0))
        lb = make_label("1", (P(1) + P(2)) / 2, (1, 0, 0))
        ones += [la, lb]
        self.play(Create(leg_a), FadeIn(la), run_time=0.9)
        self.play(Create(leg_b), FadeIn(lb), run_time=0.9)
        self.play(FadeIn(right_angle(1)), run_time=0.4)
        l2 = make_label(r"\sqrt{2}", P(2), P(2))
        polys.append(tri_poly(1))
        labels.append(l2)
        self.play(Create(hyp), FadeIn(l2), run_time=1.0)
        self.play(FadeIn(polys[0]), run_time=0.6)

        # =============================================================
        # TRIÁNGULOS 2..N: nuevo cateto de longitud 1, perpendicular a la hipotenusa anterior
        # =============================================================
        for k in range(2, N_TRI + 1):
            a = max(0.32, 0.95 - 0.07 * k)
            b = max(0.5, 1.15 - 0.07 * k)
            leg = line(k, k + 1)
            hyp = line(0, k + 1)
            poly = tri_poly(k)
            polys.append(poly)
            lab = make_label(r"\sqrt{%d}" % (k + 1), P(k + 1), P(k + 1))
            labels.append(lab)
            fw, c = camera_target(z, k)
            anims = [Create(hyp), FadeIn(poly), FadeIn(lab),
                     cam.animate.set(width=fw).move_to(np.array([c.real, c.imag, 0.0]))]
            if k == 3:
                anims += [FadeOut(la), FadeOut(lb)]     # los "1" iniciales ya cumplieron su función
            self.play(Create(leg), FadeIn(right_angle(k)), run_time=a)
            self.play(*anims, run_time=b)

        # =============================================================
        # REMATE: una ola de brillo recorre la espiral
        # =============================================================
        self.wait(0.4)
        self.play(LaggedStart(*[Indicate(p, scale_factor=1.12, color=WHITE) for p in polys],
                              lag_ratio=0.09), run_time=2.4)
        self.wait(0.8)

        # =============================================================
        # CIERRE Y LOGO
        # =============================================================
        for m in labels + ones:
            m.clear_updaters()
        self.play(FadeOut(Group(*self.mobjects)), run_time=1.0)
        cam.set(width=config.frame_width).move_to(ORIGIN)
        logo = MathTex(r"F_{GC}", font_size=150, color=COLOR_LOGO).move_to(ORIGIN)
        self.play(FadeIn(logo, scale=0.7), run_time=1.2)
        self.wait(2.5)