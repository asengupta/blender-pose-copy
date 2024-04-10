This is a simple Blender script which can work with bone trees, for adding and deleting keyframes en-masse. It was originally written to retarget the animation from a skeleton lacking a rest pose to an identical skeleton which does have a rest pose (but not animations, obviously). At the end, the rest pose-equipped armature will have the animations transferred to it.

I wrote this out of a very specific problem: Elden Ring animations imported into Blender had an incoherent rest pose, which I wanted to fix.
This script could potentially be used to retarget similar or incompatible skeletons if a bone mapping was provided.

The script you want to run is ```pose-copy.py```.

You will need to modify this script in the following way to use it effectively:

```
SOURCE_ARMATURE_NAME = "[YOUR_REST_POSE_ARMATURE_WITHOUT_ANIMATION]"
TARGET_ARMATURE_NAME = "[YOUR_ANIMATED_ARMATURE_WITHOUT_REST_POSE]"
ROOT_BONE_ID = "[ROOT_BONE_OF_POSE_TO_COPY]"
```

Also modify the following line:

```
build_keyframes([ARRAY_OF_FRAME_NUMBERS])
```

You may choose to forgo building keyframes altogether, and simply choose to pose the armature (or part of it) in line with an existing animation frame. In that case, change the frame to the target armature (which already has the animation) or pose it however you like, and then use:

```
pose_once(ROOT_BONE_ID)
```

There is other ancilliary functionality present. Here are some ways in which you can delete keyframes:

```
# Deletes all keyframes of a bone and its children
delete_keyframe(source_armature, ROOT_BONE_ID, hierarchy(source_bones[ROOT_BONE_ID]), ALL_FRAMES)

# Deletes all keyframes of a bone and its children between Frames 9 and 10 (keyframe exactly at Frame 9 is not deleted, keyframe at Frame 10 is deleted)
delete_keyframe(source_armature, ROOT_BONE_ID, hierarchy(source_bones[ROOT_BONE_ID]), SINGLE_FRAME(10))
```

You can write your own delete condition by simply implementing a lambda (see ALL_FRAMES and SINGLE_FRAME implementations for examples), and passing it into ```delete_keyframe()```.
