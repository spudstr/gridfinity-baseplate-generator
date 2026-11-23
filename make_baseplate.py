"""Standard Gridfinity baseplate (open-frame / "light" style).

42 mm grid, standard 4.65 mm socket profile (from the top: 2.15 mm 45-degree
chamfer, 1.8 mm vertical, 0.7 mm 45-degree chamfer), 4 mm outer corner radius.
Writes a binary STL in millimetres, by default to output/.

Run:  py make_baseplate.py [cols] [rows] [output.stl]
"""
import math
import struct
import sys
from pathlib import Path

PITCH = 42.0
R_TOP = 4.0          # corner radius of each socket at the top / plate corners
# (z, inset from the cell edge) for each level of the socket, bottom to top
PROFILE = [(0.0, 2.85), (0.7, 2.15), (2.5, 2.15), (4.65, 0.0)]
HEIGHT = PROFILE[-1][0]
ARC_SEGS = 12        # segments per rounded corner


def build(cols, rows):
    W, D = cols * PITCH, rows * PITCH
    tris = []

    def flat(t, up):
        """Add a horizontal triangle facing +Z (up=True) or -Z."""
        (ax, ay, _), (bx, by, _), (cx, cy, _) = t
        cz = (bx - ax) * (cy - ay) - (by - ay) * (cx - ax)
        if abs(cz) < 1e-12:
            return
        if (cz > 0) != up:
            t = (t[0], t[2], t[1])
        tris.append(t)

    for i in range(cols):
        for j in range(rows):
            x0, y0, x1, y1 = i * PITCH, j * PITCH, (i + 1) * PITCH, (j + 1) * PITCH
            # Corners counter-clockwise: (corner point, arc centre offset dir, start angle)
            corners = [((x1, y0), (-1, 1), -90), ((x1, y1), (-1, -1), 0),
                       ((x0, y1), (1, -1), 90), ((x0, y0), (1, 1), 180)]
            plate_corner = [i == cols - 1 and j == 0, i == cols - 1 and j == rows - 1,
                            i == 0 and j == rows - 1, i == 0 and j == 0]

            def loop(inset, z):
                r = R_TOP - inset
                pts = []
                for (cx, cy), (dx, dy), a0 in corners:
                    ox, oy = cx + dx * R_TOP, cy + dy * R_TOP   # arc centre
                    for k in range(ARC_SEGS + 1):
                        a = math.radians(a0 + 90 * k / ARC_SEGS)
                        # Snap so neighbouring cells produce bit-identical points.
                        pts.append((round(ox + r * math.cos(a), 6),
                                    round(oy + r * math.sin(a), 6), z))
                return pts

            loops = [loop(d, z) for z, d in PROFILE]
            n = len(loops[0])

            # Socket walls (normals face into the socket).
            for lo, hi in zip(loops, loops[1:]):
                for a in range(n):
                    b = (a + 1) % n
                    tris.append((lo[a], hi[b], lo[b]))
                    tris.append((lo[a], hi[a], hi[b]))

            top = loops[-1]
            bottom = loops[0]
            # Contour each loop point maps to on the cell's outline (z=0).
            Q = []
            for c, ((cx, cy), (dx, dy), a0) in enumerate(corners):
                for k in range(ARC_SEGS + 1):
                    t = top[c * (ARC_SEGS + 1) + k]
                    if plate_corner[c] or k in (0, ARC_SEGS):
                        Q.append((t[0], t[1], 0.0))   # on the r=4 arc / edge
                    else:
                        Q.append((cx, cy, 0.0))       # square cell corner

            # Top: little flat fans between the socket corner arcs and the
            # square cell corner (skipped at the rounded plate corners).
            for c, ((cx, cy), _, _) in enumerate(corners):
                if plate_corner[c]:
                    continue
                C = (cx, cy, HEIGHT)
                arc = top[c * (ARC_SEGS + 1):(c + 1) * (ARC_SEGS + 1)]
                for k in range(ARC_SEGS):
                    flat((C, arc[k], arc[k + 1]), up=True)

            # Bottom: ring between the socket's bottom opening and the cell outline.
            for a in range(n):
                b = (a + 1) % n
                flat((bottom[a], bottom[b], Q[b]), up=False)
                flat((bottom[a], Q[b], Q[a]), up=False)

    # Outer walls: every open edge of the top surface drops straight to z=0.
    directed = set()
    for t in tris:
        for a, b in ((t[0], t[1]), (t[1], t[2]), (t[2], t[0])):
            directed.add((a, b))
    walls = []
    for a, b in directed:
        if a[2] == HEIGHT and b[2] == HEIGHT and (b, a) not in directed:
            ab, bb = (a[0], a[1], 0.0), (b[0], b[1], 0.0)
            walls.append((ab, bb, b))
            walls.append((ab, b, a))
    return tris + walls


def normal(t):
    (ax, ay, az), (bx, by, bz), (cx, cy, cz) = t
    ux, uy, uz = bx - ax, by - ay, bz - az
    vx, vy, vz = cx - ax, cy - ay, cz - az
    nx, ny, nz = uy * vz - uz * vy, uz * vx - ux * vz, ux * vy - uy * vx
    L = math.sqrt(nx * nx + ny * ny + nz * nz) or 1.0
    return nx / L, ny / L, nz / L


def write_stl(path, tris, name):
    with open(path, "wb") as f:
        f.write(name.encode()[:80].ljust(80, b" "))
        f.write(struct.pack("<I", len(tris)))
        for t in tris:
            f.write(struct.pack("<3f", *normal(t)))
            for v in t:
                f.write(struct.pack("<3f", *v))
            f.write(b"\0\0")


def check(tris):
    edges = {}
    key = lambda v: tuple(round(x, 5) for x in v)
    for t in tris:
        for a, b in ((t[0], t[1]), (t[1], t[2]), (t[2], t[0])):
            e = (key(a), key(b))
            edges[e] = edges.get(e, 0) + 1
    bad = sum(1 for (a, b), k in edges.items() if k != 1 or edges.get((b, a)) != 1)
    vol = sum((a[0] * (b[1] * c[2] - b[2] * c[1]) - a[1] * (b[0] * c[2] - b[2] * c[0])
               + a[2] * (b[0] * c[1] - b[1] * c[0])) / 6 for a, b, c in tris)
    V = [v for t in tris for v in t]
    size = [max(v[k] for v in V) - min(v[k] for v in V) for k in range(3)]
    return bad, vol, size


if __name__ == "__main__":
    cols = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    rows = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    out_dir = Path(__file__).parent / "output"
    out_dir.mkdir(exist_ok=True)
    out = Path(sys.argv[3]) if len(sys.argv) > 3 else out_dir / f"gridfinity_baseplate_{cols}x{rows}.stl"
    tris = build(cols, rows)
    write_stl(out, tris, f"Gridfinity baseplate {cols}x{rows}")
    bad, vol, size = check(tris)
    print(f"{out}: {len(tris)} triangles, bad edges {bad}, volume {vol:.1f} mm^3, "
          f"size {size[0]:.2f} x {size[1]:.2f} x {size[2]:.2f} mm")
