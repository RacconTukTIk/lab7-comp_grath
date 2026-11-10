"""
Лабораторная работа №7. Построение трёхмерных моделей
На основе лабораторной работы №6: многогранники, аффинные преобразования, проекции.
"""
import math
import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog


class Matrix4:
    def __init__(self, data=None):
        if data is None:
            self.m = [[1 if i == j else 0 for j in range(4)] for i in range(4)]
        else:
            self.m = [row[:] for row in data]

    @staticmethod
    def identity():
        return Matrix4()

    @staticmethod
    def translation(tx, ty, tz):
        return Matrix4([
            [1, 0, 0, tx],
            [0, 1, 0, ty],
            [0, 0, 1, tz],
            [0, 0, 0, 1],
        ])

    @staticmethod
    def scale(sx, sy, sz):
        return Matrix4([
            [sx, 0, 0, 0],
            [0, sy, 0, 0],
            [0, 0, sz, 0],
            [0, 0, 0, 1],
        ])

    @staticmethod
    def rotation_x(angle_deg):
        c, s = math.cos(math.radians(angle_deg)), math.sin(math.radians(angle_deg))
        return Matrix4([
            [1, 0, 0, 0],
            [0, c, -s, 0],
            [0, s, c, 0],
            [0, 0, 0, 1],
        ])

    @staticmethod
    def rotation_y(angle_deg):
        c, s = math.cos(math.radians(angle_deg)), math.sin(math.radians(angle_deg))
        return Matrix4([
            [c, 0, s, 0],
            [0, 1, 0, 0],
            [-s, 0, c, 0],
            [0, 0, 0, 1],
        ])

    @staticmethod
    def rotation_z(angle_deg):
        c, s = math.cos(math.radians(angle_deg)), math.sin(math.radians(angle_deg))
        return Matrix4([
            [c, -s, 0, 0],
            [s, c, 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1],
        ])

    @staticmethod
    def reflection(plane):
        if plane == 'xy':
            return Matrix4.scale(1, 1, -1)
        if plane == 'yz':
            return Matrix4.scale(-1, 1, 1)
        if plane == 'xz':
            return Matrix4.scale(1, -1, 1)
        raise ValueError(plane)

    @staticmethod
    def rotation_around_axis_line(point, direction, angle_deg):
        x, y, z = direction
        length = math.sqrt(x * x + y * y + z * z)
        if length < 1e-12:
            raise ValueError("Направляющий вектор не может быть нулевым")
        l, m, n = x / length, y / length, z / length
        c = math.cos(math.radians(angle_deg))
        s = math.sin(math.radians(angle_deg))
        a, b, cc = point
        rot = Matrix4([
            [l * l * (1 - c) + c, l * m * (1 - c) - n * s, l * n * (1 - c) + m * s, 0],
            [m * l * (1 - c) + n * s, m * m * (1 - c) + c, m * n * (1 - c) - l * s, 0],
            [n * l * (1 - c) - m * s, n * m * (1 - c) + l * s, n * n * (1 - c) + c, 0],
            [0, 0, 0, 1],
        ])
        return Matrix4.translation(a, b, cc) * rot * Matrix4.translation(-a, -b, -cc)

    def __mul__(self, other):
        result = Matrix4()
        for i in range(4):
            for j in range(4):
                result.m[i][j] = sum(self.m[i][k] * other.m[k][j] for k in range(4))
        return result

    def apply(self, p):
        x, y, z = p
        nx = self.m[0][0] * x + self.m[0][1] * y + self.m[0][2] * z + self.m[0][3]
        ny = self.m[1][0] * x + self.m[1][1] * y + self.m[1][2] * z + self.m[1][3]
        nz = self.m[2][0] * x + self.m[2][1] * y + self.m[2][2] * z + self.m[2][3]
        nw = self.m[3][0] * x + self.m[3][1] * y + self.m[3][2] * z + self.m[3][3]
        if abs(nw) > 1e-12 and nw != 1:
            nx, ny, nz = nx / nw, ny / nw, nz / nw
        return (nx, ny, nz)


class Point:
    __slots__ = ('x', 'y', 'z')

    def __init__(self, x, y, z):
        self.x, self.y, self.z = x, y, z

    def coords(self):
        return (self.x, self.y, self.z)


class Polygon:
    __slots__ = ('indices',)

    def __init__(self, indices):
        self.indices = list(indices)


class Polyhedron:
    def __init__(self, points=None, polygons=None, name=''):
        self.points = points if points else []
        self.polygons = polygons if polygons else []
        self.name = name

    def apply_matrix(self, matrix):
        self.points = [Point(*matrix.apply(p.coords())) for p in self.points]

    def center(self):
        if not self.points:
            return (0, 0, 0)
        n = len(self.points)
        return (sum(p.x for p in self.points) / n,
                sum(p.y for p in self.points) / n,
                sum(p.z for p in self.points) / n)

    def scale_about_center(self, s):
        cx, cy, cz = self.center()
        m = (Matrix4.translation(cx, cy, cz) *
             Matrix4.scale(s, s, s) *
             Matrix4.translation(-cx, -cy, -cz))
        self.apply_matrix(m)

    def copy(self):
        pts = [Point(p.x, p.y, p.z) for p in self.points]
        polys = [Polygon(poly.indices) for poly in self.polygons]
        return Polyhedron(pts, polys, self.name)


