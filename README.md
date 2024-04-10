This is a simple Blender script which retargets the animation from a skeleton lacking a rest pose to an identical skeleton which does have a rest pose (but not animations, obviously). At the end, the rest pose-equipped armature will have the animations transferred to it.

I wrote this out of a very specific problem: Elden Ring animations imported into Blender had an incoherent rest pose, which I wanted to fix.
This script could potentially be used to retarget similar or incompatible skeletons if a bone mapping was provided.

This script can also pose arbitrary bones (including all child bone poses) given a source and a target. This makes it useful in remixing parts of multiple existing animations into a new one (with a little bit of tweaking after importing, of course).

THe script you want to run is ```pose-copy.py```.

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

You may choose to forgo building keyframes altogether, and simply choose to pose the armature (or part of it). In that case, change the frame to the target armature (which already has the animation) or pose it however you like, and then use:

```
pose_once(ROOT_BONE_ID)
```
