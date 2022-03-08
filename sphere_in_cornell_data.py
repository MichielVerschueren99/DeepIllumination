import os
import random
import subprocess
from termcolor import cprint
import util as u

#bol op random locatie in cornell box

sphere_train_amount = 7
sphere_val_amount = 2
sphere_test_amount = 1

write_location = "/home/r0705259/Thesis/trainingdata/"


def sphere_in_cornell_data():

    # SPHERE

    at = """NamedMaterial "Item"
                Translate {} {} 0
                Shape "sphere" "float radius" 0.4 """
    generate_data("train", at, sphere_train_amount)
    generate_data("test", at, sphere_test_amount)
    generate_data("val", at, sphere_val_amount)

def generate_data(dataset, at_template, amount):

    name = 0

    counter = 0
    while counter < amount:
        x_position = random.random() - 0.5
        y_position = random.random() * 0.8 + 0.4
        at = at_template.format(x_position, y_position)

        albedo_name = "{}_albedo_{}".format(dataset, name)
        normal_name = "{}_normal_{}".format(dataset, name)
        direct_name = "{}_direct_{}".format(dataset, name)
        depth_name = "{}_depth_{}".format(dataset, name)
        gt_name = "{}_gt_{}".format(dataset, name)

        albedo_scene_file_content = u.makePBRT(u.albedoIntegrator(), u.sobolSampler(64), u.triangleFilter(), u.imageFilm(albedo_name + ".png"), u.perspectiveCamera(), u.cornellBoxWorld(at))
        normal_scene_file_content = u.makePBRT(u.normalIntegrator(), u.sobolSampler(64), u.triangleFilter(), u.imageFilm(normal_name + ".pfm"), u.perspectiveCamera(), u.cornellBoxWorld(at))
        direct_scene_file_content = u.makePBRT(u.directIlluminationIntegrator(), u.sobolSampler(64), u.triangleFilter(), u.imageFilm(direct_name + ".png"), u.perspectiveCamera(), u.cornellBoxWorld(at))
        depth_scene_file_content = u.makePBRT(u.depthIntegrator(), u.sobolSampler(64), u.triangleFilter(), u.imageFilm(depth_name + ".pfm"), u.perspectiveCamera(), u.cornellBoxWorld(at))
        gt_scene_file_content = u.makePBRT(u.pathTracingIntegrator(), u.sobolSampler(512), u.triangleFilter(), u.imageFilm(gt_name + ".png"), u.perspectiveCamera(), u.cornellBoxWorld(at))
        save_scene_file(albedo_scene_file_content, "scenefiles\\sphere_in_cornell\\" + albedo_name + ".pbrt")
        save_scene_file(normal_scene_file_content, "scenefiles\\sphere_in_cornell\\" + normal_name + ".pbrt")
        save_scene_file(direct_scene_file_content, "scenefiles\\sphere_in_cornell\\" + direct_name + ".pbrt")
        save_scene_file(depth_scene_file_content, "scenefiles\\sphere_in_cornell\\" + depth_name + ".pbrt")
        save_scene_file(gt_scene_file_content, "scenefiles\\sphere_in_cornell\\" + gt_name + ".pbrt")
        counter += 1
        name += 1


def save_scene_file(scene_file_content, path):

    scene_file = open("scene.pbrt", "w")
    scene_file.write(scene_file_content)
    scene_file.close()

    if os.path.exists(path):
        os.remove(path)
    os.rename(os.path.abspath("scene.pbrt"), path)


sphere_in_cornell_data()