def build_tetrahedron():
    a = 1.0
    v = [Point(a, a, a), Point(a, -a, -a), Point(-a, a, -a), Point(-a, -a, a)]
    faces = [
        Polygon([0, 1, 2]), Polygon([0, 3, 1]),
        Polygon([0, 2, 3]), Polygon([1, 3, 2]),
    ]
    return Polyhedron(v, faces, 'Тетраэдр')


def build_hexahedron():
    a = 1.0
    v = [
        Point(-a, -a, -a), Point(a, -a, -a), Point(a, a, -a), Point(-a, a, -a),
        Point(-a, -a, a), Point(a, -a, a), Point(a, a, a), Point(-a, a, a),
    ]
    faces = [
        Polygon([0, 1, 2, 3]), Polygon([4, 7, 6, 5]),
        Polygon([0, 4, 5, 1]), Polygon([2, 6, 7, 3]),
        Polygon([1, 5, 6, 2]), Polygon([0, 3, 7, 4]),
    ]
    return Polyhedron(v, faces, 'Гексаэдр (куб)')


def build_octahedron():
    a = 1.0
    v = [
        Point(a, 0, 0), Point(-a, 0, 0),
        Point(0, a, 0), Point(0, -a, 0),
        Point(0, 0, a), Point(0, 0, -a),
    ]
    faces = [
        Polygon([0, 2, 4]), Polygon([2, 1, 4]),
        Polygon([1, 3, 4]), Polygon([3, 0, 4]),
        Polygon([2, 0, 5]), Polygon([1, 2, 5]),
        Polygon([3, 1, 5]), Polygon([0, 3, 5]),
    ]
    return Polyhedron(v, faces, 'Октаэдр')


def build_icosahedron():
    phi = (1 + math.sqrt(5)) / 2
    verts = [
        (-1, phi, 0), (1, phi, 0), (-1, -phi, 0), (1, -phi, 0),
        (0, -1, phi), (0, 1, phi), (0, -1, -phi), (0, 1, -phi),
        (phi, 0, -1), (phi, 0, 1), (-phi, 0, -1), (-phi, 0, 1),
    ]
    faces = [
        Polygon([0, 11, 5]), Polygon([0, 5, 1]), Polygon([0, 1, 7]),
        Polygon([0, 7, 10]), Polygon([0, 10, 11]),
        Polygon([1, 5, 9]), Polygon([5, 11, 4]), Polygon([11, 10, 2]),
        Polygon([10, 7, 6]), Polygon([7, 1, 8]),
        Polygon([3, 9, 4]), Polygon([3, 4, 2]), Polygon([3, 2, 6]),
        Polygon([3, 6, 8]), Polygon([3, 8, 9]),
        Polygon([4, 9, 5]), Polygon([2, 4, 11]), Polygon([6, 2, 10]),
        Polygon([8, 6, 7]), Polygon([9, 8, 1]),
    ]
    return Polyhedron([Point(*v) for v in verts], faces, 'Икосаэдр')


def build_dodecahedron():
    phi = (1 + math.sqrt(5)) / 2
    inv_phi = 1 / phi
    verts = [
        (1, 1, 1), (1, 1, -1), (1, -1, 1), (1, -1, -1),
        (-1, 1, 1), (-1, 1, -1), (-1, -1, 1), (-1, -1, -1),
        (0, inv_phi, phi), (0, inv_phi, -phi), (0, -inv_phi, phi), (0, -inv_phi, -phi),
        (inv_phi, phi, 0), (inv_phi, -phi, 0), (-inv_phi, phi, 0), (-inv_phi, -phi, 0),
        (phi, 0, inv_phi), (phi, 0, -inv_phi), (-phi, 0, inv_phi), (-phi, 0, -inv_phi),
    ]
    faces = [
        Polygon([0, 8, 10, 2, 16]), Polygon([0, 16, 17, 1, 12]), Polygon([0, 12, 14, 4, 8]),
        Polygon([1, 17, 3, 11, 9]), Polygon([1, 9, 5, 14, 12]), Polygon([2, 10, 6, 15, 13]),
        Polygon([2, 13, 3, 17, 16]), Polygon([3, 13, 15, 7, 11]), Polygon([4, 14, 5, 19, 18]),
        Polygon([4, 18, 6, 10, 8]), Polygon([5, 9, 11, 7, 19]), Polygon([6, 18, 19, 7, 15]),
    ]
    return Polyhedron([Point(*v) for v in verts], faces, 'Додекаэдр')


BUILDERS = {
    'Тетраэдр': build_tetrahedron,
    'Гексаэдр (куб)': build_hexahedron,
    'Октаэдр': build_octahedron,
    'Икосаэдр': build_icosahedron,
    'Додекаэдр': build_dodecahedron,
}


def rotate_point_around_coord_axis(p, axis, angle_deg):
    if axis == 'x':
        return Matrix4.rotation_x(angle_deg).apply(p)
    if axis == 'y':
        return Matrix4.rotation_y(angle_deg).apply(p)
    if axis == 'z':
        return Matrix4.rotation_z(angle_deg).apply(p)
    raise ValueError(axis)


