from manim import *
import numpy as np

# ---------------------------------------------------------------
# CONJETURA DE COLLATZ: empieza directamente con "Toma un número"
# FORMATO: cuadro vertical 9:16 (1080x1920)
# Render: manim -qh --fps 60 collatz_short.py CollatzShort
# Escenas: 1) ejemplo del 6 (con el ciclo 4-2-1)   2) ejemplo del 5
#          3) el 27: la montaña rusa               4) la conjetura, con el árbol translúcido de fondo
#          5) logo
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
EXAMPLES = (6, 5)                  # 6: par -> impar ...   5: impar -> pares hasta 1
BIG = 27                           # el número "granizo" (111 pasos, máximo 9232)

# Ritmo de los ejemplos: un número nuevo cada ARROW_T + NUM_T + GAP_T = 2.2 s (>= 2 s)
ARROW_T, NUM_T, GAP_T = 1.0, 0.5, 0.7

# Columna del camino (arriba -> abajo)
COL_Y0, COL_DY = 3.45, 0.85

# Gráfica del 27: pasos hacia abajo (eje vertical), valor hacia la derecha
X_AX, X_W = -2.5, 5.0
Y_TOP, Y_BOT = 3.6, -3.4

# Árbol de Collatz: 24 niveles, giro de 5° por cada ÷2 (inverso) y -10° por cada paso "×3+1" (inverso)
TREE_D, TREE_AE, TREE_AO = 24, 5.0, 10.0
TREE_W, TREE_H, TREE_CX, TREE_YBOT = 5.4, 6.9, 0.0, -3.1
TREE_OPACITY = 0.22                # el árbol de fondo es translúcido

