#!/usr/bin/env python
"""confluence_hsu: monolithic + 4-part decomposed transfinite meshes.

Geometry after Hsu, Lee & Chang (1998): equal-width subcritical junction,
W = 0.155 m, junction angle theta (default 30 deg), branch merging concordant.

Blocks (all transfinite quads, shared node counts => the part meshes are
CONFORMING sub-meshes of the full mesh; cuts are mesh lines):

  [A up-far][B up-near][C span][D down-near][E down-far]
                          /F branch-near
                         /G branch-far

Parts: inflow_main = A | junction = B+C+D+F | outflow = E | inflow_branch = G
Interfaces: coupling_main (A|B), coupling_out (D|E), coupling_branch (G|F).

Usage: python generate.py [angle_deg] [size_factor]
"""
import sys, math
import gmsh

TH = float(sys.argv[1]) if len(sys.argv) > 1 else 30.0
SF = float(sys.argv[2]) if len(sys.argv) > 2 else 1.0

W    = 0.155
th   = math.radians(TH)
l1   = 2.0                 # upstream main length
l2   = W / math.sin(th)    # junction span
l3   = 3.0                 # downstream main length
lb   = 1.5                 # branch length (along axis)
dcut = 0.5                 # cut-back of main arms from the junction (~3 W)
dbc  = 0.5                 # cut-back of the branch (along axis)
dx   = 0.02 / SF           # target cell size

def N(l): return max(2, round(l / dx) + 1)
NW = round(12 * SF) + 1                       # across main width
NJ = N(l2)                                    # junction span / branch cross
ex, ey = -math.cos(th), -math.sin(th)         # branch axis (away from junction)

# corner points (x, y)
P = {
 1:(0,0), 2:(0,W),                                     # main inlet
 3:(l1-dcut,W), 4:(l1-dcut,0),                          # cut A|B
 5:(l1,0), 6:(l1,W),                                    # junction start
 7:(l1+l2,0), 8:(l1+l2,W),                              # junction end
 9:(l1+l2+dcut,0), 10:(l1+l2+dcut,W),                   # cut D|E
 11:(l1+l2+l3,0), 12:(l1+l2+l3,W),                      # outlet
 13:(l1+dbc*ex,      dbc*ey), 14:(l1+l2+dbc*ex, dbc*ey),# cut F|G
 15:(l1+lb*ex,       lb*ey),  16:(l1+l2+lb*ex,  lb*ey), # branch inlet
}
# blocks: (corner ids ccw: bl, br, tr, tl), (Nx along flow, Ny across)
BLOCKS = {
 "A": ((1,4,3,2),   (N(l1-dcut), NW)),
 "B": ((4,5,6,3),   (N(dcut),    NW)),
 "C": ((5,7,8,6),   (NJ,         NW)),
 "D": ((7,9,10,8),  (N(dcut),    NW)),
 "E": ((9,11,12,10),(N(l3-dcut), NW)),
 "F": ((13,14,7,5), (NJ,   N(dbc))),
 "G": ((15,16,14,13),(NJ,  N(lb-dbc))),
}
PARTS = {
 "full":          ["A","B","C","D","E","F","G"],
 "inflow_main":   ["A"],
 "junction":      ["B","C","D","F"],
 "outflow":       ["E"],
 "inflow_branch": ["G"],
}
# physical boundary edges per part: name -> list of (block, edge) with
# edge = 0 bottom(bl-br), 1 right(br-tr), 2 top(tr-tl), 3 left(tl-bl)
def edges_for(part):
    E = {"wall": []}
    def add(name, be):
        E.setdefault(name, []).append(be)
    if part in ("full", "inflow_main"):
        add("inflow_main", ("A",3))
    if part in ("full", "inflow_branch"):
        add("inflow_branch", ("G",0))
    if part in ("full", "outflow"):
        add("outflow", ("E",1))
    walls = {
      "full": [("A",0),("A",2),("B",2),("C",2),("D",2),("E",2),("B",0),("D",0),("E",0),
               ("F",3),("F",1),("G",3),("G",1)],
      "inflow_main":  [("A",0),("A",2)],
      "outflow":      [("E",0),("E",2)],
      "inflow_branch":[("G",3),("G",1)],
      "junction":     [("B",2),("C",2),("D",2),("B",0),("D",0),("F",3),("F",1)],
    }[part]
    for be in walls: add("wall", be)
    cuts = {
      "inflow_main":  [("coupling_main",  ("A",1))],
      "outflow":      [("coupling_out",   ("E",3))],
      "inflow_branch":[("coupling_branch",("G",2))],
      "junction":     [("coupling_main",  ("B",3)),
                       ("coupling_out",   ("D",1)),
                       ("coupling_branch",("F",0))],
      "full": [],
    }[part]
    for name, be in cuts: add(name, be)
    return E

