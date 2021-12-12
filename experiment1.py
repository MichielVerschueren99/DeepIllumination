import os
import random
import subprocess
from termcolor import cprint
import util as u


def experiment1():

    generate_data("train", 3)
    generate_data("val", 1)
    generate_data("test", 1)

def generate_data(dataset, amount):


    counter = 0

    while counter < amount:
        x_rotation = random.random() * 360
        y_rotation = random.random() * 360
        z_rotation = random.random() * 360

        at = """NamedMaterial "Item"
            Translate 0 1 0
            Rotate {} 1 0 0
            Rotate {} 0 1 0
            Rotate {} 0 0 1
            Shape "cylinder" "float radius" 0.5 "float zmin" -0.25 "float zmax" 0.25 """.format(x_rotation, y_rotation, z_rotation)

        albedo_scene_file_content = u.makePBRT(u.albedoIntegrator(), u.sobolSampler(64), u.triangleFilter(), u.imageFilm("render.png"), u.perspectiveCamera(), u.cornellBoxWorld(at))
        normal_scene_file_content = u.makePBRT(u.normalIntegrator(), u.sobolSampler(64), u.triangleFilter(), u.imageFilm("render.pfm"), u.perspectiveCamera(), u.cornellBoxWorld(at))
        direct_scene_file_content = u.makePBRT(u.directIlluminationIntegrator(), u.sobolSampler(64), u.triangleFilter(), u.imageFilm("render.png"), u.perspectiveCamera(), u.cornellBoxWorld(at))
        depth_scene_file_content = u.makePBRT(u.depthIntegrator(), u.sobolSampler(64), u.triangleFilter(), u.imageFilm("render.pfm"), u.perspectiveCamera(), u.cornellBoxWorld(at))
        gt_scene_file_content = u.makePBRT(u.pathTracingIntegrator(), u.sobolSampler(64), u.triangleFilter(), u.imageFilm("render.png"), u.perspectiveCamera(), u.cornellBoxWorld(at))
        render_and_save_scene(albedo_scene_file_content, "dataset\\experiment1\\{}\\albedo\\{}.png".format(dataset, counter))
        render_and_save_scene(normal_scene_file_content, "dataset\\experiment1\\{}\\normal\\{}.pfm".format(dataset, counter))
        render_and_save_scene(direct_scene_file_content, "dataset\\experiment1\\{}\\direct\\{}.png".format(dataset, counter))
        render_and_save_scene(depth_scene_file_content, "dataset\\experiment1\\{}\\depth\\{}.pfm".format(dataset, counter))
        render_and_save_scene(gt_scene_file_content, "dataset\\experiment1\\{}\\gt\\{}.png".format(dataset, counter))
        counter += 1
        cprint("{}: {}/{} completed".format(dataset, counter, amount), 'green')




def render_and_save_scene(scene_file_content, path):

    scene_file = open("scene.pbrt", "w")
    scene_file.write(scene_file_content)
    scene_file.close()

    print(os.path.abspath("scene.pbrt"))
    subprocess.run(['pbrt', "scene.pbrt"])

    u.put_render_in_location(path)

    os.remove("scene.pbrt")


experiment1()
