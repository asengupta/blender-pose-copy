# This copies animation keyframes from any animated rig which lacks a rest pose to an identical skeleton which has a rest pose but no pre-existing animations

import bpy

bpy.app.handlers.frame_change_post.clear()

SOURCE_ARMATURE_NAME = "Rest Pose Armature.002"
TARGET_ARMATURE_NAME = "Armature.024"

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

def insert_keyframe(armature, frame):
    for bone in armature.pose.bones:
        bone.keyframe_insert(data_path="location", frame = frame)
        bone.keyframe_insert(data_path="rotation_quaternion", frame = frame)

def keyframe_insert_frame_handler(scene):
    frame = scene.frame_current
    print("Current frame is {}".format(frame))
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.context.view_layer.objects.active = source_armature
    source_armature.select_set(True)
    bpy.ops.object.mode_set(mode='POSE')
    clear_pose()
    pose_recursively("Master", root_bone_tree)
    bpy.ops.object.mode_set(mode='OBJECT')
    insert_keyframe(source_armature, frame)

def deselect_all():
    for ob in bpy.context.selected_objects:
        ob.select_set(False)

def build_keyframes(frame_numbers):
    for frame in frame_numbers:
        bpy.context.scene.frame_set(frame)

bpy.app.handlers.frame_change_post.append(keyframe_insert_frame_handler)

root_bone_tree = hierarchy(source_bones["Master"])

deselect_all()
bpy.ops.object.mode_set(mode='POSE')
build_keyframes(range(1,45))

print("Unregistering handler")
bpy.app.handlers.frame_change_post.clear()
