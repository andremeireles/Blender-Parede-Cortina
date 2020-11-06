# <pep8-80 compliant>
# https://wiki.blender.org/wiki/Process/Addons/Guidelines

# Dicas encontrada em
# https://blender.stackexchange.com/questions/128549/how-can-i-check-face-selection-in-edit-mode
#
# https://devtalk.blender.org/t/check-if-object-is-selected-and-it-is-a-mesh-or-in-edit-mode/13113/9

# def poll(cls, context):
# active_object = context.active_object
# return active_object is not None and active_object.type == 'MESH' and (context.mode == 'EDIT_MESH' or active_object.select_get())


import bpy

print(f"Este print veio de {__name__}")
