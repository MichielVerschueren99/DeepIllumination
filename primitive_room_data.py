import os
import random
import subprocess
from termcolor import cprint
import util as u

train_amount = 2
val_amount = 0
test_amount = 0

total_amount = (train_amount + val_amount + test_amount) * 5
amount_done = 0


def primitive_room():

    train_counter = 0
    test_counter = 0
    val_counter = 0

    # CYLINDER
    cylinder_template = """AttributeBegin
		Material "matte" "rgb Kd" [{} {} {}]
		Translate {} 0 {}
		Rotate -90 1 0 0
		Shape "cylinder" "float radius" 0.1 "float zmin" 0 "float zmax" 0.2
	AttributeEnd"""

    # SPHERE
    sphere_template = """AttributeBegin
		Material "matte" "rgb Kd" [{} {} {}]
		Translate {} 0.1 {}
		Shape "sphere" "float radius" 0.1
	AttributeEnd"""

    # CUBE
    cube_template = """AttributeBegin
		Material "matte" "rgb Kd" [{} {} {}]
		Translate {} 0 {}
		Scale 0.1 0.2 0.1
		Shape "plymesh" "string filename" "\\meshes\\cube.ply"
	AttributeEnd"""

    # BUNNY
    bunny_template = """AttributeBegin
		Material "matte" "rgb Kd" [{} {} {}]
		Translate {} 0 {}
		Scale 0.2 0.2 0.2
		Shape "plymesh" "string filename" "\\meshes\\\\bunny.ply"
	AttributeEnd"""

    # ICOSAHEDRON
    icos_template = """AttributeBegin
		Material "matte" "rgb Kd" [{} {} {}]
		Translate {} 0 {}
		Scale 0.2 0.2 0.2
		Shape "plymesh" "string filename" "\\meshes\\\\icosahedron.ply"
	AttributeEnd"""

    # DRAGON
    dragon_template = """AttributeBegin
		Material "matte" "rgb Kd" [{} {} {}]
		Translate {} 0 {}
		Scale 0.3 0.3 0.3
		Shape "plymesh" "string filename" "\\meshes\\dragon.ply"
	AttributeEnd"""


    while train_counter < train_amount:
        back_wall_rgb = u.generate_random_list(0, 1, 3)
        left_wall_rgb = u.generate_random_list(0, 1, 3)
        right_wall_rgb = u.generate_random_list(0, 1, 3)
        front_wall_rgb = u.generate_random_list(0, 1, 3)
        world = u.emptyPrimitiveRoom(back_wall_rgb, right_wall_rgb, front_wall_rgb, left_wall_rgb)

        object_locations = u.generate_random_xz_locations(-0.9, 0.9, 0.2, 6)

        world = add_object(cylinder_template, object_locations[0], world)
        world = add_object(cube_template, object_locations[1], world)
        world = add_object(bunny_template, object_locations[2], world)
        world = add_object(icos_template, object_locations[3], world)
        world = add_object(dragon_template, object_locations[4], world)
        world = add_object(sphere_template, object_locations[5], world)

        generate_data('train', world, train_counter)



def add_object(object_template, location,world):
    rgb = u.generate_random_list(0, 1, 3)
    world = world + '\n' + object_template.format(rgb[0], rgb[1], rgb[2], location[0], location[1])
    return world

def generate_data(dataset, camera, world, name):

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


primitive_room()
