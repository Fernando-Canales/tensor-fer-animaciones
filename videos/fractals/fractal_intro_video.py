from manim import *
import numpy as np

# ---------------------------------------------------------------
# ¿QUÉ ES UN FRACTAL?  (vídeo horizontal 16:9, 1920x1080, 60 fps, con voz)
# Render: manim -qh --fps 60 fractal_intro_video.py FractalIntroVideo
# Al terminar el render, la consola imprime los instantes de cada sección (para ajustar el guion).
# Secciones: A) título   B) intuición (Koch y círculo)   C) ideas sin definición única
#            D) ejemplos (dragón, helecho, Newton, Mandelbrot)   E) lista de reproducción
# ---------------------------------------------------------------
config.pixel_width = 1920
config.pixel_height = 1080
config.frame_height = 8.0
config.frame_width = 8.0 * 16 / 9


# ===============================================================
# MATEMÁTICAS Y DISPOSICIÓN (numpy puro; se puede probar sin Manim)
# ===============================================================
# BEGIN-GEOM
# ---- Paleta ----
C_BLUE, C_GOLD, C_MINT, C_ROSE, C_ORANGE = "#58C4DD", "#F4D35E", "#78DCB4", "#C06C84", "#F08A5D"

# ---- Curva y copo de Koch ----
def koch_curve(n):
    """Curva de Koch de nivel n entre 0 y 1 (puntos complejos). El bulto queda a la izquierda."""
    pts = np.array([0j, 1 + 0j])
    for _ in range(n):
        a, b = pts[:-1], pts[1:]
        d = (b - a) / 3
        p1, p3 = a + d, a + 2 * d
        p2 = p1 + d * np.exp(1j * np.pi / 3)
        new = np.empty(4 * len(a) + 1, dtype=complex)
        new[0:-1:4], new[1::4], new[2::4], new[3::4] = a, p1, p2, p3
        new[-1] = pts[-1]
        pts = new
    return pts


def koch_flake(n):
    """Copo de Koch: tres curvas sobre un triángulo recorrido en sentido horario (bultos hacia fuera)."""
    h = np.sqrt(3) / 2
    V = [0.5 + 1j * h, 1.0 + 0j, 0j]                 # arriba, abajo-derecha, abajo-izquierda (horario)
    curve = koch_curve(n)
    parts = []
    for i in range(3):
        a, b = V[i], V[(i + 1) % 3]
        parts.append(a + curve[:-1] * (b - a))
    parts.append(np.array([V[0]]))
    return np.concatenate(parts)


# ---- Triángulo de Sierpinski ----
def sierpinski_tris(A, B, C, n):
    """Lista de 3^n triángulos (a, b, c). Los 3^(n-1) primeros son los descendientes del hijo 0, etc."""
    tris = [(A, B, C)]
    for _ in range(n):
        new = []
        for (a, b, c) in tris:
            ab, ac, bc = (a + b) / 2, (a + c) / 2, (b + c) / 2
            new += [(a, ab, ac), (ab, b, bc), (ac, bc, c)]
        tris = new
    return tris


# ---- Curva del dragón (Heighway) ----
def dragon_points(n):
    """Se copia la curva, se gira 90° alrededor del extremo y se añade (al revés). 2^n segmentos."""
    z = np.array([0j, 1 + 0j])
    for _ in range(n):
        end = z[-1]
        z = np.concatenate([z, end + 1j * (z[::-1][1:] - end)])
    return z


