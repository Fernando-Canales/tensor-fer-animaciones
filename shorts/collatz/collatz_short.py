from manim import *
import numpy as np

# ---------------------------------------------------------------
# CONJETURA DE COLLATZ: empieza directamente con "Toma un número" (el 6)
# FORMATO: cuadro vertical 9:16 (1080x1920)
# Render: manim -qh --fps 60 collatz_short.py CollatzShort
# Escenas: 1) reglas y el camino de 6 hasta 1  2) la montaña rusa del 27
#          3) el árbol de todos los caminos hacia 1  4) la conjetura  5) logo
# ---------------------------------------------------------------
PORTRAIT = True
if PORTRAIT:
    config.pixel_width = 1080
    config.pixel_height = 1920
    config.frame_width = 6.0
    config.frame_height = 6.0 * 16 / 9


# ===============================================================
# MATEMÁTICAS Y DISPOSICIÓN (numpy puro; se puede probar sin Manim)
# ===============================================================
# BEGIN-GEOM
START = 6                          # número con el que se explican las reglas
BIG = 27                           # el número "granizo" (111 pasos, máximo 9232)

# Pausas (s) tras formarse cada uno de los tres primeros pasos del camino de 6: tiempo para explicar
PAUSE_CHAIN = {0: 1.8, 1: 1.8, 2: 1.4}

# Columna del camino de 6 (arriba -> abajo)
COL_Y0, COL_DY = 3.2, 0.85

# Gráfica del 27: pasos hacia abajo (eje vertical), valor hacia la derecha
X_AX, X_W = -2.5, 5.0
Y_TOP, Y_BOT = 3.6, -3.4

# Árbol de Collatz: 24 niveles, giro de 5° por cada ÷2 (inverso) y -10° por cada paso "×3+1" (inverso)
TREE_D, TREE_AE, TREE_AO = 24, 5.0, 10.0
TREE_W, TREE_H, TREE_CX, TREE_YBOT = 5.4, 6.9, 0.0, -3.1


def collatz_next(n):
    return n // 2 if n % 2 == 0 else 3 * n + 1


def trajectory(n):
    t = [n]
    while n != 1:
        n = collatz_next(n)
        t.append(n)
    return t


