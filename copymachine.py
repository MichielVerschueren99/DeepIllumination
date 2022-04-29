
import shutil


def replace_text(file_name, original, replacement):
    f = open(file_name, 'r')
    filedata = f.read()
    f.close()
    newdata = filedata.replace(original, replacement)
    f = open(file_name, 'w')
    f.write(newdata)
    f.close()


for i in range(4, 5):
    shutil.copyfile("C:\\Users\\Michi\\PycharmProjects\\DeepIllumination\\scenefiles\\test_setups\\test_albedo_{}.pbrt".format(str(i)),
                    "C:\\Users\\Michi\\PycharmProjects\\DeepIllumination\\scenefiles\\test_setups\\test_depth_{}.pbrt".format(str(i)))
    replace_text("C:\\Users\\Michi\\PycharmProjects\\DeepIllumination\\scenefiles\\test_setups\\test_depth_{}.pbrt".format(str(i)),
                                 'Integrator "albedo"', 'Integrator "depth"')
    replace_text("C:\\Users\\Michi\\PycharmProjects\\DeepIllumination\\scenefiles\\test_setups\\test_depth_{}.pbrt".format(str(i)),
                                 '"string filename" [ "test_albedo_{}.exr" ]'.format(str(i)), '"string filename" [ "test_depth_{}.exr" ]'.format(str(i)))

    shutil.copyfile(
        "C:\\Users\\Michi\\PycharmProjects\\DeepIllumination\\scenefiles\\test_setups\\test_albedo_{}.pbrt".format(
            str(i)),
        "C:\\Users\\Michi\\PycharmProjects\\DeepIllumination\\scenefiles\\test_setups\\test_normal_{}.pbrt".format(
            str(i)))
    replace_text(
        "C:\\Users\\Michi\\PycharmProjects\\DeepIllumination\\scenefiles\\test_setups\\test_normal_{}.pbrt".format(
            str(i)),
        'Integrator "albedo"', 'Integrator "normal"')
    replace_text(
        "C:\\Users\\Michi\\PycharmProjects\\DeepIllumination\\scenefiles\\test_setups\\test_normal_{}.pbrt".format(
            str(i)),
        '"string filename" [ "test_albedo_{}.exr" ]'.format(str(i)),
        '"string filename" [ "test_normal_{}.exr" ]'.format(str(i)))

    shutil.copyfile(
        "C:\\Users\\Michi\\PycharmProjects\\DeepIllumination\\scenefiles\\test_setups\\test_albedo_{}.pbrt".format(
            str(i)),
        "C:\\Users\\Michi\\PycharmProjects\\DeepIllumination\\scenefiles\\test_setups\\test_direct_{}.pbrt".format(
            str(i)))
    replace_text(
        "C:\\Users\\Michi\\PycharmProjects\\DeepIllumination\\scenefiles\\test_setups\\test_direct_{}.pbrt".format(
            str(i)),
        'Integrator "albedo"', 'Integrator "directlighting"')
    replace_text(
        "C:\\Users\\Michi\\PycharmProjects\\DeepIllumination\\scenefiles\\test_setups\\test_direct_{}.pbrt".format(
            str(i)),
        '"string filename" [ "test_albedo_{}.exr" ]'.format(str(i)),
        '"string filename" [ "test_direct_{}.exr" ]'.format(str(i)))

    shutil.copyfile(
        "C:\\Users\\Michi\\PycharmProjects\\DeepIllumination\\scenefiles\\test_setups\\test_albedo_{}.pbrt".format(
            str(i)),
        "C:\\Users\\Michi\\PycharmProjects\\DeepIllumination\\scenefiles\\test_setups\\test_gt_{}.pbrt".format(
            str(i)))
    replace_text(
        "C:\\Users\\Michi\\PycharmProjects\\DeepIllumination\\scenefiles\\test_setups\\test_gt_{}.pbrt".format(
            str(i)),
        'Integrator "albedo"', 'Integrator "path" "integer maxdepth" [ 65 ]')
    replace_text(
        "C:\\Users\\Michi\\PycharmProjects\\DeepIllumination\\scenefiles\\test_setups\\test_gt_{}.pbrt".format(
            str(i)),
        '"string filename" [ "test_albedo_{}.exr" ]'.format(str(i)),
        '"string filename" [ "test_gt_{}.exr" ]'.format(str(i)))

    shutil.copyfile(
        "C:\\Users\\Michi\\PycharmProjects\\DeepIllumination\\scenefiles\\test_setups\\test_albedo_{}.pbrt".format(
            str(i)),
        "C:\\Users\\Michi\\PycharmProjects\\DeepIllumination\\scenefiles\\test_setups\\test_indirect_{}.pbrt".format(
            str(i)))
    replace_text(
        "C:\\Users\\Michi\\PycharmProjects\\DeepIllumination\\scenefiles\\test_setups\\test_indirect_{}.pbrt".format(
            str(i)),
        'Integrator "albedo"', 'Integrator "indirectlighting" "integer maxdepth" [ 65 ]')
    replace_text(
        "C:\\Users\\Michi\\PycharmProjects\\DeepIllumination\\scenefiles\\test_setups\\test_indirect_{}.pbrt".format(
            str(i)),
        '"string filename" [ "test_albedo_{}.exr" ]'.format(str(i)),
        '"string filename" [ "test_indirect_{}.exr" ]'.format(str(i)))
