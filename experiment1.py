import os
import subprocess

import util as u


def experiment1():


    at = """NamedMaterial "Item"
		Translate 0 1 0
		Rotate 45 1 0 0
		Shape "sphere" "float radius" 0.5"""

    scene_file_content = u.makePBRT(u.depthIntegrator(), u.sobolSampler(64), u.triangleFilter(), u.imageFilm("render.png"), u.perspectiveCamera(), u.cornellBoxWorld(at))

    scene_file = open("scene.pbrt", "w")
    scene_file.write(scene_file_content)
    print(os.path.abspath("scene.pbrt"))
    subprocess.run(['pbrt', os.path.abspath("scene.pbrt")])

    os.rename("C:\\Users\\Michi\\render.png", "dataset\\experiment1\\1.png")

    os.remove("scene.pbrt")


experiment1()