SHOW_FACTS = True                  # tras el enunciado: "Comprobada hasta más de 10^20 / Demostrada: nadie todavía"


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
    """Escala y transformación para que el árbol quepa en TREE_W x TREE_H con la raíz abajo."""
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

        def fit(mob, maxw=5.2):
            if mob.width > maxw:
                mob.scale_to_fit_width(maxw)
            return mob

        col = lambda i: np.array([0.0, COL_Y0 - COL_DY * i, 0.0])
        legend = []

        def run_example(start, first):
            """Muestra el camino de `start` hasta 1 en columna. Devuelve (lista de mobjects, camino)."""
            chain = trajectory(start)
            items = []
            n0 = num(start, 64).scale(3.4).move_to(np.array([0.0, 0.6, 0.0]))
            self.play(FadeIn(n0, scale=0.6), run_time=1.0)
            self.wait(1.6)
            if first:                                           # las dos reglas, sólo la primera vez
                leg_par = MathTex(r"\text{par: }\div 2", font_size=40, color=C_EVEN).move_to(np.array([-1.7, 4.55, 0]))
                leg_imp = MathTex(r"\text{impar: }\times 3+1", font_size=40, color=C_ODD).move_to(np.array([1.2, 4.55, 0]))
                legend.extend([leg_par, leg_imp])
                self.play(Write(leg_par), run_time=1.2)
                self.wait(1.0)
                self.play(Write(leg_imp), run_time=1.2)
                self.wait(1.4)
            self.play(n0.animate.scale(1 / 3.4).move_to(col(0)), run_time=1.2)
            nodes = [n0]
            items.append(n0)
            for i in range(len(chain) - 1):
                a, b = chain[i], chain[i + 1]
                arr = Arrow(col(i) + DOWN * 0.3, col(i + 1) + UP * 0.3, buff=0, color=rule_color(a), stroke_width=4,
                            tip_length=0.12, max_tip_length_to_length_ratio=0.6, max_stroke_width_to_length_ratio=20)
                lab = MathTex(rule_tex(a), font_size=40, color=rule_color(a)).move_to(
                    col(i) + DOWN * (COL_DY / 2) + LEFT * 1.05)
                nb = num(b, 64).move_to(col(i + 1))
                nodes.append(nb)
                items += [arr, lab, nb]
                self.play(Create(arr), FadeIn(lab), nodes[i].animate.set_color(rule_color(a)), run_time=ARROW_T)
                self.play(FadeIn(nb, shift=0.15 * DOWN), run_time=NUM_T)
                self.wait(GAP_T)
            return items, chain

        # =============================================================
        # 1. "TOMA UN NÚMERO": el 6 (y el ciclo 4 -> 2 -> 1 -> 4)
        # =============================================================
        items6, chain6 = run_example(EXAMPLES[0], first=True)
        x_r, x_loop = 0.45, 1.05
        y1, y4 = col(len(chain6) - 1)[1], col(len(chain6) - 3)[1]
        loop = VGroup(Line(np.array([x_r, y1, 0]), np.array([x_loop, y1, 0]), color=C_ODD, stroke_width=4),
                      Line(np.array([x_loop, y1, 0]), np.array([x_loop, y4, 0]), color=C_ODD, stroke_width=4),
                      Arrow(np.array([x_loop, y4, 0]), np.array([x_r, y4, 0]), buff=0, color=C_ODD, stroke_width=4,
                            tip_length=0.15, max_tip_length_to_length_ratio=0.6))
        loop_lab = MathTex(r"\times 3+1", font_size=40, color=C_ODD).move_to(np.array([1.95, (y1 + y4) / 2 + 0.35, 0]))
        loop_txt = Text("ciclo", font_size=34, color=WHITE).move_to(np.array([1.95, (y1 + y4) / 2 - 0.25, 0]))
        self.play(Create(loop), FadeIn(loop_lab), run_time=1.6)
        self.play(FadeIn(loop_txt), run_time=0.8)
        self.wait(2.2)

        # =============================================================
        # 2. EL 5: impar primero, luego todo pares
        # =============================================================
        self.play(FadeOut(Group(*items6, loop, loop_lab, loop_txt)), run_time=1.0)
        items5, chain5 = run_example(EXAMPLES[1], first=False)
        self.wait(1.6)

        # =============================================================
        # 3. EL 27: LA MONTAÑA RUSA
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
        for m in (trail, dot, lab_now, peak_lab):
            m.clear_updaters()
        self.play(FadeOut(Group(*self.mobjects)), run_time=1.0)

        # =============================================================
        # 4. LA CONJETURA, con el árbol de Collatz translúcido de fondo
        # =============================================================
        pos, layers = build_tree()
        s, T = tree_fit(pos)
        by_depth = []
        for segs in layers:
            grp = []
            for even in (True, False):
                vm = VMobject(color=C_EVEN if even else C_ODD, stroke_width=2.0, stroke_opacity=TREE_OPACITY)
                used = False
                for (m, c, x0, y0, x1, y1, ev) in segs:
                    if ev != even:
                        continue
                    p0, p1 = T(x0, y0), T(x1, y1)
                    vm.start_new_path(np.array([p0[0], p0[1], 0.0]))
                    vm.add_line_to(np.array([p1[0], p1[1], 0.0]))
                    used = True
                if used:
                    grp.append(vm)
            by_depth.append(grp)

        title = fit(Text("Conjetura\nde Collatz", font_size=84, line_spacing=0.9, color=WHITE).set_z_index(10), 5.2)
        title.move_to(np.array([0, 2.3, 0]))
        statement = fit(Text("Todo número positivo\nacaba llegando a 1", font_size=50, line_spacing=0.95,
                             color=WHITE).set_z_index(10), 5.2)
        statement.move_to(np.array([0, -0.6, 0]))
        grow = LaggedStart(*[AnimationGroup(*[Create(m) for m in grp]) for grp in by_depth],
                           lag_ratio=0.35, run_time=9.0)
        self.play(FadeIn(title, shift=0.3 * UP, run_time=1.4), grow,
                  Succession(Wait(3.0), FadeIn(statement, shift=0.2 * UP, run_time=1.2)))
        self.wait(3.0)
        if SHOW_FACTS:
            self.play(FadeOut(statement), run_time=0.8)
            comp_a = Text("Comprobada hasta\nmás de", font_size=40, line_spacing=0.9, color=WHITE).set_z_index(10)
            comp_b = MathTex(r"10^{20}", font_size=110, color=C_ODD).set_z_index(10)
            comp = VGroup(comp_a, comp_b).arrange(DOWN, buff=0.3).move_to(np.array([0, 0.0, 0]))
            self.play(FadeIn(comp, shift=0.2 * UP), run_time=1.2)
            self.wait(3.0)
            dem = fit(Text("Demostrada:\nnadie todavía", font_size=48, line_spacing=0.9,
                           color=C_EVEN).set_z_index(10), 5.2).move_to(np.array([0, -2.5, 0]))
            self.play(FadeIn(dem, shift=0.2 * UP), run_time=1.2)
            self.wait(3.5)
        else:
            self.wait(2.0)

        # =============================================================
        # 5. CIERRE Y LOGO
        # =============================================================
        self.play(FadeOut(Group(*self.mobjects)), run_time=1.2)
        logo = MathTex(r"F_{GC}", font_size=150, color=COLOR_LOGO).move_to(ORIGIN)
        self.play(FadeIn(logo, scale=0.7), run_time=1.2)
        self.wait(2.5)