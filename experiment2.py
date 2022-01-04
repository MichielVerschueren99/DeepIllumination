import os
import random
import subprocess
from termcolor import cprint
import util as u

#EXPERIMENT 2: roterende buddha animatie

buddha_train_amount = 0
buddha_val_amount = 0
buddha_test_amount = 4

total_amount = (buddha_train_amount
                + buddha_val_amount + buddha_test_amount) * 5
amount_done = 0


def experiment2():

    test_counter = 0

    # BUDDHA

    at = """NamedMaterial "Item"
                    Translate 0 1 0
                    Rotate {} 0 1 0
                    Rotate 45 0 0 1
                    Translate 0 -0.5 0
                    Scale 0.75 0.75 0.75
                    Shape "plymesh" "string filename" "\\meshes\\\\buddha.ply" """
    test_counter = generate_data("test", at, test_counter, buddha_test_amount)



def generate_data(dataset, at_template, name, amount):

    counter = 0
    while counter < amount:
        y_rotation = counter * 10
        at = at_template.format(y_rotation)

        albedo_scene_file_content = u.makePBRT(u.albedoIntegrator(), u.sobolSampler(64), u.triangleFilter(), u.imageFilm("render.png"), u.perspectiveCamera(), u.cornellBoxWorld(at))
        normal_scene_file_content = u.makePBRT(u.normalIntegrator(), u.sobolSampler(64), u.triangleFilter(), u.imageFilm("render.pfm"), u.perspectiveCamera(), u.cornellBoxWorld(at))
        direct_scene_file_content = u.makePBRT(u.directIlluminationIntegrator(), u.sobolSampler(64), u.triangleFilter(), u.imageFilm("render.png"), u.perspectiveCamera(), u.cornellBoxWorld(at))
        depth_scene_file_content = u.makePBRT(u.depthIntegrator(), u.sobolSampler(64), u.triangleFilter(), u.imageFilm("render.pfm"), u.perspectiveCamera(), u.cornellBoxWorld(at))
        gt_scene_file_content = u.makePBRT(u.pathTracingIntegrator(), u.sobolSampler(512), u.triangleFilter(), u.imageFilm("render.png"), u.perspectiveCamera(), u.cornellBoxWorld(at))
#        render_and_save_scene(albedo_scene_file_content, "dataset\\experiment2\\{}\\albedo\\{}.png".format(dataset, name))
#        render_and_save_scene(normal_scene_file_content, "dataset\\experiment2\\{}\\normal\\{}.pfm".format(dataset, name))
        render_and_save_scene(direct_scene_file_content, "dataset\\experiment2\\{}\\direct\\{}.png".format(dataset, name))
#        render_and_save_scene(depth_scene_file_content, "dataset\\experiment2\\{}\\depth\\{}.pfm".format(dataset, name))
#        render_and_save_scene(gt_scene_file_content, "dataset\\experiment2\\{}\\gt\\{}.png".format(dataset, name))
        counter += 1
        name += 1
    return name


def render_and_save_scene(scene_file_content, path):

    scene_file = open("scene.pbrt", "w")
    scene_file.write(scene_file_content)
    scene_file.close()

    print(os.path.abspath("scene.pbrt"))
    subprocess.run(['pbrt', "scene.pbrt"])

    global amount_done
    amount_done = amount_done + 1
    cprint("{}/{} renders completed".format(amount_done, total_amount), 'green')

    u.put_render_in_location(path)

    os.remove("scene.pbrt")


experiment2()
