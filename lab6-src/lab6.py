import tkinter as tk
from tkinter import ttk, messagebox
import math


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
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 1, 0],
            [tx, ty, tz, 1],
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
            [0, c, s, 0],
            [0, -s, c, 0],
            [0, 0, 0, 1],
        ])

    @staticmethod
    def rotation_y(angle_deg):
        c, s = math.cos(math.radians(angle_deg)), math.sin(math.radians(angle_deg))
        return Matrix4([
            [c, 0, -s, 0],
            [0, 1, 0, 0],
            [s, 0, c, 0],
            [0, 0, 0, 1],
        ])

    @staticmethod
    def rotation_z(angle_deg):
        c, s = math.cos(math.radians(angle_deg)), math.sin(math.radians(angle_deg))
        return Matrix4([
            [c, s, 0, 0],
            [-s, c, 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1],
        ])

    @staticmethod
    def reflection(plane):
        if plane == 'xy':
            return Matrix4.scale(1, 1, -1)
        elif plane == 'yz':
            return Matrix4.scale(-1, 1, 1)
        elif plane == 'xz':
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
            [l * l + c * (1 - l * l), l * (1 - c) * m + n * s, l * (1 - c) * n - m * s, 0],
            [l * (1 - c) * m - n * s, m * m + c * (1 - m * m), m * (1 - c) * n + l * s, 0],
            [l * (1 - c) * n + m * s, m * (1 - c) * n - l * s, n * n + c * (1 - n * n), 0],
            [0, 0, 0, 1],
        ])
        return Matrix4.translation(-a, -b, -cc) * rot * Matrix4.translation(a, b, cc)

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
    def __init__(self, points=None, polygons=None):
        self.points = points if points else []
        self.polygons = polygons if polygons else []

    def apply_matrix(self, matrix):
        new_points = []
        for p in self.points:
            nx, ny, nz = matrix.apply(p.coords())
            new_points.append(Point(nx, ny, nz))
        self.points = new_points

    def center(self):
        if not self.points:
            return (0, 0, 0)
        n = len(self.points)
        return (sum(p.x for p in self.points) / n,
                sum(p.y for p in self.points) / n,
                sum(p.z for p in self.points) / n)

    def scale_about_center(self, s):
        cx, cy, cz = self.center()
        m = (Matrix4.translation(-cx, -cy, -cz) *
             Matrix4.scale(s, s, s) *
             Matrix4.translation(cx, cy, cz))
        self.apply_matrix(m)


def build_tetrahedron():
    a = 1.0
    v = [
        Point(a, a, a),
        Point(a, -a, -a),
        Point(-a, a, -a),
        Point(-a, -a, a),
    ]
    faces = [
        Polygon([0, 1, 2]),
        Polygon([0, 3, 1]),
        Polygon([0, 2, 3]),
        Polygon([1, 3, 2]),
    ]
    return Polyhedron(v, faces)


def build_hexahedron():
    a = 1.0
    v = [
        Point(-a, -a, -a), Point(a, -a, -a), Point(a, a, -a), Point(-a, a, -a),
        Point(-a, -a, a), Point(a, -a, a), Point(a, a, a), Point(-a, a, a),
    ]
    faces = [
        Polygon([0, 1, 2, 3]),
        Polygon([4, 5, 6, 7]),
        Polygon([0, 1, 5, 4]),
        Polygon([2, 3, 7, 6]),
        Polygon([1, 2, 6, 5]),
        Polygon([0, 3, 7, 4]),
    ]
    return Polyhedron(v, faces)


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
    return Polyhedron(v, faces)