def _on_axis(p, axis, eps=1e-9):
    x, y, z = p
    if axis == 'x':
        return abs(y) < eps and abs(z) < eps
    if axis == 'y':
        return abs(x) < eps and abs(z) < eps
    return abs(x) < eps and abs(y) < eps


def build_surface_of_revolution(profile, axis='y', divisions=16):
    """Образующая — набор точек, вращение на 360° вокруг координатной оси."""
    if len(profile) < 2:
        raise ValueError("Образующая должна содержать хотя бы две точки")
    if divisions < 3:
        raise ValueError("Количество разбиений должно быть не меньше 3")
    step = 360.0 / divisions
    points = []
    rings = []
    for pt in profile:
        coords = pt.coords() if isinstance(pt, Point) else tuple(pt)
        if _on_axis(coords, axis):
            rings.append([len(points)])
            points.append(Point(*coords))
        else:
            ring = []
            for j in range(divisions):
                ring.append(len(points))
                x, y, z = rotate_point_around_coord_axis(coords, axis, j * step)
                points.append(Point(x, y, z))
            rings.append(ring)

    faces = []
    for i in range(len(profile) - 1):
        a, b = rings[i], rings[i + 1]
        na, nb = len(a), len(b)
        for j in range(divisions):
            ia0 = a[j % na]
            ia1 = a[(j + 1) % na]
            ib0 = b[j % nb]
            ib1 = b[(j + 1) % nb]
            idx = []
            for k in (ia0, ib0, ib1, ia1):
                if k not in idx:
                    idx.append(k)
            if len(idx) >= 3:
                faces.append(Polygon(idx))
    return Polyhedron(points, faces, f'Фигура вращения ({axis}, n={divisions})')


SURFACE_FUNCTIONS = {
    'z = x² + y²': lambda x, y: x * x + y * y,
    'z = x² − y²': lambda x, y: x * x - y * y,
    'z = x · y': lambda x, y: x * y,
    'z = sin(x) · cos(y)': lambda x, y: math.sin(x) * math.cos(y),
    'z = sin(√(x²+y²))': lambda x, y: math.sin(math.sqrt(x * x + y * y)),
    'z = cos(x) + cos(y)': lambda x, y: math.cos(x) + math.cos(y),
    'z = e^{−(x²+y²)}': lambda x, y: math.exp(-(x * x + y * y)),
    'z = sin(x) + sin(y)': lambda x, y: math.sin(x) + math.sin(y),
}


def build_graph_surface(func, x0, x1, y0, y1, nx, ny, name=''):
    if nx < 1 or ny < 1:
        raise ValueError("Количество разбиений должно быть не меньше 1")
    if x1 == x0 or y1 == y0:
        raise ValueError("Диапазон не должен быть нулевой длины")
    points = []
    for i in range(nx + 1):
        x = x0 + (x1 - x0) * i / nx
        for j in range(ny + 1):
            y = y0 + (y1 - y0) * j / ny
            points.append(Point(x, y, func(x, y)))
    faces = []
    cols = ny + 1
    for i in range(nx):
        for j in range(ny):
            a = i * cols + j
            b = (i + 1) * cols + j
            c = (i + 1) * cols + (j + 1)
            d = i * cols + (j + 1)
            faces.append(Polygon([a, b, c, d]))
    return Polyhedron(points, faces, name or 'График z = f(x, y)')


def load_obj(path):
    vertices = []
    faces = []
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        for raw in f:
            line = raw.strip()
            if not line or line.startswith('#'):
                continue
            parts = line.split()
            tag = parts[0]
            if tag == 'v' and len(parts) >= 4:
                vertices.append(Point(float(parts[1]), float(parts[2]), float(parts[3])))
            elif tag == 'f' and len(parts) >= 4:
                indices = []
                for token in parts[1:]:
                    v_str = token.split('/')[0]
                    if not v_str:
                        continue
                    idx = int(v_str)
                    if idx < 0:
                        idx = len(vertices) + idx
                    else:
                        idx -= 1
                    if idx < 0 or idx >= len(vertices):
                        raise ValueError(f"Некорректный индекс вершины в OBJ: {token}")
                    indices.append(idx)
                if len(indices) >= 3:
                    faces.append(Polygon(indices))
    if not vertices:
        raise ValueError("В файле нет вершин (строк v)")
    if not faces:
        raise ValueError("В файле нет граней (строк f)")
    name = os.path.splitext(os.path.basename(path))[0]
    return Polyhedron(vertices, faces, name)


def save_obj(polyhedron, path):
    with open(path, 'w', encoding='utf-8') as f:
        f.write('# Wavefront OBJ\n')
        f.write(f'# {polyhedron.name}\n')
        f.write(f'# vertices: {len(polyhedron.points)}\n')
        f.write(f'# faces: {len(polyhedron.polygons)}\n')
        for p in polyhedron.points:
            f.write(f'v {p.x:.8f} {p.y:.8f} {p.z:.8f}\n')
        for poly in polyhedron.polygons:
            idx = ' '.join(str(i + 1) for i in poly.indices)
            f.write(f'f {idx}\n')


class Projection:
    @staticmethod
    def isometric(points):
        m = Matrix4.rotation_x(35.264) * Matrix4.rotation_y(45)
        return [m.apply(p.coords()) for p in points]

    @staticmethod
    def perspective(points, camera_z=-8.0, focal=5.0):
        result = []
        for p in points:
            z = p.z - camera_z
            if z < 0.01:
                z = 0.01
            x = p.x * focal / z
            y = p.y * focal / z
            result.append((x, y, p.z))
        return result