# ---- Curva de Hilbert ----
def hilbert_points(order):
    n = 2 ** order
    out = np.empty((n * n, 2))
    for d in range(n * n):
        t, x, y, s = d, 0, 0, 1
        while s < n:
            rx = 1 & (t // 2)
            ry = 1 & (t ^ rx)
            if ry == 0:
                if rx == 1:
                    x, y = s - 1 - x, s - 1 - y
                x, y = y, x
            x += s * rx
            y += s * ry
            t //= 4
            s *= 2
        out[d] = (x, y)
    return (out[:, 0] + 1j * out[:, 1]) / (n - 1)


# ---- Helecho de Barnsley (IFS con 4 transformaciones afines) ----
IFS_A = np.array([
    [[0.00, 0.00], [0.00, 0.16]],       # f1: tallo
    [[0.85, 0.04], [-0.04, 0.85]],      # f2: hoja principal
    [[0.20, -0.26], [0.23, 0.22]],      # f3: hoja izquierda
    [[-0.15, 0.28], [0.26, 0.24]],      # f4: hoja derecha
])
IFS_B = np.array([[0.0, 0.0], [0.0, 1.6], [0.0, 1.6], [0.0, 0.44]])
IFS_P = np.array([0.01, 0.85, 0.07, 0.07])


def chaos_game(n, rng):
    """Juego del caos: n+1 puntos del helecho (el origen ya pertenece a él)."""
    idx = rng.choice(4, size=n, p=IFS_P)
    pts = np.zeros((n + 1, 2))
    for k in range(n):
        j = idx[k]
        pts[k + 1] = IFS_A[j] @ pts[k] + IFS_B[j]
    return pts


def fern_raster(pts, nx=220, ny=220):
    """Miniatura del helecho: imagen RGB con la densidad de puntos."""
    x, y = pts[:, 0], pts[:, 1]
    H, _, _ = np.histogram2d(y, x, bins=[ny, nx], range=[[0, 10.2], [-3.0, 3.0]])
    H = np.flipud(H)
    v = np.clip(np.log1p(H) / np.log1p(H.max()), 0, 1)
    rgb = np.zeros((ny, nx, 3))
    rgb[..., 0] = 40 + 90 * v
    rgb[..., 1] = 90 + 150 * v
    rgb[..., 2] = 50 + 60 * v
    rgb[H == 0] = 0
    return rgb


# ---- Newton para z^3 - 1 ----
ROOTS = np.exp(2j * np.pi * np.arange(3) / 3)
NEWTON_RGB = np.array([[88, 196, 221], [244, 211, 94], [192, 108, 132]], dtype=float)


def newton_image(cx, cy, hx, nx, ny, maxit=40):
    """Cada píxel (un punto z0 del plano) se pinta del color de la raíz de z^3-1 a la que llega el
    método de Newton; más oscuro cuanto más tarda en llegar."""
    hy = hx * ny / nx
    xs = cx - hx + (np.arange(nx) + 0.5) * (2 * hx / nx)
    ys = cy + hy - (np.arange(ny) + 0.5) * (2 * hy / ny)
    z = xs[None, :] + 1j * ys[:, None]
    conv = np.full(z.shape, maxit, dtype=float)
    done = np.zeros(z.shape, dtype=bool)
    with np.errstate(all="ignore"):
        for k in range(maxit):
            z = z - (z ** 3 - 1) / (3 * z ** 2)
            d = np.min(np.abs(z[..., None] - ROOTS[None, None, :]), axis=-1)
            new = (~done) & (d < 1e-3)
            conv[new] = k + 1
            done |= new
    z = np.nan_to_num(z)
    root = np.argmin(np.abs(z[..., None] - ROOTS[None, None, :]), axis=-1)
    shade = np.clip(1.0 - 0.035 * conv, 0.2, 1.0)
    rgb = NEWTON_RGB[root] * shade[..., None]
    rgb[~done] = 15.0
    return rgb


# ---- Mandelbrot ----
PAL_POS = np.array([0.0, 0.25, 0.5, 0.75, 1.0])
PAL_RGB = np.array([[22, 34, 110], [88, 196, 221], [120, 220, 180], [252, 214, 98], [22, 34, 110]], dtype=float)
M_CEN, M_HW0, M_TARGET, M_ZOOM = -0.6, 2.2, -1.7549, 45.0


def mandelbrot_mu(cx, cy, hx, nx, ny, maxit=100, R=16.0):
    """Tiempo de escape suavizado de z -> z^2 + c (ventana de semiancho hx y proporción nx:ny).
    Devuelve -1 dentro del conjunto (no escapa en maxit pasos)."""
    hy = hx * ny / nx
    xs = cx - hx + (np.arange(nx) + 0.5) * (2 * hx / nx)
    ys = cy + hy - (np.arange(ny) + 0.5) * (2 * hy / ny)
    c = (xs[None, :] + 1j * ys[:, None]).ravel()
    z = np.zeros_like(c)
    idx = np.arange(c.size)
    res = np.full(c.size, -1.0)
    for n in range(maxit):
        z = z * z + c
        mag2 = z.real ** 2 + z.imag ** 2
        esc = mag2 > R * R
        if esc.any():
            m = n + 1 - np.log(np.log(np.sqrt(mag2[esc]))) / np.log(2.0)
            res[idx[esc]] = np.maximum(m, 0.0)
            keep = ~esc
            z, c, idx = z[keep], c[keep], idx[keep]
            if z.size == 0:
                break
    return res.reshape(ny, nx)


def mandel_colorize(mu, period=24.0):
    t = (mu / period) % 1.0
    rgb = np.stack([np.interp(t, PAL_POS, PAL_RGB[:, k]) for k in range(3)], axis=-1)
    rgb[mu < 0] = 0.0
    return rgb


def mandel_view(u):
    """Cámara del zoom (u de 0 a 1): el semiancho baja por un factor M_ZOOM y el centro llega
    exactamente al objetivo en u = 1 (la copia pequeña del conjunto queda centrada)."""
    hw = M_HW0 * (1.0 / M_ZOOM) ** u
    hw1 = M_HW0 / M_ZOOM
    cx = M_TARGET + (M_CEN - M_TARGET) * (hw - hw1) / (M_HW0 - hw1)
    return cx, 0.0, hw


def mandel_maxit(hw):
    return int(100 + 40 * np.log2(M_HW0 / hw))


# ---- Utilidades de encaje y de imagen ----
def make_fit(zref, cx, cy, w, h):
    """Devuelve f(z) -> puntos Nx3 que encajan `zref` en una caja w x h centrada en (cx, cy) (misma escala para todo)."""
    zref = np.asarray(zref)
    x0, x1, y0, y1 = zref.real.min(), zref.real.max(), zref.imag.min(), zref.imag.max()
    s = min(w / (x1 - x0) if x1 > x0 else np.inf, h / (y1 - y0) if y1 > y0 else np.inf)
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2

    def f(z):
        z = np.asarray(z)
        return np.column_stack([cx + (z.real - mx) * s, cy + (z.imag - my) * s, np.zeros(z.shape)])
    f.scale = s
    return f


def upsample(rgb, nx, ny):
    """Bloques nítidos: repite cada celda hasta nx x ny píxeles."""
    r = (np.arange(ny) * rgb.shape[0]) // ny
    c = (np.arange(nx) * rgb.shape[1]) // nx
    return rgb[r][:, c]


def circle_zoom_points(k, R=2.2, win=2.2, n=240):
    """Círculo de radio R visto con aumento k alrededor de su punto más a la derecha
    (ventana cuadrada de lado 2*win): se aplana hasta parecer una recta."""
    phi_m = np.arcsin(min(1.0, win / (k * R)))
    phi = np.linspace(-phi_m, phi_m, n)
    return k * R * (np.cos(phi) - 1.0), k * R * np.sin(phi)
# END-GEOM


# ===============================================================
# ESCENA
# ===============================================================
class FractalIntroVideo(Scene):
    def construct(self):
        clock = [0.0]
        marks = []

        def play(*anims, run_time=1.0, **kw):
            self.play(*anims, run_time=run_time, **kw)
            clock[0] += run_time

        def wait(s):
            self.wait(s)
            clock[0] += s

        def mark(name):
            marks.append((name, clock[0]))

        def fit_text(m, maxw=13.0):
            if m.width > maxw:
                m.scale_to_fit_width(maxw)
            return m

        def poly(pts3, color, w=4, fill=None):
            vm = VMobject(color=color, stroke_width=w)
            vm.set_points_as_corners(pts3)
            if fill is not None:
                vm.set_fill(color, opacity=fill)
            return vm

        def tri_polys(tris, f, color, opacity=0.9):
            g = VGroup()
            for (a, b, c) in tris:
                g.add(Polygon(*[f(np.array([v]))[0] for v in (a, b, c)], fill_color=color, fill_opacity=opacity,
                              stroke_width=0))
            return g

        def to_img(rgb, w, h, center, nx, ny):
            m = ImageMobject(np.clip(upsample(rgb, nx, ny), 0, 255).astype(np.uint8))
            m.stretch_to_fit_width(w)
            m.stretch_to_fit_height(h)
            m.move_to(np.array([center[0], center[1], 0.0]))
            return m

        def header(txt, y=3.45, size=50, color=WHITE):
            return fit_text(Text(txt, font_size=size, color=color)).move_to(np.array([0, y, 0]))

        cover = Rectangle(width=config.frame_width + 0.4, height=config.frame_height + 0.4, fill_color=BLACK,
                          fill_opacity=1, stroke_width=0).set_z_index(100)

        def fade_to_black():
            play(FadeIn(cover), run_time=0.8)
            self.clear()
            clock[0] += 0.0

        # =============================================================
        # A. TÍTULO: ¿Qué es un fractal?  (copo de Koch creciendo)
        # =============================================================
        mark("A. Título")
        title = Text("¿Qué es un fractal?", font_size=88, weight=BOLD, color=WHITE).move_to(np.array([0, 2.75, 0]))
        flake_fit = make_fit(koch_flake(4), 0.0, -1.05, 5.0, 4.3)
        play(Write(title), run_time=1.6)
        flake = poly(flake_fit(koch_flake(0)), C_BLUE, 5, fill=0.18)
        play(Create(flake), run_time=1.2)
        for n in range(1, 5):
            nxt = poly(flake_fit(koch_flake(n)), C_BLUE, 5 if n < 4 else 3.5, fill=0.18)
            play(ReplacementTransform(flake, nxt), run_time=1.4)
            flake = nxt
        wait(2.0)
        play(FadeOut(Group(title, flake)), run_time=0.8)

        # =============================================================
        # B1. INTUICIÓN: una parte se parece al todo (curva de Koch)
        # =============================================================
        mark("B1. Una parte se parece al todo")
        hdr = header("Si te acercas, ves lo mismo")
        L, X0, Y0 = 10.0, -5.0, -1.4                       # largo de la curva y su extremo izquierdo
        K = lambda n: np.column_stack([X0 + L * koch_curve(n).real, Y0 + L * koch_curve(n).imag, np.zeros(4 ** n + 1)])
        left_end = np.array([X0, Y0, 0.0])
        play(FadeIn(hdr), run_time=0.8)
        whole = poly(K(5), C_BLUE, 3.5)
        play(Create(whole), run_time=3.5, rate_func=linear)
        wait(1.5)
        piece1 = poly(K(5)[: 4 ** 4 + 1], C_GOLD, 6)        # primer tercio: es una curva de Koch más pequeña
        play(FadeIn(piece1), whole.animate.set_stroke(opacity=0.35), run_time=1.0)
        wait(1.5)
        play(piece1.animate.scale(3, about_point=left_end), run_time=2.4)
        wait(2.0)
        play(FadeOut(piece1), whole.animate.set_stroke(opacity=1.0), run_time=0.8)
        piece2 = poly(K(4)[: 4 ** 3 + 1], C_ROSE, 6)
        play(FadeIn(piece2), run_time=0.8)
        wait(1.0)
        play(piece2.animate.scale(3, about_point=left_end), run_time=2.4)
        wait(2.0)
        play(FadeOut(Group(hdr, whole, piece2)), run_time=0.8)

        # =============================================================
        # B2. EN CAMBIO, UN CÍRCULO SE VUELVE UNA RECTA
        # =============================================================
        mark("B2. El círculo")
        hdr = header("Un círculo, en cambio…")
        R, win = 2.2, 2.2
        c_left = np.array([-3.6, -0.2, 0.0])
        c_right = np.array([3.9, -0.2, 0.0])
        circle = Circle(radius=R, color=C_BLUE, stroke_width=5).move_to(c_left)
        tangent_pt = c_left + np.array([R, 0, 0])
        panel = Square(side_length=2 * win, color=GREY_B, stroke_width=2.5).move_to(c_right)
        tr = ValueTracker(0.0)                              # u de 0 a 1; el aumento es k = 40^u
        kk = lambda: 40.0 ** tr.get_value()

        def zoom_rect():
            s = 2 * win / kk()
            return Rectangle(width=s, height=s, color=C_GOLD, stroke_width=4).move_to(tangent_pt)

        def zoom_arc():
            x, y = circle_zoom_points(kk(), R, win)
            pts = np.column_stack([c_right[0] + x, c_right[1] + y, np.zeros_like(x)])
            return poly(pts, C_BLUE, 5)

        def zoom_label():
            return Text("×%d" % round(kk()), font_size=46, color=C_GOLD).move_to(c_right + np.array([0, -2.75, 0]))

        play(FadeIn(hdr), Create(circle), run_time=1.5)
        rect, arc, lab = always_redraw(zoom_rect), always_redraw(zoom_arc), always_redraw(zoom_label)
        play(Create(panel), FadeIn(rect), FadeIn(arc), FadeIn(lab), run_time=1.0)
        wait(1.0)
        play(tr.animate.set_value(1.0), run_time=9.0, rate_func=smooth)
        end_txt = Text("…se vuelve una recta", font_size=46, color=WHITE).move_to(np.array([0, -3.45, 0]))
        play(FadeIn(end_txt), run_time=1.0)
        wait(2.5)
        for m in (rect, arc, lab):
            m.clear_updaters()
        play(FadeOut(Group(*self.mobjects)), run_time=0.8)

        # =============================================================
        # C0. NO HAY UNA DEFINICIÓN ÚNICA
        # =============================================================
        mark("C0. No hay definición única")
        card = VGroup(Text("No existe una definición única…", font_size=56, color=WHITE),
                      Text("pero sí ideas que se repiten", font_size=56, color=C_GOLD)).arrange(DOWN, buff=0.5)
        fit_text(card, 12.5)
        play(FadeIn(card, shift=0.2 * UP), run_time=1.4)
        wait(4.0)
        play(FadeOut(card), run_time=0.8)

        # =============================================================
        # C1. IDEA 1: se parece a sí mismo (Sierpinski)
        # =============================================================
        mark("C1. Autosemejanza")
        hdr = header("1 · Se parece a sí mismo", color=C_BLUE)
        S = 6.0
        A = np.array([-S / 2, -3.3, 0.0])
        B, C = A + np.array([S, 0, 0]), A + np.array([S / 2, S * np.sqrt(3) / 2, 0])
        zA, zB, zC = complex(A[0], A[1]), complex(B[0], B[1]), complex(C[0], C[1])
        tris = sierpinski_tris(zA, zB, zC, 5)
        third = len(tris) // 3
        ident = lambda z: np.column_stack([np.real(z), np.imag(z), np.zeros(np.shape(z))])
        groups = [tri_polys(tris[i * third:(i + 1) * third], ident, WHITE, 0.9) for i in range(3)]
        sier = VGroup(*groups)
        play(FadeIn(hdr), FadeIn(sier), run_time=1.5)
        wait(1.5)
        play(LaggedStart(groups[0].animate.set_fill(C_BLUE, 0.95), groups[1].animate.set_fill(C_GOLD, 0.95),
                         groups[2].animate.set_fill(C_MINT, 0.95), lag_ratio=0.6), run_time=2.4)
        wait(1.5)
        play(groups[0].animate.scale(2, about_point=A), run_time=2.4)     # la copia azul, ×2, es el todo
        wait(2.0)
        play(groups[0].animate.scale(0.5, about_point=A), run_time=1.4)
        wait(0.6)
        play(FadeOut(Group(hdr, sier)), run_time=0.8)

        # =============================================================
        # C2. IDEA 2: nace de una regla simple, repetida
        # =============================================================
        mark("C2. Regla simple repetida")
        hdr = header("2 · Nace de una regla simple, repetida", color=C_GOLD)
        play(FadeIn(hdr), run_time=0.8)
        lvl = tri_polys(sierpinski_tris(zA, zB, zC, 0), ident, C_GOLD, 0.95)
        play(FadeIn(lvl), run_time=1.0)
        wait(1.0)
        for n in range(1, 6):
            nxt = tri_polys(sierpinski_tris(zA, zB, zC, n), ident, C_GOLD, 0.95)
            play(FadeTransform(lvl, nxt), run_time=1.2)
            lvl = nxt
            wait(1.3)
        wait(1.5)
        play(FadeOut(Group(hdr, lvl)), run_time=0.8)

        # =============================================================
        # C3. IDEA 3: su dimensión no es un número entero
        # =============================================================
        mark("C3. Dimensión")
        hdr = header("3 · Su dimensión no es un número entero", color=C_MINT, size=46)
        q = Text("Reduce a la mitad: ¿cuántas copias hacen falta para reconstruirlo?", font_size=34, color=GREY_A)
        q = fit_text(q, 13.0).move_to(np.array([0, 2.65, 0]))
        play(FadeIn(hdr), run_time=0.8)
        play(FadeIn(q), run_time=0.8)
        cy = 0.35
        # --- segmento (2 mitades) ---
        seg_a = Line(np.array([-6.2, cy, 0]), np.array([-4.6, cy, 0]), color=WHITE, stroke_width=8)
        seg_b = Line(np.array([-4.6, cy, 0]), np.array([-3.0, cy, 0]), color=WHITE, stroke_width=8)
        # --- cuadrado (4 cuadrados de lado mitad) ---
        sq = [Square(side_length=1.5, color=WHITE, stroke_width=4, fill_color=WHITE, fill_opacity=0.25)
              .move_to(np.array([dx * 0.75, cy + dy * 0.75, 0])) for dx, dy in ((-1, 1), (1, 1), (-1, -1), (1, -1))]
        # --- Sierpinski (3 copias de lado mitad) ---
        SS = 3.4
        sA = complex(3.0, cy - 1.45)
        sB, sC = sA + SS, sA + SS / 2 + 1j * SS * np.sqrt(3) / 2
        s_tris = sierpinski_tris(sA, sB, sC, 4)
        s_third = len(s_tris) // 3
        s_groups = [tri_polys(s_tris[i * s_third:(i + 1) * s_third], ident, WHITE, 0.9) for i in range(3)]
        play(FadeIn(Group(seg_a, seg_b, *sq, *s_groups)), run_time=1.4)
        wait(1.0)

        def count_and_formula(x, n_txt, tex, color):
            t1 = Text(n_txt, font_size=44, color=color).move_to(np.array([x, -2.2, 0]))
            t2 = MathTex(tex, font_size=60, color=color).move_to(np.array([x, -3.2, 0]))
            return t1, t2

        # segmento: 2 copias
        t1, t2 = count_and_formula(-4.6, "2 copias", r"2^{1}=2", C_BLUE)
        play(seg_a.animate.set_color(C_BLUE).shift(LEFT * 0.12), seg_b.animate.set_color(C_GOLD).shift(RIGHT * 0.12),
             run_time=1.2)
        play(FadeIn(t1), run_time=0.8)
        play(FadeIn(t2), run_time=1.0)
        wait(1.0)
        # cuadrado: 4 copias
        u1, u2 = count_and_formula(0.0, "4 copias", r"2^{2}=4", C_GOLD)
        cols = [C_BLUE, C_GOLD, C_MINT, C_ROSE]
        shifts = [np.array([-0.1, 0.1, 0]), np.array([0.1, 0.1, 0]), np.array([-0.1, -0.1, 0]), np.array([0.1, -0.1, 0])]
        play(*[sq[i].animate.set_color(cols[i]).set_fill(cols[i], 0.45).shift(shifts[i]) for i in range(4)], run_time=1.2)
        play(FadeIn(u1), run_time=0.8)
        play(FadeIn(u2), run_time=1.0)
        wait(1.0)
        # Sierpinski: 3 copias
        v1, v2 = count_and_formula(4.7, "3 copias", r"2^{1{.}58}\approx 3", C_MINT)
        cen = (sA + sB + sC) / 3
        anims = []
        for i, col in enumerate((C_BLUE, C_GOLD, C_MINT)):
            g = s_groups[i]
            gc = g.get_center()
            d = np.array([gc[0] - cen.real, gc[1] - cen.imag, 0.0])
            d = 0.14 * d / np.linalg.norm(d)
            anims.append(g.animate.set_fill(col, 0.95).shift(d))
        play(*anims, run_time=1.2)
        play(FadeIn(v1), run_time=0.8)
        play(FadeIn(v2), run_time=1.0)
        play(Indicate(v2, scale_factor=1.15, color=C_MINT), run_time=1.2)
        wait(3.0)
        play(FadeOut(Group(*self.mobjects)), run_time=0.8)

        # =============================================================
        # C4. ¿Y LA DEFINICIÓN?
        # =============================================================
        mark("C4. ¿Y la definición?")
        hdr = header("¿Y la definición matemática?", size=54)
        lines = [Text("Benoît Mandelbrot acuñó la palabra «fractal» en 1975", font_size=40, color=WHITE),
                 Text("Su definición no cubre todos los casos", font_size=40, color=WHITE),
                 Text("Por eso, en la práctica, estas ideas son una guía", font_size=40, color=C_GOLD)]
        for i, t in enumerate(lines):
            fit_text(t, 12.8).move_to(np.array([0, 1.3 - 1.5 * i, 0]))
        play(FadeIn(hdr), run_time=0.8)
        for t in lines:
            play(FadeIn(t, shift=0.15 * UP), run_time=1.0)
            wait(3.2)
        wait(1.0)
        play(FadeOut(Group(hdr, *lines)), run_time=0.8)

        # =============================================================
        # D. EJEMPLOS
        # =============================================================
        BOXW, BOXH, BOXC = 11.0, 5.7, (0.0, -0.05)

        def name_and_detail(name, detail_parts):
            nm = fit_text(Text(name, font_size=58, weight=BOLD, color=WHITE)).move_to(np.array([0, 3.45, 0]))
            parts = []
            for p in detail_parts:
                parts.append(MathTex(p[1], font_size=40, color=GREY_A) if p[0] == "m"
                             else Text(p[1], font_size=36, color=GREY_A))
            det = VGroup(*parts).arrange(RIGHT, buff=0.16, aligned_edge=DOWN)
            fit_text(det, 12.8).move_to(np.array([0, -3.4, 0]))
            return nm, det

        # ---- D1. Curva del dragón ----
        mark("D1. Dragón")
        nm, det = name_and_detail("Curva del dragón", [("t", "Cada paso: copia la curva, gírala 90° y pégala al final")])
        play(FadeIn(Group(nm, det)), run_time=0.8)

        def dragon_level(n):
            z = dragon_points(n)
            return make_fit(z, BOXC[0], BOXC[1], BOXW, BOXH)(z)

        dpal = color_gradient([C_BLUE, C_MINT, C_GOLD, C_ORANGE, C_ROSE], 12)
        dr = poly(dragon_level(0), dpal[0], 6)
        play(Create(dr), run_time=0.8)
        durs = [1.0, 0.95, 0.9, 0.85, 0.8, 0.75, 0.7, 0.7, 0.7, 0.7, 0.7]
        for n, dur in zip(range(1, 12), durs):
            nxt = poly(dragon_level(n), dpal[n], max(1.5, 6 - 0.4 * n))
            play(ReplacementTransform(dr, nxt), run_time=dur)
            dr = nxt
            wait(0.35)
        wait(2.0)
        play(FadeOut(Group(nm, det, dr)), run_time=0.8)

        # ---- D2. Helecho de Barnsley ----
        mark("D2. Helecho")
        nm, det = name_and_detail("Helecho de Barnsley", [("t", "Un punto salta al azar entre cuatro reglas… y dibuja un helecho")])
        play(FadeIn(Group(nm, det)), run_time=0.8)
        NF = 60000
        fp = chaos_game(NF, np.random.default_rng(7))
        f_fit = make_fit(fp[:, 0] + 1j * fp[:, 1], BOXC[0], BOXC[1], BOXW, BOXH)
        P3 = f_fit(fp[:, 0] + 1j * fp[:, 1])
        yn = (fp[:, 1] - fp[:, 1].min()) / (fp[:, 1].max() - fp[:, 1].min())
        rgba = np.zeros((len(fp), 4))
        rgba[:, 0] = 0.25 + 0.45 * yn
        rgba[:, 1] = 0.60 + 0.35 * yn
        rgba[:, 2] = 0.30 + 0.15 * yn
        rgba[:, 3] = 1.0
        cloud = PMobject(stroke_width=3.0)
        cloud.count = 0
        ft = ValueTracker(0.0)

        def cloud_upd(m):
            n = int(NF * ft.get_value() ** 3)
            if n > m.count:
                m.add_points(P3[m.count:n], rgbas=rgba[m.count:n])
                m.count = n
        cloud.add_updater(cloud_upd)
        self.add(cloud)
        play(ft.animate.set_value(1.0), run_time=11.0, rate_func=linear)
        cloud.clear_updaters()
        wait(2.0)
        fade_to_black()

        # ---- D3. Fractal de Newton ----
        mark("D3. Newton")
        nm, det = name_and_detail("Fractal de Newton", [("t", "Cada color: a qué raíz de"), ("m", r"z^3-1"),
                                                         ("t", "llega el método de Newton")])
        play(FadeIn(Group(nm, det)), run_time=0.8)
        IW, IH = 10.0, 10.0 * 9 / 16
        prev = None
        for (nx, ny) in [(16, 9), (48, 27), (160, 90), (480, 270), (960, 540)]:
            img = to_img(newton_image(0.0, 0.0, 2.2, nx, ny), IW, IH, BOXC, 960, 540)
            if prev is None:
                play(FadeIn(img), run_time=0.8)
            else:
                play(FadeIn(img), run_time=0.6)
                self.remove(prev)
            prev = img
            wait(1.0)
        wait(1.5)
        play(FadeOut(Group(nm, det, prev)), run_time=0.8)

        # ---- D4. Conjunto de Mandelbrot ----
        mark("D4. Mandelbrot")
        nm, det = name_and_detail("Conjunto de Mandelbrot", [("t", "Cada punto c: ¿escapa al infinito"), ("m", r"z\to z^2+c"),
                                                              ("t", "?")])
        play(FadeIn(Group(nm, det)), run_time=0.8)
        MX, MY = 640, 360
        mt = ValueTracker(0.0)

        def mandel_frame():
            cx, cy, hw = mandel_view(mt.get_value())
            mu = mandelbrot_mu(cx, cy, hw, MX, MY, mandel_maxit(hw))
            m = ImageMobject(np.clip(mandel_colorize(mu), 0, 255).astype(np.uint8))
            m.stretch_to_fit_width(IW)
            m.stretch_to_fit_height(IH)
            m.move_to(np.array([BOXC[0], BOXC[1], 0.0]))
            return m

        mframe = always_redraw(mandel_frame)
        play(FadeIn(mframe), run_time=1.2)
        wait(1.0)
        play(mt.animate.set_value(1.0), run_time=12.0, rate_func=linear)
        wait(1.5)
        mframe.clear_updaters()
        play(FadeOut(Group(nm, det, mframe)), run_time=0.8)

        # =============================================================
        # E. LISTA DE REPRODUCCIÓN (la pantalla final de YouTube va a la derecha)
        # =============================================================
        mark("E. Lista de reproducción")
        LEFT_X = -6.8                                        # borde izquierdo de la zona de miniaturas
        head = fit_text(Text("Mis shorts de fractales", font_size=56, weight=BOLD, color=WHITE), 7.4)
        head.move_to(np.array([LEFT_X + head.width / 2, 3.0, 0]))
        sub = fit_text(Text("Cada uno explica cómo se construye", font_size=34, color=C_GOLD), 7.4)
        sub.move_to(np.array([LEFT_X + sub.width / 2, -3.2, 0]))
        TW = 1.55                                            # lado de cada miniatura
        xs = [-5.9 + 1.95 * i for i in range(4)]
        ys = [1.15, -1.35]
        slots = [(xs[i % 4], ys[i // 4]) for i in range(8)]

        def thumb_curve(z, color, w=2.2):
            return poly(make_fit(z, 0, 0, TW * 0.92, TW * 0.92)(z), color, w)

        thumbs = []
        # Koch
        thumbs.append(("Koch", thumb_curve(koch_flake(4), C_BLUE)))
        # Sierpinski
        sz = [complex(-0.5, -0.43), complex(0.5, -0.43), complex(0, 0.43)]
        ft_s = make_fit(np.array(sz), 0, 0, TW * 0.92, TW * 0.92)
        thumbs.append(("Sierpinski", tri_polys(sierpinski_tris(sz[0], sz[1], sz[2], 5),
                                               lambda z: ft_s(z), C_GOLD, 0.95)))
        # Hilbert
        thumbs.append(("Hilbert", thumb_curve(hilbert_points(5), C_MINT, 1.8)))
        # Dragón
        thumbs.append(("Dragón", thumb_curve(dragon_points(12), C_ROSE, 1.5)))
        # Helecho
        fim = fern_raster(chaos_game(25000, np.random.default_rng(3)))
        fm = ImageMobject(np.clip(fim, 0, 255).astype(np.uint8))
        fm.stretch_to_fit_width(TW)
        fm.stretch_to_fit_height(TW)
        thumbs.append(("Helecho", fm))
        # Newton
        nm_img = ImageMobject(np.clip(newton_image(0, 0, 1.6, 240, 240), 0, 255).astype(np.uint8))
        nm_img.stretch_to_fit_width(TW)
        nm_img.stretch_to_fit_height(TW)
        thumbs.append(("Newton", nm_img))
        # Mandelbrot
        mm_img = ImageMobject(np.clip(mandel_colorize(mandelbrot_mu(-0.6, 0.0, 1.7, 240, 240, 120)), 0, 255).astype(np.uint8))
        mm_img.stretch_to_fit_width(TW)
        mm_img.stretch_to_fit_height(TW)
        thumbs.append(("Mandelbrot", mm_img))

        cards = []
        for (name, mob), (sx, sy) in zip(thumbs, slots):
            frame = RoundedRectangle(corner_radius=0.08, width=TW + 0.2, height=TW + 0.2, color=GREY_B,
                                     stroke_width=2).move_to(np.array([sx, sy, 0]))
            mob.move_to(np.array([sx, sy, 0]))
            lab = Text(name, font_size=22, color=GREY_A).move_to(np.array([sx, sy - TW / 2 - 0.28, 0]))
            cards.append(Group(frame, mob, lab))
        logo = MathTex(r"F_{GC}", font_size=90, color=BLUE_C).move_to(np.array([slots[7][0], slots[7][1], 0]))
        play(FadeIn(head), FadeIn(sub), run_time=1.2)
        play(LaggedStart(*[FadeIn(c) for c in cards], FadeIn(logo), lag_ratio=0.25), run_time=3.0)
        wait(22.0)                                           # los últimos segundos: pantalla final de YouTube
        play(FadeOut(Group(*self.mobjects)), run_time=1.0)
        mark("Fin")
        print("\n=== LÍNEA DE TIEMPO (s) ===")
        for name, t in marks:
            print("%6.1f  %s" % (t, name))