def build_icosahedron():
    phi = (1 + math.sqrt(5)) / 2
    verts = [
        (-1, phi, 0), (1, phi, 0), (-1, -phi, 0), (1, -phi, 0),
        (0, -1, phi), (0, 1, phi), (0, -1, -phi), (0, 1, -phi),
        (phi, 0, -1), (phi, 0, 1), (-phi, 0, -1), (-phi, 0, 1),
    ]
    points = [Point(*v) for v in verts]
    faces = [
        Polygon([0, 11, 5]), Polygon([0, 5, 1]), Polygon([0, 1, 7]), Polygon([0, 7, 10]), Polygon([0, 10, 11]),
        Polygon([1, 5, 9]), Polygon([5, 11, 4]), Polygon([11, 10, 2]), Polygon([10, 7, 6]), Polygon([7, 1, 8]),
        Polygon([3, 9, 4]), Polygon([3, 4, 2]), Polygon([3, 2, 6]), Polygon([3, 6, 8]), Polygon([3, 8, 9]),
        Polygon([4, 9, 5]), Polygon([2, 4, 11]), Polygon([6, 2, 10]), Polygon([8, 6, 7]), Polygon([9, 8, 1]),
    ]
    return Polyhedron(points, faces)


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
    points = [Point(*v) for v in verts]
    faces = [
        Polygon([0, 8, 10, 2, 16]), Polygon([0, 16, 17, 1, 12]), Polygon([0, 12, 14, 4, 8]),
        Polygon([1, 17, 3, 11, 9]), Polygon([1, 9, 5, 14, 12]), Polygon([2, 10, 6, 15, 13]),
        Polygon([2, 13, 3, 17, 16]), Polygon([3, 13, 15, 7, 11]), Polygon([4, 14, 5, 19, 18]),
        Polygon([4, 18, 6, 10, 8]), Polygon([5, 9, 11, 7, 19]), Polygon([6, 18, 19, 7, 15]),
    ]
    return Polyhedron(points, faces)


BUILDERS = {
    'Тетраэдр': build_tetrahedron,
    'Гексаэдр (куб)': build_hexahedron,
    'Октаэдр': build_octahedron,
    'Икосаэдр (бонус)': build_icosahedron,
    'Додекаэдр (бонус)': build_dodecahedron,
}