def _face_normal(pts):
    if len(pts) < 3:
        return (0, 0, 1)
    ax, ay, az = pts[0]
    bx, by, bz = pts[1]
    cx, cy, cz = pts[2]
    ux, uy, uz = bx - ax, by - ay, bz - az
    vx, vy, vz = cx - ax, cy - ay, cz - az
    nx = uy * vz - uz * vy
    ny = uz * vx - ux * vz
    nz = ux * vy - uy * vx
    length = math.sqrt(nx * nx + ny * ny + nz * nz)
    if length < 1e-12:
        return (0, 0, 1)
    return (nx / length, ny / length, nz / length)


def _shade_color(normal, light=(0.35, 0.55, 0.75)):
    lx, ly, lz = light
    ln = math.sqrt(lx * lx + ly * ly + lz * lz)
    lx, ly, lz = lx / ln, ly / ln, lz / ln
    nx, ny, nz = normal
    d = abs(nx * lx + ny * ly + nz * lz)
    t = 0.22 + 0.78 * d
    r = int(70 + 150 * t)
    g = int(90 + 140 * t)
    b = int(130 + 110 * t)
    return f'#{r:02x}{g:02x}{b:02x}'


PROFILE_PRESETS = {
    'Цилиндр': [(1.0, -1.2, 0.0), (1.0, 1.2, 0.0)],
    'Конус': [(0.05, -1.2, 0.0), (1.1, 1.2, 0.0)],
    'Ваза': [
        (0.35, -1.4, 0.0), (0.85, -1.1, 0.0), (1.05, -0.4, 0.0),
        (0.7, 0.2, 0.0), (0.55, 0.8, 0.0), (0.9, 1.3, 0.0),
    ],
    'Тор (профиль)': [
        (1.4 + 0.45 * math.cos(math.radians(a)), 0.45 * math.sin(math.radians(a)), 0.0)
        for a in range(0, 361, 20)
    ],
}


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Лабораторная работа №7. Построение трёхмерных моделей")

        self.polyhedron = build_tetrahedron()
        self.projection_mode = 'isometric'
        self.model_source = 'Тетраэдр'

        outer = ttk.Panedwindow(root, orient=tk.HORIZONTAL)
        outer.pack(fill=tk.BOTH, expand=True)

        left_wrap = ttk.Frame(outer)
        right = ttk.Frame(outer)
        outer.add(left_wrap, weight=0)
        outer.add(right, weight=1)

        self._build_controls(left_wrap)
        self.canvas = tk.Canvas(right, width=820, height=640, bg='#f7f7f7', highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind('<Configure>', lambda e: self.redraw())
        self.redraw()

    def _build_controls(self, parent):
        notebook = ttk.Notebook(parent)
        notebook.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        tab_model = ttk.Frame(notebook, padding=6)
        tab_rev = ttk.Frame(notebook, padding=6)
        tab_graph = ttk.Frame(notebook, padding=6)
        tab_aff = ttk.Frame(notebook, padding=6)
        notebook.add(tab_model, text='Модель / OBJ')
        notebook.add(tab_rev, text='Фигура вращения')
        notebook.add(tab_graph, text='График z=f(x,y)')
        notebook.add(tab_aff, text='Преобразования')

        self._build_model_tab(tab_model)
        self._build_revolution_tab(tab_rev)
        self._build_graph_tab(tab_graph)
        self._build_affine_tab(tab_aff)

    def _build_model_tab(self, ctrl):
        ttk.Label(ctrl, text="Многогранник (лаб. №6):").grid(row=0, column=0, columnspan=2, sticky='w')
        self.shape_var = tk.StringVar(value='Тетраэдр')
        shape_combo = ttk.Combobox(ctrl, textvariable=self.shape_var,
                                   values=list(BUILDERS.keys()), state='readonly', width=22)
        shape_combo.grid(row=1, column=0, columnspan=2, sticky='we', pady=2)
        shape_combo.bind('<<ComboboxSelected>>', lambda e: self.rebuild())
        ttk.Button(ctrl, text="Построить многогранник", command=self.rebuild).grid(
            row=2, column=0, columnspan=2, sticky='we', pady=2)

        ttk.Separator(ctrl).grid(row=3, column=0, columnspan=2, sticky='we', pady=8)
        ttk.Label(ctrl, text="Wavefront OBJ:").grid(row=4, column=0, columnspan=2, sticky='w')
        ttk.Button(ctrl, text="Загрузить .obj", command=self.load_obj_dialog).grid(
            row=5, column=0, sticky='we', padx=(0, 3), pady=2)
        ttk.Button(ctrl, text="Сохранить .obj", command=self.save_obj_dialog).grid(
            row=5, column=1, sticky='we', pady=2)

        ttk.Separator(ctrl).grid(row=6, column=0, columnspan=2, sticky='we', pady=8)
        ttk.Label(ctrl, text="Проекция:").grid(row=7, column=0, sticky='w')
        self.proj_var = tk.StringVar(value='Аксонометрическая')
        proj_combo = ttk.Combobox(ctrl, textvariable=self.proj_var,
                                  values=['Аксонометрическая', 'Перспективная'],
                                  state='readonly', width=20)
        proj_combo.grid(row=7, column=1, sticky='we')
        proj_combo.bind('<<ComboboxSelected>>', lambda e: self.set_projection())

        self.show_vertices = tk.BooleanVar(value=False)
        self.fill_faces = tk.BooleanVar(value=True)
        ttk.Checkbutton(ctrl, text="Показывать вершины", variable=self.show_vertices,
                        command=self.redraw).grid(row=8, column=0, columnspan=2, sticky='w')
        ttk.Checkbutton(ctrl, text="Заливка граней", variable=self.fill_faces,
                        command=self.redraw).grid(row=9, column=0, columnspan=2, sticky='w')

        self.info_var = tk.StringVar(value='')
        ttk.Label(ctrl, textvariable=self.info_var, wraplength=240, foreground='#333').grid(
            row=10, column=0, columnspan=2, sticky='w', pady=8)

        for i in range(2):
            ctrl.columnconfigure(i, weight=1)

    def _build_revolution_tab(self, ctrl):
        ttk.Label(ctrl, text="Ось вращения:").grid(row=0, column=0, sticky='w')
        self.rev_axis = tk.StringVar(value='y')
        ttk.Combobox(ctrl, textvariable=self.rev_axis, values=['x', 'y', 'z'],
                     state='readonly', width=6).grid(row=0, column=1, sticky='w')

        ttk.Label(ctrl, text="Разбиений (n):").grid(row=1, column=0, sticky='w')
        self.rev_div = tk.IntVar(value=24)
        ttk.Spinbox(ctrl, from_=3, to=128, textvariable=self.rev_div, width=8).grid(
            row=1, column=1, sticky='w')

        ttk.Label(ctrl, text="Заготовка образующей:").grid(row=2, column=0, sticky='w', pady=(8, 0))
        self.rev_preset = tk.StringVar(value='Ваза')
        ttk.Combobox(ctrl, textvariable=self.rev_preset, values=list(PROFILE_PRESETS.keys()),
                     state='readonly', width=16).grid(row=2, column=1, sticky='we', pady=(8, 0))
        ttk.Button(ctrl, text="Подставить заготовку", command=self.apply_profile_preset).grid(
            row=3, column=0, columnspan=2, sticky='we', pady=2)

        ttk.Label(ctrl, text="Образующая (x y z, по одной точке в строке):").grid(
            row=4, column=0, columnspan=2, sticky='w', pady=(8, 0))
        self.profile_text = tk.Text(ctrl, width=28, height=9, font=('Consolas', 9))
        self.profile_text.grid(row=5, column=0, columnspan=2, sticky='nsew')

        ttk.Label(ctrl, text="Клик по схеме добавляет точку профиля (плоскость XY):").grid(
            row=6, column=0, columnspan=2, sticky='w', pady=(6, 0))
        self.profile_canvas = tk.Canvas(ctrl, width=240, height=180, bg='white', highlightthickness=1,
                                        highlightbackground='#bbb')
        self.profile_canvas.grid(row=7, column=0, columnspan=2, pady=4)
        self.profile_canvas.bind('<Button-1>', self.on_profile_click)
        self.profile_canvas.bind('<Button-3>', self.on_profile_undo)
        self.apply_profile_preset()

        btns = ttk.Frame(ctrl)
        btns.grid(row=8, column=0, columnspan=2, sticky='we', pady=6)
        ttk.Button(btns, text="Построить фигуру", command=self.build_revolution).pack(
            side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 3))
        ttk.Button(btns, text="Очистить", command=self.clear_profile).pack(
            side=tk.LEFT, expand=True, fill=tk.X)

        ttk.Label(ctrl, text="ПКМ по схеме — удалить последнюю точку.",
                  foreground='#555').grid(row=9, column=0, columnspan=2, sticky='w')
        ctrl.rowconfigure(5, weight=1)
        ctrl.columnconfigure(1, weight=1)
        self.root.after(50, self.draw_profile_preview)

    def _build_graph_tab(self, ctrl):
        ttk.Label(ctrl, text="Функция f(x, y):").grid(row=0, column=0, columnspan=2, sticky='w')
        self.func_var = tk.StringVar(value='z = sin(x) · cos(y)')
        ttk.Combobox(ctrl, textvariable=self.func_var, values=list(SURFACE_FUNCTIONS.keys()),
                     state='readonly', width=24).grid(row=1, column=0, columnspan=2, sticky='we', pady=2)

        ttk.Label(ctrl, text="Диапазон X, Y  [min, max]:").grid(row=2, column=0, columnspan=2, sticky='w', pady=(8, 0))
        self.g_min = tk.DoubleVar(value=-3.14)
        self.g_max = tk.DoubleVar(value=3.14)
        ttk.Entry(ctrl, textvariable=self.g_min, width=10).grid(row=3, column=0, sticky='we', padx=(0, 3))
        ttk.Entry(ctrl, textvariable=self.g_max, width=10).grid(row=3, column=1, sticky='we')

        ttk.Label(ctrl, text="Разбиений по осям (n):").grid(row=4, column=0, sticky='w', pady=(8, 0))
        self.g_div = tk.IntVar(value=24)
        ttk.Spinbox(ctrl, from_=2, to=80, textvariable=self.g_div, width=8).grid(
            row=4, column=1, sticky='w', pady=(8, 0))

        ttk.Button(ctrl, text="Построить поверхность", command=self.build_graph).grid(
            row=5, column=0, columnspan=2, sticky='we', pady=10)

        ttk.Label(
            ctrl,
            text="Сегмент z = f(x, y) на квадрате [min, max]²\n"
                 "с одинаковым шагом по X и Y.\n"
                 "Модель содержит вершины и грани (quads).",
            wraplength=250, foreground='#444'
        ).grid(row=6, column=0, columnspan=2, sticky='w')
        ctrl.columnconfigure(0, weight=1)
        ctrl.columnconfigure(1, weight=1)

    def _build_affine_tab(self, ctrl):
        ttk.Label(ctrl, text="Смещение dx dy dz:").grid(row=0, column=0, columnspan=4, sticky='w')
        self.tx = tk.DoubleVar(value=0)
        self.ty = tk.DoubleVar(value=0)
        self.tz = tk.DoubleVar(value=0)
        ttk.Entry(ctrl, textvariable=self.tx, width=7).grid(row=1, column=0, padx=1)
        ttk.Entry(ctrl, textvariable=self.ty, width=7).grid(row=1, column=1, padx=1)
        ttk.Entry(ctrl, textvariable=self.tz, width=7).grid(row=1, column=2, padx=1)
        ttk.Button(ctrl, text="Сместить", command=self.do_translate).grid(row=1, column=3, padx=3)

        ttk.Label(ctrl, text="Масштаб s:").grid(row=2, column=0, sticky='w', pady=(8, 0))
        self.scale_var = tk.DoubleVar(value=1.2)
        ttk.Entry(ctrl, textvariable=self.scale_var, width=7).grid(row=3, column=0, padx=1)
        ttk.Button(ctrl, text="От начала", command=self.do_scale).grid(row=3, column=1, padx=2)
        ttk.Button(ctrl, text="От центра", command=self.do_scale_center).grid(row=3, column=2, columnspan=2, padx=2)

        ttk.Label(ctrl, text="Поворот (°), ось:").grid(row=4, column=0, columnspan=4, sticky='w', pady=(8, 0))
        self.rot_angle = tk.DoubleVar(value=30)
        self.rot_axis = tk.StringVar(value='y')
        ttk.Entry(ctrl, textvariable=self.rot_angle, width=7).grid(row=5, column=0, padx=1)
        ttk.Combobox(ctrl, textvariable=self.rot_axis, values=['x', 'y', 'z'],
                     state='readonly', width=5).grid(row=5, column=1)
        ttk.Button(ctrl, text="Поворот", command=self.do_rotate).grid(row=5, column=2, padx=2)
        ttk.Button(ctrl, text="Вокруг центра", command=self.do_rotate_center_axis).grid(row=5, column=3, padx=2)

        ttk.Label(ctrl, text="Отражение:").grid(row=6, column=0, sticky='w', pady=(8, 0))
        self.reflect_plane = tk.StringVar(value='xy')
        ttk.Combobox(ctrl, textvariable=self.reflect_plane, values=['xy', 'yz', 'xz'],
                     state='readonly', width=5).grid(row=7, column=0)
        ttk.Button(ctrl, text="Отразить", command=self.do_reflect).grid(row=7, column=1, padx=2)

        ttk.Label(ctrl, text="Поворот вокруг произвольной прямой").grid(
            row=8, column=0, columnspan=4, sticky='w', pady=(10, 0))
        ttk.Label(ctrl, text="Точка A:").grid(row=9, column=0, sticky='w')
        self.ax = tk.DoubleVar(value=0)
        self.ay = tk.DoubleVar(value=0)
        self.az = tk.DoubleVar(value=0)
        ttk.Entry(ctrl, textvariable=self.ax, width=7).grid(row=9, column=1)
        ttk.Entry(ctrl, textvariable=self.ay, width=7).grid(row=9, column=2)
        ttk.Entry(ctrl, textvariable=self.az, width=7).grid(row=9, column=3)

        ttk.Label(ctrl, text="Напр. d:").grid(row=10, column=0, sticky='w')
        self.dx = tk.DoubleVar(value=1)
        self.dy = tk.DoubleVar(value=1)
        self.dz = tk.DoubleVar(value=0)
        ttk.Entry(ctrl, textvariable=self.dx, width=7).grid(row=10, column=1)
        ttk.Entry(ctrl, textvariable=self.dy, width=7).grid(row=10, column=2)
        ttk.Entry(ctrl, textvariable=self.dz, width=7).grid(row=10, column=3)

        ttk.Label(ctrl, text="Угол (°):").grid(row=11, column=0, sticky='w')
        self.arb_angle = tk.DoubleVar(value=45)
        ttk.Entry(ctrl, textvariable=self.arb_angle, width=7).grid(row=11, column=1)
        ttk.Button(ctrl, text="Повернуть", command=self.do_rotate_arbitrary).grid(
            row=11, column=2, columnspan=2, sticky='we', padx=2)

        ttk.Button(ctrl, text="Сбросить текущий тип модели", command=self.reset_current).grid(
            row=12, column=0, columnspan=4, sticky='we', pady=12)

    def set_projection(self):
        self.projection_mode = 'isometric' if self.proj_var.get() == 'Аксонометрическая' else 'perspective'
        self.redraw()

    def rebuild(self):
        name = self.shape_var.get()
        self.polyhedron = BUILDERS[name]()
        self.model_source = name
        self.redraw()

    def reset_current(self):
        src = self.model_source
        if src in BUILDERS:
            self.polyhedron = BUILDERS[src]()
        self.redraw()

    def parse_profile(self):
        pts = []
        for line in self.profile_text.get('1.0', tk.END).splitlines():
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            parts = line.replace(',', ' ').split()
            if len(parts) < 2:
                raise ValueError(f"Некорректная строка образующей: {line}")
            x = float(parts[0])
            y = float(parts[1])
            z = float(parts[2]) if len(parts) >= 3 else 0.0
            pts.append(Point(x, y, z))
        return pts

    def set_profile_text(self, points):
        lines = [f'{p[0]:.4f}  {p[1]:.4f}  {p[2]:.4f}' for p in points]
        self.profile_text.delete('1.0', tk.END)
        self.profile_text.insert('1.0', '\n'.join(lines))
        self.draw_profile_preview()

    def apply_profile_preset(self):
        self.set_profile_text(PROFILE_PRESETS[self.rev_preset.get()])

    def clear_profile(self):
        self.profile_text.delete('1.0', tk.END)
        self.draw_profile_preview()

    def on_profile_click(self, event):
        x, y = self._canvas_to_profile(event.x, event.y)
        self.profile_text.insert(tk.END, f'\n{x:.4f}  {y:.4f}  0.0000')
        self.draw_profile_preview()

    def on_profile_undo(self, event):
        try:
            pts = self.parse_profile()
        except Exception:
            return
        if not pts:
            return
        self.set_profile_text([(p.x, p.y, p.z) for p in pts[:-1]])

    def _canvas_to_profile(self, sx, sy):
        w = self.profile_canvas.winfo_width() or 240
        h = self.profile_canvas.winfo_height() or 180
        span = 3.2
        x = (sx - w / 2) / (w / 2) * span
        y = (h / 2 - sy) / (h / 2) * span
        return x, y

    def draw_profile_preview(self):
        if not hasattr(self, 'profile_canvas'):
            return
        c = self.profile_canvas
        c.delete('all')
        w = c.winfo_width() or 240
        h = c.winfo_height() or 180
        span = 3.2
        c.create_line(w / 2, 0, w / 2, h, fill='#ccc')
        c.create_line(0, h / 2, w, h / 2, fill='#ccc')
        c.create_text(w / 2 + 8, 12, text='Y', fill='#888', anchor='w')
        c.create_text(w - 8, h / 2 - 8, text='X', fill='#888', anchor='e')
        try:
            pts = self.parse_profile()
        except Exception:
            return

        def to_s(p):
            return (w / 2 + p.x / span * (w / 2), h / 2 - p.y / span * (h / 2))

        screen = [to_s(p) for p in pts]
        for i in range(len(screen) - 1):
            c.create_line(*screen[i], *screen[i + 1], fill='#1a6', width=2)
        for (sx, sy) in screen:
            c.create_oval(sx - 3, sy - 3, sx + 3, sy + 3, fill='#c33', outline='')

    def build_revolution(self):
        try:
            profile = self.parse_profile()
            n = int(self.rev_div.get())
            axis = self.rev_axis.get()
            self.polyhedron = build_surface_of_revolution(profile, axis, n)
            self.model_source = 'revolution'
            self.redraw()
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def build_graph(self):
        try:
            name = self.func_var.get()
            func = SURFACE_FUNCTIONS[name]
            a, b = self.g_min.get(), self.g_max.get()
            n = int(self.g_div.get())
            self.polyhedron = build_graph_surface(func, a, b, a, b, n, n, name)
            self.model_source = 'graph'
            self.redraw()
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def load_obj_dialog(self):
        path = filedialog.askopenfilename(
            title='Открыть Wavefront OBJ',
            filetypes=[('Wavefront OBJ', '*.obj'), ('Все файлы', '*.*')],
        )
        if not path:
            return
        try:
            self.polyhedron = load_obj(path)
            self.model_source = 'obj'
            self.redraw()
        except Exception as e:
            messagebox.showerror("Ошибка загрузки OBJ", str(e))

    def save_obj_dialog(self):
        if not self.polyhedron.points:
            messagebox.showinfo("Сохранение", "Нет модели для сохранения")
            return
        path = filedialog.asksaveasfilename(
            title='Сохранить Wavefront OBJ',
            defaultextension='.obj',
            filetypes=[('Wavefront OBJ', '*.obj')],
            initialfile=(self.polyhedron.name or 'model').replace(' ', '_') + '.obj',
        )
        if not path:
            return
        try:
            save_obj(self.polyhedron, path)
            messagebox.showinfo("Сохранено", path)
        except Exception as e:
            messagebox.showerror("Ошибка сохранения", str(e))

    def do_translate(self):
        m = Matrix4.translation(self.tx.get(), self.ty.get(), self.tz.get())
        self.polyhedron.apply_matrix(m)
        self.redraw()

    def do_scale(self):
        s = self.scale_var.get()
        self.polyhedron.apply_matrix(Matrix4.scale(s, s, s))
        self.redraw()

    def do_scale_center(self):
        self.polyhedron.scale_about_center(self.scale_var.get())
        self.redraw()

    def do_rotate(self):
        angle = self.rot_angle.get()
        axis = self.rot_axis.get()
        if axis == 'x':
            m = Matrix4.rotation_x(angle)
        elif axis == 'y':
            m = Matrix4.rotation_y(angle)
        else:
            m = Matrix4.rotation_z(angle)
        self.polyhedron.apply_matrix(m)
        self.redraw()

    def do_rotate_center_axis(self):
        cx, cy, cz = self.polyhedron.center()
        axis = self.rot_axis.get()
        direction = {'x': (1, 0, 0), 'y': (0, 1, 0), 'z': (0, 0, 1)}[axis]
        m = Matrix4.rotation_around_axis_line((cx, cy, cz), direction, self.rot_angle.get())
        self.polyhedron.apply_matrix(m)
        self.redraw()

    def do_reflect(self):
        self.polyhedron.apply_matrix(Matrix4.reflection(self.reflect_plane.get()))
        self.redraw()

    def do_rotate_arbitrary(self):
        try:
            point = (self.ax.get(), self.ay.get(), self.az.get())
            direction = (self.dx.get(), self.dy.get(), self.dz.get())
            m = Matrix4.rotation_around_axis_line(point, direction, self.arb_angle.get())
            self.polyhedron.apply_matrix(m)
            self.redraw()
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def redraw(self):
        self.canvas.delete('all')
        w = self.canvas.winfo_width() or 800
        h = self.canvas.winfo_height() or 600
        ph = self.polyhedron
        if not ph.points:
            return

        if self.projection_mode == 'isometric':
            proj3 = Projection.isometric(ph.points)
        else:
            proj3 = Projection.perspective(ph.points)

        xs = [p[0] for p in proj3]
        ys = [p[1] for p in proj3]
        minx, maxx = min(xs), max(xs)
        miny, maxy = min(ys), max(ys)
        spanx = max(maxx - minx, 1e-6)
        spany = max(maxy - miny, 1e-6)
        margin = 40
        scale = min((w - 2 * margin) / spanx, (h - 2 * margin) / spany)
        cx = (minx + maxx) / 2
        cy = (miny + maxy) / 2

        def to_screen(p):
            return (w / 2 + (p[0] - cx) * scale, h / 2 - (p[1] - cy) * scale)

        screen_pts = [to_screen(p) for p in proj3]

        faces = []
        for poly in ph.polygons:
            idx = poly.indices
            if len(idx) < 3:
                continue
            world = [ph.points[i].coords() for i in idx]
            avg_z = sum(proj3[i][2] for i in idx) / len(idx)
            faces.append((avg_z, idx, world))
        faces.sort(key=lambda t: t[0])

        if self.fill_faces.get():
            for _, idx, world in faces:
                n = _face_normal(world)
                color = _shade_color(n)
                coords = []
                for i in idx:
                    coords.extend(screen_pts[i])
                self.canvas.create_polygon(*coords, fill=color, outline='#222', width=1)
        else:
            for _, idx, _ in faces:
                for i in range(len(idx)):
                    a, b = idx[i], idx[(i + 1) % len(idx)]
                    x1, y1 = screen_pts[a]
                    x2, y2 = screen_pts[b]
                    self.canvas.create_line(x1, y1, x2, y2, fill='#222', width=1.2)

        if self.show_vertices.get() and len(screen_pts) <= 400:
            for sx, sy in screen_pts:
                self.canvas.create_oval(sx - 2, sy - 2, sx + 2, sy + 2, fill='#c33', outline='')

        mode = 'Изометрия' if self.projection_mode == 'isometric' else 'Перспектива'
        caption = f'{ph.name}  |  {mode}  |  V={len(ph.points)}  F={len(ph.polygons)}'
        self.canvas.create_text(12, 12, anchor='nw', text=caption, fill='#444',
                                font=('Segoe UI', 10))
        self.info_var.set(caption)