for part, blocks in PARTS.items():
    gmsh.initialize()
    gmsh.option.setNumber("General.Terminal", 0)
    gmsh.model.add(part)
    pt = {}   # point id per corner
    for b in blocks:
        for c in BLOCKS[b][0]:
            if c not in pt:
                x, y = P[c]
                pt[c] = gmsh.model.geo.addPoint(x, y, 0)
    ln = {}   # line id per (corner, corner), shared between blocks
    def line(a, b_):
        if (a,b_) in ln: return ln[(a,b_)]
        if (b_,a) in ln: return -ln[(b_,a)]
        ln[(a,b_)] = gmsh.model.geo.addLine(pt[a], pt[b_])
        return ln[(a,b_)]
    surf = {}
    for b in blocks:
        (bl,br,tr,tl),(nx,ny) = BLOCKS[b]
        e0,e1,e2,e3 = line(bl,br), line(br,tr), line(tr,tl), line(tl,bl)
        cl = gmsh.model.geo.addCurveLoop([e0,e1,e2,e3])
        surf[b] = gmsh.model.geo.addPlaneSurface([cl])
        for e,n in ((e0,nx),(e2,nx),(e1,ny),(e3,ny)):
            gmsh.model.geo.mesh.setTransfiniteCurve(abs(e), n)
        gmsh.model.geo.mesh.setTransfiniteSurface(surf[b])
        gmsh.model.geo.mesh.setRecombine(2, surf[b])
    gmsh.model.geo.synchronize()
    EDGE = {0:(0,1),1:(1,2),2:(2,3),3:(3,0)}
    # ALPHABETICAL physical-group creation: the jax mesh loader numbers
    # boundary functions by ascending physical id while the core BC container
    # sorts tags by name — creation order must be alphabetical or the BC↔patch
    # pairing silently permutes (outflow became a wall).
    for name, bes in sorted(edges_for(part).items()):
        ids = []
        for b, e in bes:
            cs = BLOCKS[b][0]; i,j = EDGE[e]
            ids.append(abs(line(cs[i], cs[j])))
        gmsh.model.addPhysicalGroup(1, ids, name=name)
    gmsh.model.addPhysicalGroup(2, list(surf.values()), name="domain")
    gmsh.model.mesh.generate(2)
    gmsh.option.setNumber("Mesh.MshFileVersion", 2.2)
    out = f"mesh_2d.msh" if part == "full" else f"part_{part}.msh"
    import os
    here = os.path.dirname(os.path.abspath(__file__))
    gmsh.write(os.path.join(here, out))
    nn = len(gmsh.model.mesh.getNodes()[0])
    print(f"{part:14s} -> {out:22s} {nn} nodes")

    # extruded one-layer volume mesh for OpenFOAM (gmshToFoam; front/back -> empty)
    gmsh.model.geo.synchronize()
    HZ = 0.1
    ext = gmsh.model.geo.extrude(
        [(2, s) for s in surf.values()], 0, 0, HZ,
        numElements=[1], recombine=True)
    gmsh.model.geo.synchronize()
    gmsh.model.removePhysicalGroups([])   # 2-D groups; re-added as surfaces below
    # extrude() returns per input surface: [top, volume, side per boundary edge...]
    tops, vols = [], []
    side_of = {}          # abs(line id) -> lateral surface tag
    i = 0
    for b in blocks:
        top, vol = ext[i][1], ext[i+1][1]
        tops.append(top); vols.append(vol)
        cs = BLOCKS[b][0]
        for k in range(4):
            e = abs(line(cs[EDGE[k][0]], cs[EDGE[k][1]]))
            side_of.setdefault(e, ext[i+2+k][1])
        i += 6
    for name, bes in sorted(edges_for(part).items()):
        ids = [side_of[abs(line(BLOCKS[b][0][EDGE[e][0]], BLOCKS[b][0][EDGE[e][1]]))]
               for b, e in bes]
        gmsh.model.addPhysicalGroup(2, ids, name=name)
    gmsh.model.addPhysicalGroup(2, list(surf.values()), name="back")
    gmsh.model.addPhysicalGroup(2, tops, name="front")
    gmsh.model.addPhysicalGroup(3, vols, name="domain")
    gmsh.model.mesh.generate(3)
    out3 = "mesh_3d.msh" if part == "full" else f"part_{part}_3d.msh"
    gmsh.write(os.path.join(here, out3))
    print(f"{part:14s} -> {out3}")
    gmsh.finalize()