def children(m):
    """Números que llegan a m en un paso: 2m siempre, y (m-1)/3 si es impar mayor que 1
    (sólo cuando m ≡ 4 mod 6). El 1 no se cuenta como hijo del 4 (sería el ciclo 4-2-1)."""
    c = [2 * m]
    if m % 6 == 4 and (m - 1) // 3 > 1:
        c.append((m - 1) // 3)
    return c


def build_tree(D=TREE_D, aE=TREE_AE, aO=TREE_AO):
    """Árbol inverso desde 1: cada arista es de longitud 1 y gira según el tipo de paso.
    Devuelve pos {n: (x, y)} y layers[d] = lista de (n_padre, n_hijo, x0, y0, x1, y1, hijo_es_par)."""
    pos = {1: (0.0, 0.0)}
    level = [(1, 0.0, 0.0, np.radians(90.0))]
    layers = []
    for d in range(1, D + 1):
        nl, segs = [], []
        for (m, x, y, h) in level:
            for c in children(m):
                hc = h + np.radians(aE if c % 2 == 0 else -aO)
                xc, yc = x + np.cos(hc), y + np.sin(hc)
                pos[c] = (xc, yc)
                nl.append((c, xc, yc, hc))
                segs.append((m, c, x, y, xc, yc, c % 2 == 0))
        layers.append(segs)
        level = nl
    return pos, layers


def tree_fit(pos):
    """Escala y desplazamiento para que el árbol quepa en TREE_W x TREE_H con la raíz abajo."""
    xs = np.array([p[0] for p in pos.values()])
    ys = np.array([p[1] for p in pos.values()])
    s = min(TREE_W / (xs.max() - xs.min()), TREE_H / (ys.max() - ys.min()))
    xc = (xs.max() + xs.min()) / 2
    return s, (lambda x, y: (TREE_CX + (x - xc) * s, TREE_YBOT + (y - ys.min()) * s))


def chart_points(traj):
    vmax = max(traj)
    ys = np.linspace(Y_TOP, Y_BOT, len(traj))
    xs = X_AX + np.array(traj, dtype=float) / vmax * X_W
    return np.column_stack([xs, ys])
# END-GEOM


# ===============================================================
# ESCENA
# ===============================================================
class CollatzShort(Scene):
    def construct(self):
        C_EVEN = "#58C4DD"     # ÷2
        C_ODD = "#F08A5D"      # ×3+1
        COLOR_LOGO = BLUE_C

        def num(n, size=64, color=WHITE):
            return MathTex(str(n), font_size=size, color=color)

        def rule_color(n):
            return C_EVEN if n % 2 == 0 else C_ODD

        def rule_tex(n):
            return r"\div 2" if n % 2 == 0 else r"\times 3+1"

        # =============================================================
        # 1. "TOMA UN NÚMERO": el 6 y las dos reglas
        # =============================================================
        col = lambda i: np.array([0.0, COL_Y0 - COL_DY * i, 0.0])
        chain = trajectory(START)                       # [6, 3, 10, 5, 16, 8, 4, 2, 1]
        n0 = num(START, 64).scale(3.4).move_to(np.array([0.0, 0.6, 0.0]))
        self.play(FadeIn(n0, scale=0.6), run_time=1.0)
        self.wait(1.6)

        leg_par = MathTex(r"\text{par: }\div 2", font_size=40, color=C_EVEN).move_to(np.array([-1.7, 4.55, 0]))
        leg_imp = MathTex(r"\text{impar: }\times 3+1", font_size=40, color=C_ODD).move_to(np.array([1.2, 4.55, 0]))
        self.play(Write(leg_par), run_time=1.2)
        self.wait(1.2)
        self.play(Write(leg_imp), run_time=1.2)
        self.wait(1.4)

        # el 6 pasa a ser el primer elemento de la columna
        self.play(n0.animate.scale(1 / 3.4).move_to(col(0)), run_time=1.2)

        nodes = [n0]
        for i in range(len(chain) - 1):
            a, b = chain[i], chain[i + 1]
            slow = i in PAUSE_CHAIN
            arr = Arrow(col(i) + DOWN * 0.3, col(i + 1) + UP * 0.3, buff=0, color=rule_color(a), stroke_width=4,
                        tip_length=0.12, max_tip_length_to_length_ratio=0.6, max_stroke_width_to_length_ratio=20)
            lab = MathTex(rule_tex(a), font_size=40, color=rule_color(a)).move_to(
                col(i) + DOWN * (COL_DY / 2) + LEFT * 1.05)
            nb = num(b, 64)
            nodes.append(nb.move_to(col(i + 1)))
            self.play(Create(arr), FadeIn(lab), nodes[i].animate.set_color(rule_color(a)),
                      run_time=1.5 if slow else 1.4)
            self.play(FadeIn(nb, shift=0.15 * DOWN), run_time=1.5 if slow else 1.4)
            if slow:
                self.wait(PAUSE_CHAIN[i])

        # el ciclo 4 -> 2 -> 1 -> 4
        x_r, x_loop = 0.45, 1.05
        y1, y4 = col(len(chain) - 1)[1], col(len(chain) - 3)[1]
        loop = VGroup(Line(np.array([x_r, y1, 0]), np.array([x_loop, y1, 0]), color=C_ODD, stroke_width=4),
                      Line(np.array([x_loop, y1, 0]), np.array([x_loop, y4, 0]), color=C_ODD, stroke_width=4),
                      Arrow(np.array([x_loop, y4, 0]), np.array([x_r, y4, 0]), buff=0, color=C_ODD, stroke_width=4,
                            tip_length=0.15, max_tip_length_to_length_ratio=0.6))
        loop_lab = MathTex(r"\times 3+1", font_size=40, color=C_ODD).move_to(np.array([1.95, (y1 + y4) / 2 + 0.35, 0]))
        loop_txt = Text("ciclo", font_size=34, color=WHITE).move_to(np.array([1.95, (y1 + y4) / 2 - 0.25, 0]))
        self.play(Create(loop), FadeIn(loop_lab), run_time=3.6)
        self.play(FadeIn(loop_txt), run_time=0.8)
        self.wait(2.0)

        # =============================================================
        # 2. EL 27: LA MONTAÑA RUSA
        # =============================================================
        self.play(FadeOut(Group(*self.mobjects)), run_time=1.0)
        big = num(BIG, 64).scale(3.4).move_to(np.array([0.0, 0.6, 0.0]))
        self.play(FadeIn(big, scale=0.6), run_time=1.0)
        self.wait(1.8)
        self.play(FadeOut(big), run_time=0.7)

        traj = trajectory(BIG)
        V = len(traj) - 1                              # 111 pasos
        peak_step = int(np.argmax(traj))               # 77
        pts = chart_points(traj)
        P3 = lambda p: np.array([p[0], p[1], 0.0])
        axis = Line(np.array([X_AX, Y_TOP + 0.15, 0]), np.array([X_AX, Y_BOT - 0.15, 0]), color=GREY_B, stroke_width=2.5)
        self.play(Create(axis), run_time=0.7)

        tr = ValueTracker(0.0)

        def revealed():
            t = tr.get_value()
            i = min(int(np.floor(t)), V)
            g = VGroup()
            for s in range(i):
                c = C_ODD if traj[s + 1] > traj[s] else C_EVEN
                g.add(Line(P3(pts[s]), P3(pts[s + 1]), color=c, stroke_width=4))
            if i < V:
                f = t - i
                p0, p1 = P3(pts[i]), P3(pts[i + 1])
                c = C_ODD if traj[i + 1] > traj[i] else C_EVEN
                g.add(Line(p0, p0 + (p1 - p0) * f, color=c, stroke_width=4))
            return g

        def cur_point():
            t = tr.get_value()
            i = min(int(np.floor(t)), V)
            if i >= V:
                return P3(pts[V])
            return P3(pts[i]) + (P3(pts[i + 1]) - P3(pts[i])) * (t - i)

        def cur_dot():
            return Dot(cur_point(), radius=0.1, color=WHITE).set_z_index(5)

        def cur_label():
            t = tr.get_value()
            i = min(int(np.floor(t + 0.5)), V)
            p = cur_point()
            lab = Text(str(traj[i]), font_size=34, color=WHITE).set_z_index(6)
            lab.next_to(p, LEFT if p[0] > 0.3 else RIGHT, buff=0.15)
            return lab

        peak_lab = Text(str(max(traj)), font_size=34, color=C_ODD)
        peak_lab.move_to(P3(pts[peak_step]) + np.array([-0.5, -0.4, 0]))
        peak_lab.add_updater(lambda m: m.set_opacity(float(np.clip((tr.get_value() - peak_step + 0.5) / 2.0, 0, 1))))
        trail = always_redraw(revealed)
        dot = always_redraw(cur_dot)
        lab_now = always_redraw(cur_label)
        self.add(trail, dot, lab_now, peak_lab)
        self.play(tr.animate.set_value(V), run_time=15.0, rate_func=linear)
        steps_lab = Text("111 pasos", font_size=38, color=WHITE).move_to(np.array([1.0, Y_BOT, 0]))
        self.play(FadeIn(steps_lab, shift=0.2 * UP), run_time=1.0)
        self.wait(2.5)
        for m in (trail, dot, lab_now):
            m.clear_updaters()
        peak_lab.clear_updaters()
        self.play(FadeOut(Group(*self.mobjects)), run_time=1.0)

        # =============================================================
        # 3. EL ÁRBOL: todos los caminos terminan en 1
        # =============================================================
        pos, layers = build_tree()
        s, T = tree_fit(pos)
        sw = 2.0
        grow = []
        tree_layers = VGroup()
        for segs in layers:
            for even in (True, False):
                vm = VMobject(color=C_EVEN if even else C_ODD, stroke_width=sw)
                first = True
                for (m, c, x0, y0, x1, y1, ev) in segs:
                    if ev != even:
                        continue
                    p0, p1 = T(x0, y0), T(x1, y1)
                    vm.start_new_path(np.array([p0[0], p0[1], 0.0]))
                    vm.add_line_to(np.array([p1[0], p1[1], 0.0]))
                    first = False
                if not first:
                    tree_layers.add(vm)
        # (los pares de capas par/impar de cada profundidad se animan juntos: son 2 elementos consecutivos)
        by_depth = []
        k = 0
        for segs in layers:
            n_el = (1 if any(sg[6] for sg in segs) else 0) + (1 if any(not sg[6] for sg in segs) else 0)
            by_depth.append(tree_layers[k:k + n_el])
            k += n_el
        root = Dot(np.array([TREE_CX + T(0, 0)[0], T(0, 0)[1], 0]), radius=0.09, color=WHITE).set_z_index(5)
        root_lab = Text("1", font_size=34, color=WHITE).next_to(root, DOWN, buff=0.2)
        self.play(FadeIn(root), FadeIn(root_lab), run_time=0.8)
        self.play(LaggedStart(*[AnimationGroup(*[Create(m) for m in grp]) for grp in by_depth],
                              lag_ratio=0.35), run_time=11.0)
        self.wait(1.0)

        # el camino del 6 dentro del árbol
        path_nums = list(reversed(chain))                      # 1, 2, 4, 8, 16, 5, 10, 3, 6
        path_pts = [np.array([T(*pos[n])[0], T(*pos[n])[1], 0.0]) for n in path_nums]
        path = VMobject(color=WHITE, stroke_width=6).set_points_as_corners(path_pts).set_z_index(4)
        six = Dot(path_pts[-1], radius=0.11, color=WHITE).set_z_index(5)
        six_lab = Text("6", font_size=38, color=WHITE).next_to(six, UP, buff=0.18).set_z_index(5)
        self.play(Create(path), run_time=2.4)
        self.play(FadeIn(six), FadeIn(six_lab), run_time=0.6)
        self.wait(1.4)

        # =============================================================
        # 4. LA CONJETURA
        # =============================================================
        self.play(tree_layers.animate.set_opacity(0.18), path.animate.set_opacity(0.3),
                  FadeOut(Group(six, six_lab)), run_time=1.2)
        title = Text("Conjetura\nde Collatz", font_size=64, line_spacing=0.9, color=WHITE).move_to(np.array([0, 2.7, 0]))
        self.play(FadeIn(title, shift=0.3 * UP), run_time=1.2)
        self.wait(2.0)
        comp_a = Text("Comprobada hasta\nmás de", font_size=40, line_spacing=0.9, color=WHITE)
        comp_b = MathTex(r"10^{20}", font_size=110, color=C_ODD)
        comp = VGroup(comp_a, comp_b).arrange(DOWN, buff=0.3).move_to(np.array([0, 0.1, 0]))
        self.play(FadeIn(comp, shift=0.2 * UP), run_time=1.2)
        self.wait(3.2)
        dem = Text("Demostrada:\nnadie todavía", font_size=48, line_spacing=0.9, color=C_EVEN).move_to(np.array([0, -2.5, 0]))
        self.play(FadeIn(dem, shift=0.2 * UP), run_time=1.2)
        self.wait(4.0)

        # =============================================================
        # 5. CIERRE Y LOGO
        # =============================================================
        self.play(FadeOut(Group(*self.mobjects)), run_time=1.2)
        logo = MathTex(r"F_{GC}", font_size=150, color=COLOR_LOGO).move_to(ORIGIN)
        self.play(FadeIn(logo, scale=0.7), run_time=1.2)
        self.wait(2.5)