SAMPLE_OBJ_NAMES = {
    'Тетраэдр': 'tetrahedron.obj',
    'Гексаэдр (куб)': 'hexahedron.obj',
    'Октаэдр': 'octahedron.obj',
    'Икосаэдр': 'icosahedron.obj',
    'Додекаэдр': 'dodecahedron.obj',
}


def write_sample_objs(folder):
    os.makedirs(folder, exist_ok=True)
    for name, builder in BUILDERS.items():
        save_obj(builder(), os.path.join(folder, SAMPLE_OBJ_NAMES[name]))
    vase = build_surface_of_revolution(
        [Point(*p) for p in PROFILE_PRESETS['Ваза']], 'y', 24)
    save_obj(vase, os.path.join(folder, 'vase_revolution.obj'))
    graph = build_graph_surface(
        SURFACE_FUNCTIONS['z = sin(x) · cos(y)'], -3.14, 3.14, -3.14, 3.14, 24, 24,
        'z = sin(x) · cos(y)')
    save_obj(graph, os.path.join(folder, 'graph_sin_cos.obj'))


if __name__ == '__main__':
    base = os.path.dirname(os.path.abspath(__file__))
    samples = os.path.join(base, 'models')
    write_sample_objs(samples)
    root = tk.Tk()
    App(root)
    root.geometry('1280x760')
    root.minsize(1000, 640)
    root.mainloop()
