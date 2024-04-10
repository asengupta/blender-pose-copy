# This copies animation keyframes from any animated rig which lacks a rest pose to an identical skeleton which has a rest pose but no pre-existing animations

import bpy

bpy.app.handlers.frame_change_post.clear()

SOURCE_ARMATURE_NAME = "Block Transition.Original.001"
TARGET_ARMATURE_NAME = "Spear Walk.001"
ROOT_BONE_ID = "R_UpperArm"

source_armature = bpy.data.objects.get(SOURCE_ARMATURE_NAME)
target_armature = bpy.data.objects.get(TARGET_ARMATURE_NAME)

source_bones = source_armature.pose.bones
target_bones = target_armature.pose.bones

def clear_pose():
    bpy.ops.object.location_clear()
    bpy.ops.object.rotation_clear()
    bpy.ops.object.scale_clear()

# Record hierarchy
def hierarchy(bone):
    bone_tree = {}
    for child in bone.children:
        bone_tree[child.name] = hierarchy(child)
    return bone_tree

def pose(source_bone, target_bone, source_armature, target_armature):
    bpy.context.evaluated_depsgraph_get().update()
    target_bone = target_armature.pose.bones[source_bone.name]
    target_matrix = target_armature.convert_space(pose_bone=target_bone, matrix=target_bone.matrix, from_space="POSE", to_space="WORLD")
    source_bone.matrix = source_armature.convert_space(pose_bone=source_bone, matrix=target_matrix, from_space="WORLD", to_space="POSE")
    

def pose_recursively(bone_name, bone_tree):
    pose(source_bones[bone_name], target_bones[bone_name], source_armature, target_armature)
    for child_name, child_tree in bone_tree.items():
        pose_recursively(child_name, child_tree)

def pose_once(bone_name):
    root_bone_tree = hierarchy(source_bones[bone_name])
    pose_internal(bone_name, root_bone_tree)

def pose_internal(bone_name, root_bone_tree):
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.context.view_layer.objects.active = source_armature
    source_armature.select_set(True)
    bpy.ops.object.mode_set(mode='POSE')
    clear_pose()
    pose_recursively(bone_name, root_bone_tree)

def SINGLE_FRAME(frame):
    return lambda kf: (kf.co.x > frame -1 and kf.co.x <= frame)

def FRAME_RANGE(start_frame, end_frame):
    return lambda kf: (kf.co.x >= start_frame and kf.co.x <= end_frame)

def ALL_FRAMES(kf):
    return True
 
def delete_keyframe_with_property(property, bone, armature, delete_condition):
    data_path = "pose.bones[\"{}\"].{}".format(bone.name, property)
    print("Searching for {}".format(data_path))
    fcurves = armature.animation_data.action.fcurves
    bone_fcurves = [fcu for fcu in fcurves if fcu.data_path == data_path]
    for fcurve in bone_fcurves:
        print("Processing {}".format(fcurve.data_path))
#        points = [kf for kf in fcurve.keyframe_points if (kf.co.x > frame -1 and kf.co.x <= frame)]
        points = [kf for kf in fcurve.keyframe_points if delete_condition(kf)]
        while len(points) > 0:
            print("Deleting {}".format(points[0].co))
            fcurve.keyframe_points.remove(points[0])
            fcurve.keyframe_points.handles_recalc()
            points = [kf for kf in fcurve.keyframe_points if delete_condition(kf)]

def delete_bone_keyframe(bone, armature, delete_condition):
    delete_keyframe_with_property("location", bone, armature, delete_condition)
    delete_keyframe_with_property("rotation_quaternion", bone, armature, delete_condition)

def insert_keyframe_recursively(frame, bone_tree, armature):
    for child_bone_name, child_bone_tree in bone_tree.items():
        child_bone = armature.pose.bones[child_bone_name]
        child_bone.keyframe_insert(data_path="location", frame = frame)
        child_bone.keyframe_insert(data_path="rotation_quaternion", frame = frame)
        insert_keyframe_recursively(frame, child_bone_tree, armature)

def delete_keyframe_recursively(bone_tree, armature, delete_condition):
    for child_bone_name, child_bone_tree in bone_tree.items():
        child_bone = armature.pose.bones[child_bone_name]
        delete_bone_keyframe(child_bone, armature, delete_condition)
        delete_keyframe_recursively(child_bone_tree, armature, delete_condition)

def delete_keyframe(armature, root_bone_name, root_bone_tree, delete_condition):
    root_bone = armature.pose.bones[root_bone_name]
    delete_bone_keyframe(root_bone, armature, delete_condition)
    delete_keyframe_recursively(root_bone_tree, armature, delete_condition)

def insert_keyframe(armature, root_bone_name, root_bone_tree, frame):
    root_bone = armature.pose.bones[root_bone_name]
    root_bone.keyframe_insert(data_path="location", frame = frame)
    root_bone.keyframe_insert(data_path="rotation_quaternion", frame = frame)
    insert_keyframe_recursively(frame, root_bone_tree, armature)

def clear_animation(armature, root_bone_name):
   root_bone_tree = hierarchy(armature.pose.bones[root_bone_name])
   delete_keyframe(armature, root_bone_name, root_bone_tree, ALL_FRAMES)

def keyframe_insert_frame_handler_builder(root_bone_name):
    root_bone_tree = hierarchy(source_bones[root_bone_name])
    def keyframe_insert_frame_handler(scene):
        frame = scene.frame_current
        print("Current frame is {}".format(frame))
        delete_keyframe(source_armature, root_bone_name, root_bone_tree, SINGLE_FRAME(frame))
        pose_internal(root_bone_name, root_bone_tree)
#        bpy.ops.object.mode_set(mode='OBJECT')
        insert_keyframe(source_armature, root_bone_name, root_bone_tree, frame)
    return keyframe_insert_frame_handler

def deselect_all():
    for ob in bpy.context.selected_objects:
        ob.select_set(False)

def build_keyframes(frame_numbers):
    for frame in frame_numbers:
        bpy.context.scene.frame_set(frame)

handler = keyframe_insert_frame_handler_builder(ROOT_BONE_ID)
bpy.app.handlers.frame_change_post.append(handler)

deselect_all()

#pose_once(ROOT_BONE_ID)
#delete_keyframe(source_armature, ROOT_BONE_ID, hierarchy(source_bones[ROOT_BONE_ID]), ALL_FRAMES)
#clear_animation(source_armature, ROOT_BONE_ID)
delete_keyframe(source_armature, ROOT_BONE_ID, hierarchy(source_bones[ROOT_BONE_ID]), FRAME_RANGE(0, 7))

#build_keyframes([0])

print("Unregistering handler")
bpy.app.handlers.frame_change_post.clear()
