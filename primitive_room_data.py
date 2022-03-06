import os
import random
import subprocess
from termcolor import cprint
import util as u

train_amount = 70
val_amount = 0
test_amount = 0

write_location = "/home/r0705259/Thesis/trainingdata/"

def primitive_room():

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

    counter = 0
    per_dataset_counter = 0
    dataset = "train"
    while counter < train_amount:

        if counter == train_amount:
            dataset = "test"
            per_dataset_counter = 0
        if counter == train_amount + test_amount:
            dataset = "val"
            per_dataset_counter = 0
        back_wall_rgb = u.generate_random_list(0, 1, 3)
        left_wall_rgb = u.generate_random_list(0, 1, 3)
        right_wall_rgb = u.generate_random_list(0, 1, 3)
        front_wall_rgb = u.generate_random_list(0, 1, 3)
        world = u.emptyPrimitiveRoom(back_wall_rgb, right_wall_rgb, front_wall_rgb, left_wall_rgb)

        object_locations = u.generate_random_xz_locations(-0.9, 0.9, 0.2, 12)

        world = add_object(cylinder_template, object_locations[0], world)
        world = add_object(cylinder_template, object_locations[1], world)
        world = add_object(cylinder_template, object_locations[2], world)
        world = add_object(cylinder_template, object_locations[3], world)
        world = add_object(cylinder_template, object_locations[4], world)
        world = add_object(cylinder_template, object_locations[5], world)
        world = add_object(sphere_template, object_locations[6], world)
        world = add_object(sphere_template, object_locations[7], world)
        world = add_object(sphere_template, object_locations[8], world)
        world = add_object(sphere_template, object_locations[9], world)
        world = add_object(sphere_template, object_locations[10], world)
        world = add_object(sphere_template, object_locations[11], world)

        world = world + '\n' + u.cornellBoxLight()

        camera_position = u.generate_random_list(-0.9, 0.9, 3)
        camera_position[1] = 0.4

        camera = u.lookAtPerspectiveCamera(camera_position, [0, 0, 0], u.generate_random_list(0, 1, 3), 45)

        generate_data(dataset, camera, world, per_dataset_counter)

        per_dataset_counter += 1
        counter += 1



def add_object(object_template, location, world):
    rgb = u.generate_random_list(0, 1, 3)
    world = world + '\n' + object_template.format(rgb[0], rgb[1], rgb[2], location[0], location[1])
    return world

def generate_data(dataset, camera, world, name):
    albedo_name = "{}_albedo_{}".format(dataset, name)
    normal_name = "{}_normal_{}".format(dataset, name)
    direct_name = "{}_direct_{}".format(dataset, name)
    depth_name = "{}_depth_{}".format(dataset, name)
    gt_name = "{}_gt_{}".format(dataset, name)

    albedo_scene_file_content = u.makePBRT(u.albedoIntegrator(), u.sobolSampler(64), u.triangleFilter(),
                                           u.imageFilm(write_location + albedo_name + ".png"), camera, world)
    normal_scene_file_content = u.makePBRT(u.normalIntegrator(), u.sobolSampler(64), u.triangleFilter(),
                                           u.imageFilm(write_location + normal_name + ".pfm"), camera, world)
    direct_scene_file_content = u.makePBRT(u.directIlluminationIntegrator(), u.sobolSampler(64), u.triangleFilter(),
                                           u.imageFilm(write_location + direct_name + ".png"), camera, world)
    depth_scene_file_content = u.makePBRT(u.depthIntegrator(), u.sobolSampler(64), u.triangleFilter(),
                                          u.imageFilm(write_location + depth_name + ".pfm"), camera, world)
    gt_scene_file_content = u.makePBRT(u.pathTracingIntegrator(), u.sobolSampler(512), u.triangleFilter(),
                                       u.imageFilm(write_location + gt_name + ".png"), camera, world)
    save_scene_file(albedo_scene_file_content, "scenefiles\\primitive_room\\" + albedo_name + ".pbrt")
    save_scene_file(normal_scene_file_content, "scenefiles\\primitive_room\\" + normal_name + ".pbrt")
    save_scene_file(direct_scene_file_content, "scenefiles\\primitive_room\\" + direct_name + ".pbrt")
    save_scene_file(depth_scene_file_content, "scenefiles\\primitive_room\\" + depth_name + ".pbrt")
    save_scene_file(gt_scene_file_content, "scenefiles\\primitive_room\\" + gt_name + ".pbrt")


def save_scene_file(scene_file_content, path):

    scene_file = open("scene.pbrt", "w")
    scene_file.write(scene_file_content)
    scene_file.close()

    if os.path.exists(path):
        os.remove(path)
    os.rename(os.path.abspath("scene.pbrt"), path)


primitive_room()
