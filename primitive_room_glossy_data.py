import os
import random
import subprocess
from termcolor import cprint
import util as u

train_amount = 2000
val_amount = 500
test_amount = 30

write_location = "/home/r0705259/Thesis/trainingdata/"

def primitive_room():

    # CYLINDER
    cylinder_template = """AttributeBegin
    		Material "matte" "rgb Kd" [{} {} {}]
    		Translate {} 0 {}
    		Rotate {} 0 1 0
    		Rotate -90 1 0 0
    		Shape "cylinder" "float radius" 0.1 "float zmin" 0 "float zmax" 0.2
    	AttributeEnd"""

    # SPHERE
    sphere_template = """AttributeBegin
    		Material "matte" "rgb Kd" [{} {} {}]
    		Translate {} 0.1 {}
    		Rotate {} 0 1 0
    		Shape "sphere" "float radius" 0.1
    	AttributeEnd"""

    # DODECAHEDRON
    dodecahedron_template = """AttributeBegin
    		Material "matte" "rgb Kd" [{} {} {}]
    		Translate {} 0 {}
    		Scale 0.1 0.1 0.1
    		Rotate {} 0 1 0
    		Shape "plymesh" "string filename" "/home/r0705259/Thesis/meshes/dodecahedron.ply"
    	AttributeEnd"""

    # BUNNY
    bunny_template = """AttributeBegin
    		Material "matte" "rgb Kd" [{} {} {}]
    		Translate {} 0 {}
    		Scale 0.15 0.15 0.15
    		Rotate {} 0 1 0
    		Shape "plymesh" "string filename" "/home/r0705259/Thesis/meshes/bunny.ply"
    	AttributeEnd"""

    # TEAPOT
    teapot_template = """AttributeBegin
    		Material "matte" "rgb Kd" [{} {} {}]
    		Translate {} 0 {}
    		Scale 0.17 0.17 0.17
    		Rotate {} 0 1 0
    		Shape "plymesh" "string filename" "/home/r0705259/Thesis/meshes/teapot.ply"
    	AttributeEnd"""

    # CYLINDER
    glossy_cylinder_template = """AttributeBegin
    		Material "plastic" "rgb Kd" [0 0 0] "rgb Ks" [{} {} {}] "float roughness" [ {} ]
    		Translate {} 0 {}
    		Rotate {} 0 1 0
    		Rotate -90 1 0 0
    		Shape "cylinder" "float radius" 0.1 "float zmin" 0 "float zmax" 0.2
    	AttributeEnd"""

    # SPHERE
    glossy_sphere_template = """AttributeBegin
    		Material "plastic" "rgb Kd" [0 0 0] "rgb Ks" [{} {} {}] "float roughness" [ {} ]
    		Translate {} 0.1 {}
    		Rotate {} 0 1 0
    		Shape "sphere" "float radius" 0.1
    	AttributeEnd"""

    # DODECAHEDRON
    glossy_dodecahedron_template = """AttributeBegin
		Material "plastic" "rgb Kd" [0 0 0] "rgb Ks" [{} {} {}] "float roughness" [ {} ]
		Translate {} 0 {}
		Scale 0.1 0.1 0.1
		Rotate {} 0 1 0
		Shape "plymesh" "string filename" "/home/r0705259/Thesis/meshes/dodecahedron.ply"
	AttributeEnd""" # "/home/r0705259/Thesis/meshes/dodecahedron.ply"

    # BUNNY
    glossy_bunny_template = """AttributeBegin
		Material "plastic" "rgb Kd" [0 0 0] "rgb Ks" [{} {} {}] "float roughness" [ {} ]
		Translate {} 0 {}
		Scale 0.15 0.15 0.15
		Rotate {} 0 1 0
		Shape "plymesh" "string filename" "/home/r0705259/Thesis/meshes/bunny.ply"
	AttributeEnd""" # "/home/r0705259/Thesis/meshes/bunny.ply"

    # TEAPOT
    glossy_teapot_template = """AttributeBegin
		Material "plastic" "rgb Kd" [0 0 0] "rgb Ks" [{} {} {}] "float roughness" [ {} ]
		Translate {} 0 {}
		Scale 0.17 0.17 0.17
		Rotate {} 0 1 0
		Shape "plymesh" "string filename" "/home/r0705259/Thesis/meshes/teapot.ply"
	AttributeEnd""" # "/home/r0705259/Thesis/meshes/teapot.ply"

    counter = 0
    per_dataset_counter = 0
    dataset = "train"
    while counter < train_amount + test_amount + val_amount:

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

        object_locations = u.generate_random_xz_locations(-0.9, 0.9, 0.2, 20)

        object_rotations = u.generate_random_list(0, 360, 20)

        world = add_glossy_object(glossy_cylinder_template, object_locations[1], object_rotations[1], world)
        world = add_glossy_object(glossy_cylinder_template, object_locations[2], object_rotations[2], world)
        world = add_glossy_object(glossy_cylinder_template, object_locations[3], object_rotations[3], world)

        world = add_glossy_object(glossy_sphere_template, object_locations[5], object_rotations[5], world)
        world = add_glossy_object(glossy_sphere_template, object_locations[6], object_rotations[6], world)
        world = add_glossy_object(glossy_sphere_template, object_locations[7], object_rotations[7], world)

        world = add_glossy_object(glossy_dodecahedron_template, object_locations[9], object_rotations[9], world)
        world = add_glossy_object(glossy_dodecahedron_template, object_locations[10], object_rotations[10], world)
        world = add_glossy_object(glossy_dodecahedron_template, object_locations[11], object_rotations[11], world)

        world = add_glossy_object(glossy_bunny_template, object_locations[13], object_rotations[13], world)
        world = add_glossy_object(glossy_bunny_template, object_locations[14], object_rotations[14], world)
        world = add_glossy_object(glossy_bunny_template, object_locations[15], object_rotations[15], world)

        world = add_glossy_object(glossy_teapot_template, object_locations[17], object_rotations[17], world)
        world = add_glossy_object(glossy_teapot_template, object_locations[18], object_rotations[18], world)
        world = add_glossy_object(glossy_teapot_template, object_locations[19], object_rotations[19], world)

        world = world + '\n' + u.cornellBoxLight()

        camera_position = u.generate_random_list(0.35, 0.95, 3)
        camera_position[1] = 0.4

        camera = u.lookAtPerspectiveCamera(camera_position, [0, 0, 0], u.generate_random_list(0, 1, 3), 45)

        generate_data(dataset, camera, world, per_dataset_counter)

        per_dataset_counter += 1
        counter += 1

