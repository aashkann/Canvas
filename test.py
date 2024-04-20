import pyradiance as pr


scene = pr.Scene("Scene")
scene.add_material("materials.mat")
scene.add_surface("terrain.rad")
scene.add_surface("design.rad")
scene.add_surface("context.rad")
#print(meshes)

scene.add_source("sky.rad")

octree = pr.oconv("materials.mat", "terrain.rad", "design", "context.rad")
with open("office.oct", "wb") as wtr:
    wtr.write(octree)
pr.rtrace(b"1 1 1 0 0 1", "office.oct", header=False, params=["-I", "-ab", "1"])

