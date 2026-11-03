from manim import *
import numpy as np

# ---------------------------------------------------------------
# ESPIRAL DE TEODORO (sin voz): empieza directamente con dos catetos de longitud 1,
# la espiral sigue creciendo (y la cámara se aleja) para sugerir que no termina nunca,
# aparece el título y, al final, el logo.
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
# GEOMETRÍA Y TIEMPOS (numpy puro; se puede probar sin Manim)
# ===============================================================
# BEGIN-GEOM
N_TRI = 16                 # los 16 primeros triángulos (hasta √17) se construyen despacio y con etiquetas
N_END = 100                # la espiral sigue hasta el triángulo 100 (cada vez más rápido)
SLOW = 1.6                 # factor de lentitud de los primeros 16 pasos (tiempo para hablar)
FW_MIN = 3.2               # ancho del cuadro al empezar (el primer triángulo se ve grande)
FILL = 0.96                # fracción del cuadro que puede ocupar la figura (el margen de etiquetas va aparte)
LABEL_OFF = 0.32           # separación de la etiqueta (en unidades de pantalla)
UP_SHIFT = 0.02            # ligero desplazamiento hacia arriba (zona segura inferior)


# Triángulo 1: velocidad de dibujo normal (la hipotenusa √2 puede tardar un poco)
T1 = dict(leg_a=1.4, leg_b=1.4, ang=0.7, hyp=1.6, fill=1.0)
# Pausa (s) DESPUÉS de formarse cada uno de los tres primeros triángulos: tiempo para explicar
# lo que se acaba de construir antes de que empiece el siguiente
PAUSE = {1: 6.0, 2: 5.0, 3: 5.0}


def theodorus_points(n=N_END):
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


def step_times(k):
    """Tiempos (nuevo cateto, hipotenusa+relleno+cámara) del triángulo k = 2..16."""
    return SLOW * max(0.32, 0.95 - 0.07 * k), SLOW * max(0.5, 1.15 - 0.07 * k)


def tail_time(k):
    """Duración del paso k > 16: empieza a 0.5 s y se acelera hasta 0.04 s (≈ 2-3 fotogramas)."""
    return max(0.04, 0.5 * 0.93 ** (k - 17))


def color_index(k, n=N_TRI):
    """Índice de color del triángulo k: recorre la paleta de ida y vuelta (sin saltos)."""
    period = 2 * (n - 1)
    j = (k - 1) % period
    return j if j < n else period - j
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
            if k <= N_TRI:
                op, zi = 0.8, 0
            else:                                   # los triángulos de la 2.ª vuelta quedan DETRÁS de los anteriores
                op, zi = 0.7, -(k - N_TRI)
            return Polygon(P(0), P(k), P(k + 1), fill_color=PAL[color_index(k)], fill_opacity=op,
                           stroke_width=0).set_z_index(zi)

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
        self.play(Create(leg_a), FadeIn(la), run_time=T1["leg_a"])
        self.play(Create(leg_b), FadeIn(lb), run_time=T1["leg_b"])
        self.play(FadeIn(right_angle(1)), run_time=T1["ang"])
        l2 = make_label(r"\sqrt{2}", P(2), P(2))
        polys.append(tri_poly(1))
        labels.append(l2)
        self.play(Create(hyp), FadeIn(l2), run_time=T1["hyp"])
        self.play(FadeIn(polys[0]), run_time=T1["fill"])
        self.wait(PAUSE[1])                                   # pausa larga antes del triángulo 2

        # =============================================================
        # TRIÁNGULOS 2..16: nuevo cateto de longitud 1, perpendicular a la hipotenusa anterior (lento)
        # =============================================================
        for k in range(2, N_TRI + 1):
            a, b = step_times(k)
            leg = line(k, k + 1)
            hyp = line(0, k + 1)
            poly = tri_poly(k)
            polys.append(poly)
            lab = make_label(r"\sqrt{%d}" % (k + 1), P(k + 1), P(k + 1))
            labels.append(lab)
            fw, c = camera_target(z, k)
            cam_move = cam.animate.set(width=fw).move_to(np.array([c.real, c.imag, 0.0]))
            anims = [Create(hyp), FadeIn(poly), FadeIn(lab), cam_move]
            if k == 3:
                anims += [FadeOut(m) for m in ones]         # los "1" iniciales ya cumplieron su función
            self.play(Create(leg), FadeIn(right_angle(k)), run_time=a)
            self.play(*anims, run_time=b)
            if k in PAUSE:                                  # triángulos 2 y 3: pausa larga para explicar
                self.wait(PAUSE[k])
        self.wait(0.8)

        # =============================================================
        # LA ESPIRAL SIGUE... Y SIGUE: pasos cada vez más rápidos, la cámara se aleja sin parar
        # =============================================================
        for k in range(N_TRI + 1, N_END + 1):
            rt = tail_time(k)
            w = 1.8 if k <= 50 else 1.1
            leg, hyp, poly = line(k, k + 1, w), line(0, k + 1, w), tri_poly(k)
            polys.append(poly)
            fw, c = camera_target(z, k)
            anims = [Create(leg), Create(hyp), FadeIn(poly),
                     cam.animate.set(width=fw).move_to(np.array([c.real, c.imag, 0.0]))]
            i0 = 2 * (k - N_TRI - 1)                    # las etiquetas se van apagando de dos en dos
            if i0 < len(labels):
                anims += [FadeOut(m) for m in labels[i0:i0 + 2]]
            self.play(*anims, run_time=rt, rate_func=linear)
        self.wait(0.6)

        # =============================================================
        # TÍTULO (tamaño y posición fijos en pantalla, aunque la cámara esté muy alejada)
        # =============================================================
        title = Text("Espiral de\nTeodoro", font_size=64, line_spacing=0.9, color=WHITE).set_z_index(20)
        t_h0 = title.height

        def title_upd(m):
            s = frame_scale()
            m.set_height(t_h0 * s)
            m.move_to(cam.get_center() + np.array([0.0, 3.95 * s, 0.0]))
        title.add_updater(title_upd)
        title_upd(title)
        self.play(FadeIn(title, shift=0.3 * UP), run_time=1.5)
        self.wait(3.5)

        # =============================================================
        # CIERRE Y LOGO
        # =============================================================
        title.clear_updaters()
        for m in labels + ones:
            m.clear_updaters()
        self.play(FadeOut(Group(*self.mobjects)), run_time=1.2)
        cam.set(width=config.frame_width).move_to(ORIGIN)
        logo = MathTex(r"F_{GC}", font_size=150, color=COLOR_LOGO).move_to(ORIGIN)
        self.play(FadeIn(logo, scale=0.7), run_time=1.2)
        self.wait(2.5)