def add_object(object_template, location, rotation, world):
    rgb = u.generate_random_list(0, 1, 3)
    world = world + '\n' + object_template.format(rgb[0], rgb[1], rgb[2], location[0], location[1], rotation)
    return world

def add_glossy_object(object_template, location, rotation, world):
    ks = u.generate_random_list(0, 1, 3)
    roughness = u.generate_random_list(0, 1, 1)
    world = world + '\n' + object_template.format(ks[0], ks[1], ks[2], roughness[0], location[0], location[1], rotation)
    return world

def generate_data(dataset, camera, world, name):

    direct_name = "{}_direct_{}".format(dataset, name)
    depth_name = "{}_depth_{}".format(dataset, name)
    gt_name = "{}_gt_{}".format(dataset, name)
    indirect_name = "{}_indirect_{}".format(dataset, name)

    roughness_name = "{}_roughness_{}".format(dataset, name)
    roughness2_name = "{}_roughness2p0t0_{}".format(dataset, name)
    reflectroughness2_name = "{}_reflectroughness2p0t0_{}".format(dataset, name)

    albedo_name = "{}_albedo_{}".format(dataset, name)
    albedo2_name = "{}_albedo2p0t0_{}".format(dataset, name)
    reflectalbedo2_name = "{}_reflectalbedo2p0t0_{}".format(dataset, name)

    specalbedo_name = "{}_specalbedo_{}".format(dataset, name)
    specalbedo2_name = "{}_specalbedo2p0t0_{}".format(dataset, name)
    reflectspecalbedo2_name = "{}_reflectspecalbedo2p0t0_{}".format(dataset, name)

    normal_name = "{}_normal_{}".format(dataset, name)
    normal2_name = "{}_normal2p0t0_{}".format(dataset, name)
    reflectnormal2_name = "{}_reflectnormal2p0t0_{}".format(dataset, name)

    albedo_scene_file_content = u.makePBRT(u.albedoIntegrator(), u.stratifiedSampler(), u.triangleFilter(), u.imageFilm(albedo_name + ".exr"), camera, world)
    albedo2_scene_file_content = u.makePBRT(u.albedo2Integrator(), u.stratifiedSampler(), u.triangleFilter(), u.imageFilm(albedo2_name + ".exr"), camera, world)
    reflectalbedo2_scene_file_content = u.makePBRT(u.reflectAlbedo2Integrator(), u.stratifiedSampler(), u.triangleFilter(), u.imageFilm(reflectalbedo2_name + ".exr"), camera, world)

    specalbedo_scene_file_content = u.makePBRT(u.specAlbedoIntegrator(), u.stratifiedSampler(), u.triangleFilter(), u.imageFilm(specalbedo_name + ".exr"), camera, world)
    specalbedo2_scene_file_content = u.makePBRT(u.specAlbedo2Integrator(), u.stratifiedSampler(), u.triangleFilter(), u.imageFilm(specalbedo2_name + ".exr"), camera, world)
    reflectspecalbedo2_scene_file_content = u.makePBRT(u.reflectSpecAlbedo2Integrator(), u.stratifiedSampler(), u.triangleFilter(), u.imageFilm(reflectspecalbedo2_name + ".exr"), camera, world)

    normal_scene_file_content = u.makePBRT(u.normalIntegrator(), u.stratifiedSampler(), u.triangleFilter(), u.imageFilm(normal_name + ".exr"), camera, world)
    normal2_scene_file_content = u.makePBRT(u.normal2Integrator(), u.stratifiedSampler(), u.triangleFilter(), u.imageFilm(normal2_name + ".exr"), camera, world)
    reflectnormal2_scene_file_content = u.makePBRT(u.reflectNormal2Integrator(), u.stratifiedSampler(), u.triangleFilter(), u.imageFilm(reflectnormal2_name + ".exr"), camera, world)

    roughness_scene_file_content = u.makePBRT(u.roughnessIntegrator(), u.stratifiedSampler(), u.triangleFilter(), u.imageFilm(roughness_name + ".exr"), camera, world)
    roughness2_scene_file_content = u.makePBRT(u.roughness2Integrator(), u.stratifiedSampler(), u.triangleFilter(), u.imageFilm(roughness2_name + ".exr"), camera, world)
    reflectroughness2_scene_file_content = u.makePBRT(u.reflectRoughness2Integrator(), u.stratifiedSampler(), u.triangleFilter(), u.imageFilm(reflectroughness2_name + ".exr"), camera, world)

    direct_scene_file_content = u.makePBRT(u.directIlluminationIntegrator(), u.stratifiedSampler(16, 16), u.triangleFilter(), u.imageFilm(direct_name + ".exr"), camera, world)
    depth_scene_file_content = u.makePBRT(u.depthIntegrator(), u.stratifiedSampler(), u.triangleFilter(), u.imageFilm(depth_name + ".exr"), camera, world)
    gt_scene_file_content = u.makePBRT(u.pathTracingIntegrator(), u.stratifiedSampler(32, 32), u.triangleFilter(), u.imageFilm(gt_name + ".exr"), camera, world)
    indirect_scene_file_content = u.makePBRT(u.indirectIlluminationIntegrator(), u.stratifiedSampler(32, 32), u.triangleFilter(), u.imageFilm(indirect_name + ".exr"), camera, world)

    save_scene_file(albedo_scene_file_content, "scenefiles\\primitive_room_ff3\\" + albedo_name + ".pbrt")
    save_scene_file(albedo2_scene_file_content, "scenefiles\\primitive_room_ff3\\" + albedo2_name + ".pbrt")
    save_scene_file(reflectalbedo2_scene_file_content, "scenefiles\\primitive_room_ff3\\" + reflectalbedo2_name + ".pbrt")

    save_scene_file(specalbedo_scene_file_content, "scenefiles\\primitive_room_ff3\\" + specalbedo_name + ".pbrt")
    save_scene_file(specalbedo2_scene_file_content, "scenefiles\\primitive_room_ff3\\" + specalbedo2_name + ".pbrt")
    save_scene_file(reflectspecalbedo2_scene_file_content, "scenefiles\\primitive_room_ff3\\" + reflectspecalbedo2_name + ".pbrt")

    save_scene_file(normal_scene_file_content, "scenefiles\\primitive_room_ff3\\" + normal_name + ".pbrt")
    save_scene_file(normal2_scene_file_content, "scenefiles\\primitive_room_ff3\\" + normal2_name + ".pbrt")
    save_scene_file(reflectnormal2_scene_file_content, "scenefiles\\primitive_room_ff3\\" + reflectnormal2_name + ".pbrt")

    save_scene_file(roughness_scene_file_content, "scenefiles\\primitive_room_ff3\\" + roughness_name + ".pbrt")
    save_scene_file(roughness2_scene_file_content, "scenefiles\\primitive_room_ff3\\" + roughness2_name + ".pbrt")
    save_scene_file(reflectroughness2_scene_file_content, "scenefiles\\primitive_room_ff3\\" + reflectroughness2_name + ".pbrt")

    save_scene_file(direct_scene_file_content, "scenefiles\\primitive_room_ff3\\" + direct_name + ".pbrt")
    save_scene_file(depth_scene_file_content, "scenefiles\\primitive_room_ff3\\" + depth_name + ".pbrt")
    #save_scene_file(gt_scene_file_content, "scenefiles\\primitive_room_ff3\\" + gt_name + ".pbrt")
    save_scene_file(indirect_scene_file_content, "scenefiles\\primitive_room_ff3\\" + indirect_name + ".pbrt")


def save_scene_file(scene_file_content, path):

    scene_file = open("scene.pbrt", "w")
    scene_file.write(scene_file_content)
    scene_file.close()

    if os.path.exists(path):
        os.remove(path)
    os.rename(os.path.abspath("scene.pbrt"), path)


primitive_room()