class Projection:
    @staticmethod
    def isometric(points):
        m = Matrix4.rotation_y(45) * Matrix4.rotation_x(35.264)
        result = []
        for p in points:
            x, y, z = m.apply(p.coords())
            result.append((x, y))
        return result

    @staticmethod
    def perspective(points, camera_z=-8.0, focal=5.0):
        result = []
        for p in points:
            z = p.z - camera_z
            if z < 0.01:
                z = 0.01
            x = p.x * focal / z
            y = p.y * focal / z
            result.append((x, y))
        return result


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Лабораторная работа №6: Аффинные преобразования в 3D")

        self.polyhedron = build_tetrahedron()
        self.projection_mode = 'isometric'

        ctrl = ttk.Frame(root, padding=5)
        ctrl.pack(side=tk.TOP, fill=tk.X)

        ttk.Label(ctrl, text="Многогранник:").grid(row=0, column=0, sticky='w')
        self.shape_var = tk.StringVar(value='Тетраэдр')
        shape_combo = ttk.Combobox(ctrl, textvariable=self.shape_var,
                                   values=list(BUILDERS.keys()), state='readonly', width=18)
        shape_combo.grid(row=0, column=1, padx=3)
        shape_combo.bind('<<ComboboxSelected>>', lambda e: self.rebuild())

        ttk.Label(ctrl, text="Проекция:").grid(row=0, column=2, sticky='w', padx=(10, 0))
        self.proj_var = tk.StringVar(value='Аксонометрическая')
        proj_combo = ttk.Combobox(ctrl, textvariable=self.proj_var,
                                  values=['Аксонометрическая', 'Перспективная'],
                                  state='readonly', width=16)
        proj_combo.grid(row=0, column=3, padx=3)
        proj_combo.bind('<<ComboboxSelected>>', lambda e: self.set_projection())

        row = 1
        ttk.Label(ctrl, text="Смещение (dx dy dz):").grid(row=row, column=0, sticky='w')
        self.tx = tk.DoubleVar(value=0)
        self.ty = tk.DoubleVar(value=0)
        self.tz = tk.DoubleVar(value=0)
        ttk.Entry(ctrl, textvariable=self.tx, width=5).grid(row=row, column=1, padx=1)
        ttk.Entry(ctrl, textvariable=self.ty, width=5).grid(row=row, column=2, padx=1)
        ttk.Entry(ctrl, textvariable=self.tz, width=5).grid(row=row, column=3, padx=1)
        ttk.Button(ctrl, text="Сместить", command=self.do_translate).grid(row=row, column=4, padx=3)

        row += 1
        ttk.Label(ctrl, text="Масштаб (s):").grid(row=row, column=0, sticky='w')
        self.scale_var = tk.DoubleVar(value=1.0)
        ttk.Entry(ctrl, textvariable=self.scale_var, width=5).grid(row=row, column=1, padx=1)
        ttk.Button(ctrl, text="Масштаб", command=self.do_scale).grid(row=row, column=2, padx=3)
        ttk.Button(ctrl, text="Масштаб отн. центра", command=self.do_scale_center).grid(row=row, column=3,
                                                                                        columnspan=2, padx=3)

        row += 1
        ttk.Label(ctrl, text="Поворот (°):").grid(row=row, column=0, sticky='w')
        self.rot_angle = tk.DoubleVar(value=30)
        ttk.Entry(ctrl, textvariable=self.rot_angle, width=5).grid(row=row, column=1, padx=1)
        ttk.Label(ctrl, text="Ось:").grid(row=row, column=2, sticky='e')
        self.rot_axis = tk.StringVar(value='x')
        ttk.Combobox(ctrl, textvariable=self.rot_axis, values=['x', 'y', 'z'], state='readonly', width=3).grid(row=row,
                                                                                                             column=3)
        ttk.Button(ctrl, text="Поворот", command=self.do_rotate).grid(row=row, column=4, padx=3)

        row += 1
        ttk.Button(ctrl, text="Вращение вокруг центра || оси", command=self.do_rotate_center_axis).grid(row=row,
                                                                                                        column=0,
                                                                                                        columnspan=3,
                                                                                                        padx=3,
                                                                                                        sticky='we')

        row += 1
        ttk.Label(ctrl, text="Отражение отн.:").grid(row=row, column=0, sticky='w')
        self.reflect_plane = tk.StringVar(value='xy')
        ttk.Combobox(ctrl, textvariable=self.reflect_plane, values=['xy', 'yz', 'xz'], state='readonly', width=5).grid(
            row=row, column=1)
        ttk.Button(ctrl, text="Отразить", command=self.do_reflect).grid(row=row, column=2, padx=3)

        row += 1
        ttk.Label(ctrl, text="Прямая: A(").grid(row=row, column=0, sticky='w')
        self.ax = tk.DoubleVar(value=0)
        self.ay = tk.DoubleVar(value=0)
        self.az = tk.DoubleVar(value=0)
        ttk.Entry(ctrl, textvariable=self.ax, width=4).grid(row=row, column=1, padx=1)
        ttk.Entry(ctrl, textvariable=self.ay, width=4).grid(row=row, column=2, padx=1)
        ttk.Entry(ctrl, textvariable=self.az, width=4).grid(row=row, column=3, padx=1)

        row += 1
        ttk.Label(ctrl, text="напр. d(").grid(row=row, column=0, sticky='w')
        self.dx = tk.DoubleVar(value=1)
        self.dy = tk.DoubleVar(value=1)
        self.dz = tk.DoubleVar(value=0)
        ttk.Entry(ctrl, textvariable=self.dx, width=4).grid(row=row, column=1, padx=1)
        ttk.Entry(ctrl, textvariable=self.dy, width=4).grid(row=row, column=2, padx=1)
        ttk.Entry(ctrl, textvariable=self.dz, width=4).grid(row=row, column=3, padx=1)

        row += 1
        ttk.Label(ctrl, text="Угол (°):").grid(row=row, column=0, sticky='w')
        self.arb_angle = tk.DoubleVar(value=45)
        ttk.Entry(ctrl, textvariable=self.arb_angle, width=5).grid(row=row, column=1, padx=1)
        ttk.Button(ctrl, text="Поворот вокруг прямой", command=self.do_rotate_arbitrary).grid(row=row, column=2,
                                                                                              columnspan=2, padx=3,
                                                                                              sticky='we')

        row += 1
        ttk.Button(ctrl, text="Сбросить модель", command=self.rebuild).grid(row=row, column=0, columnspan=5, pady=5,
                                                                            sticky='we')

        self.canvas = tk.Canvas(root, width=800, height=600, bg='white')
        self.canvas.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
        self.canvas.bind('<Configure>', lambda e: self.redraw())

        self.redraw()

    def set_projection(self):
        self.projection_mode = 'isometric' if self.proj_var.get() == 'Аксонометрическая' else 'perspective'
        self.redraw()

    def rebuild(self):
        self.polyhedron = BUILDERS[self.shape_var.get()]()
        self.redraw()

    def do_translate(self):
        m = Matrix4.translation(self.tx.get(), self.ty.get(), self.tz.get())
        self.polyhedron.apply_matrix(m)
        self.redraw()

    def do_scale(self):
        s = self.scale_var.get()
        m = Matrix4.scale(s, s, s)
        self.polyhedron.apply_matrix(m)
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
        if axis == 'x':
            direction = (1, 0, 0)
        elif axis == 'y':
            direction = (0, 1, 0)
        else:
            direction = (0, 0, 1)
        m = Matrix4.rotation_around_axis_line((cx, cy, cz), direction, self.rot_angle.get())
        self.polyhedron.apply_matrix(m)
        self.redraw()

    def do_reflect(self):
        plane = self.reflect_plane.get()
        m = Matrix4.reflection(plane)
        self.polyhedron.apply_matrix(m)
        self.redraw()

    def do_rotate_arbitrary(self):
        try:
            point = (self.ax.get(), self.ay.get(), self.az.get())
            direction = (self.dx.get(), self.dy.get(), self.dz.get())
            angle = self.arb_angle.get()
            m = Matrix4.rotation_around_axis_line(point, direction, angle)
            self.polyhedron.apply_matrix(m)
            self.redraw()
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def redraw(self):
        self.canvas.delete("all")
        w = self.canvas.winfo_width() or 800
        h = self.canvas.winfo_height() or 600

        points = self.polyhedron.points
        if not points:
            return

        if self.projection_mode == 'isometric':
            proj = Projection.isometric(points)
        else:
            proj = Projection.perspective(points)

        xs = [p[0] for p in proj]
        ys = [p[1] for p in proj]
        minx, maxx = min(xs), max(xs)
        miny, maxy = min(ys), max(ys)
        spanx = max(maxx - minx, 1e-6)
        spany = max(maxy - miny, 1e-6)
        margin = 40
        scale = min((w - 2 * margin) / spanx, (h - 2 * margin) / spany)
        cx = (minx + maxx) / 2
        cy = (miny + maxy) / 2

        def to_screen(p):
            return (w / 2 + (p[0] - cx) * scale,
                    h / 2 - (p[1] - cy) * scale)

        screen_pts = [to_screen(p) for p in proj]

        for poly in self.polyhedron.polygons:
            idx = poly.indices
            for i in range(len(idx)):
                a = idx[i]
                b = idx[(i + 1) % len(idx)]
                x1, y1 = screen_pts[a]
                x2, y2 = screen_pts[b]
                self.canvas.create_line(x1, y1, x2, y2, fill='black', width=1.5)

        for (sx, sy) in screen_pts:
            self.canvas.create_oval(sx - 2, sy - 2, sx + 2, sy + 2, fill='red', outline='')

        mode = 'Изометрия' if self.projection_mode == 'isometric' else 'Перспектива'
        self.canvas.create_text(10, 10, anchor='nw', text=f"{self.shape_var.get()} | {mode}",
                                fill='gray', font=('Arial', 10))


if __name__ == '__main__':
    root = tk.Tk()
    app = App(root)
    root.geometry("1000x750")
    root.mainloop()