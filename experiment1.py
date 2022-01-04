import os
import random
import subprocess
from termcolor import cprint
import util as u

#EXPERIMENT 1: roterende objecten in een cornell box (zie paper)

sphere_train_amount = 70
sphere_val_amount = 30
sphere_test_amount = 0

cylinder_train_amount = 70
cylinder_val_amount = 30
cylinder_test_amount = 0

cube_train_amount = 70
cube_val_amount = 30
cube_test_amount = 0

bunny_train_amount = 70
bunny_val_amount = 30
bunny_test_amount = 0

dragon_train_amount = 70
dragon_val_amount = 30
dragon_test_amount = 0

buddha_train_amount = 0
buddha_val_amount = 0
buddha_test_amount = 20

total_amount = (sphere_train_amount + sphere_val_amount + sphere_test_amount + cylinder_train_amount + cylinder_val_amount
                + cylinder_test_amount + cube_train_amount + cube_val_amount + cube_test_amount + bunny_train_amount + bunny_val_amount
                + bunny_test_amount + dragon_train_amount + dragon_val_amount + dragon_test_amount + buddha_train_amount
                + buddha_val_amount + buddha_test_amount) * 5
amount_done = 0


def experiment1():

    train_counter = 0
    test_counter = 0
    val_counter = 0

    # CYLINDER

    at = """NamedMaterial "Item"
                Translate 0 1 0
                Rotate {} 1 0 0
                Rotate {} 0 1 0
                Rotate {} 0 0 1
                Shape "cylinder" "float radius" 0.5 "float zmin" -0.5 "float zmax" 0.5 """
    train_counter = generate_data("train", at, train_counter, cylinder_train_amount)
    test_counter = generate_data("test", at, test_counter, cylinder_test_amount)
    val_counter = generate_data("val", at, val_counter, cylinder_val_amount)


    # SPHERE

    at = """NamedMaterial "Item"
                Translate 0 1 0
                Rotate {} 1 0 0
                Rotate {} 0 1 0
                Rotate {} 0 0 1
                Shape "sphere" "float radius" 0.5 """
    train_counter = generate_data("train", at, train_counter, sphere_train_amount)
    test_counter = generate_data("test", at, test_counter, sphere_test_amount)
    val_counter = generate_data("val", at, val_counter, sphere_val_amount)


    # CUBE

    at = """NamedMaterial "Item"
                Translate 0 1 0
                Rotate {} 1 0 0
                Rotate {} 0 1 0
                Rotate {} 0 0 1
                Translate 0 -0.5 0
                Scale 0.3 0.3 0.3
                Shape "plymesh" "string filename" "\\meshes\\\\cube.ply" """
    train_counter = generate_data("train", at, train_counter, cube_train_amount)
    test_counter = generate_data("test", at, test_counter, cube_test_amount)
    val_counter = generate_data("val", at, val_counter, cube_val_amount)


    #BUNNY

    at = """NamedMaterial "Item"
                Translate 0 1 0
                Rotate {} 1 0 0
                Rotate {} 0 1 0
                Rotate {} 0 0 1
                Translate 0 -0.5 0
                Scale 0.75 0.75 0.75
                Shape "plymesh" "string filename" "\\meshes\\\\bunny.ply" """
    train_counter = generate_data("train", at, train_counter, bunny_train_amount)
    test_counter = generate_data("test", at, test_counter, bunny_test_amount)
    val_counter = generate_data("val", at, val_counter, bunny_val_amount)


    # DRAGON

    at = """NamedMaterial "Item"
                Translate 0 1 0
                Rotate {} 1 0 0
                Rotate {} 0 1 0
                Rotate {} 0 0 1
                Translate 0 -0.5 0
                Scale 0.75 0.75 0.75
                Shape "plymesh" "string filename" "\\meshes\\\\dragon.ply" """
    train_counter = generate_data("train", at, train_counter, dragon_train_amount)
    test_counter = generate_data("test", at, test_counter, dragon_test_amount)
    val_counter = generate_data("val", at, val_counter, dragon_val_amount)


    # BUDDHA

    at = """NamedMaterial "Item"
                    Translate 0 1 0
                    Rotate {} 1 0 0
                    Rotate {} 0 1 0
                    Rotate {} 0 0 1
                    Translate 0 -0.5 0
                    Scale 0.75 0.75 0.75
                    Shape "plymesh" "string filename" "\\meshes\\\\buddha.ply" """
    train_counter = generate_data("train", at, train_counter, buddha_train_amount)
    test_counter = generate_data("test", at, test_counter, buddha_test_amount)
    val_counter = generate_data("val", at, val_counter, buddha_val_amount)



def generate_data(dataset, at_template, name, amount):

    counter = 0
    while counter < amount:
        x_rotation = random.random() * 360
        y_rotation = random.random() * 360
        z_rotation = random.random() * 360
        at = at_template.format(x_rotation, y_rotation, z_rotation)

        albedo_scene_file_content = u.makePBRT(u.albedoIntegrator(), u.sobolSampler(64), u.triangleFilter(), u.imageFilm("render.png"), u.perspectiveCamera(), u.cornellBoxWorld(at))
        normal_scene_file_content = u.makePBRT(u.normalIntegrator(), u.sobolSampler(64), u.triangleFilter(), u.imageFilm("render.pfm"), u.perspectiveCamera(), u.cornellBoxWorld(at))
        direct_scene_file_content = u.makePBRT(u.directIlluminationIntegrator(), u.sobolSampler(64), u.triangleFilter(), u.imageFilm("render.png"), u.perspectiveCamera(), u.cornellBoxWorld(at))
        depth_scene_file_content = u.makePBRT(u.depthIntegrator(), u.sobolSampler(64), u.triangleFilter(), u.imageFilm("render.pfm"), u.perspectiveCamera(), u.cornellBoxWorld(at))
        gt_scene_file_content = u.makePBRT(u.pathTracingIntegrator(), u.sobolSampler(512), u.triangleFilter(), u.imageFilm("render.png"), u.perspectiveCamera(), u.cornellBoxWorld(at))
        render_and_save_scene(albedo_scene_file_content, "dataset\\experiment1\\{}\\albedo\\{}.png".format(dataset, name))
        render_and_save_scene(normal_scene_file_content, "dataset\\experiment1\\{}\\normal\\{}.pfm".format(dataset, name))
        render_and_save_scene(direct_scene_file_content, "dataset\\experiment1\\{}\\direct\\{}.png".format(dataset, name))
        render_and_save_scene(depth_scene_file_content, "dataset\\experiment1\\{}\\depth\\{}.pfm".format(dataset, name))
        render_and_save_scene(gt_scene_file_content, "dataset\\experiment1\\{}\\gt\\{}.png".format(dataset, name))
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


experiment1()