# ── VOF variant: full mesh extruded with resolved vertical layers ───────────
# (separate gmsh model: N_LAYER-layer extrusion to H_DOM; groups: bottom,
#  atmosphere (top), wall (sides), inflow_main/inflow_branch/outflow)
H_DOM, N_LAYER = 0.20, 24
gmsh.initialize()
gmsh.option.setNumber("General.Terminal", 0)
gmsh.model.add("vof")
pt, ln = {}, {}
def line(a, b_):
    if (a, b_) in ln: return ln[(a, b_)]
    if (b_, a) in ln: return -ln[(b_, a)]
    ln[(a, b_)] = gmsh.model.geo.addLine(pt[a], pt[b_])
    return ln[(a, b_)]
blocks = PARTS["full"]
for b in blocks:
    for c in BLOCKS[b][0]:
        if c not in pt:
            x, y = P[c]
            pt[c] = gmsh.model.geo.addPoint(x, y, 0)
surf = {}
EDGE = {0:(0,1),1:(1,2),2:(2,3),3:(3,0)}
for b in blocks:
    (bl,br,tr,tl),(nx,ny) = BLOCKS[b]
    e0,e1,e2,e3 = line(bl,br), line(br,tr), line(tr,tl), line(tl,bl)
    cl = gmsh.model.geo.addCurveLoop([e0,e1,e2,e3])
    surf[b] = gmsh.model.geo.addPlaneSurface([cl])
    for e,n in ((e0,nx),(e2,nx),(e1,ny),(e3,ny)):
        gmsh.model.geo.mesh.setTransfiniteCurve(abs(e), n)
    gmsh.model.geo.mesh.setTransfiniteSurface(surf[b])
    gmsh.model.geo.mesh.setRecombine(2, surf[b])
gmsh.model.geo.synchronize()
ext = gmsh.model.geo.extrude([(2, s) for s in surf.values()], 0, 0, H_DOM,
                             numElements=[N_LAYER], recombine=True)
gmsh.model.geo.synchronize()
tops, vols, side_of = [], [], {}
i = 0
for b in blocks:
    tops.append(ext[i][1]); vols.append(ext[i+1][1])
    cs = BLOCKS[b][0]
    for k in range(4):
        e = abs(line(cs[EDGE[k][0]], cs[EDGE[k][1]]))
        side_of.setdefault(e, ext[i+2+k][1])
    i += 6
for name, bes in sorted(edges_for("full").items()):
    ids = [side_of[abs(line(BLOCKS[b][0][EDGE[e][0]], BLOCKS[b][0][EDGE[e][1]]))]
           for b, e in bes]
    gmsh.model.addPhysicalGroup(2, ids, name=name)
gmsh.model.addPhysicalGroup(2, list(surf.values()), name="bottom")
gmsh.model.addPhysicalGroup(2, tops, name="atmosphere")
gmsh.model.addPhysicalGroup(3, vols, name="domain")
gmsh.model.mesh.generate(3)
gmsh.option.setNumber("Mesh.MshFileVersion", 2.2)
import os as _os
gmsh.write(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "mesh_vof.msh"))
nn = len(gmsh.model.mesh.getNodes()[0])
print(f"vof            -> mesh_vof.msh          {nn} nodes "
      f"({N_LAYER} layers to z={H_DOM})")
gmsh.finalize()
