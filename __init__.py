# https://wiki.blender.org/wiki/Process/Addons/Guidelines

import bpy

# ----------------------------------------------
# Define Addon info
# ----------------------------------------------

bl_info = {
    "name": "Parede Cortina",
    "description": "Permite criar parede cortina.",
    "author": "André Meireles Barbosa",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "View3D > Sidebar > Add-on",
    # used for warning icon and text in addons panel
    "warning": "Versão em estágio alpha, portanto erros podem acontecer com mais frequência",
    "wiki_url": "https://github.com/andremeireles/Blender-Parede-Cortina/wiki/",
    "tracker_url": "https://github.com/andremeireles/Blender-Parede-Cortina/issues",
    "support": "COMMUNITY",
    "category": "Add Mesh",
}


class Painel_Principal(bpy.types.Panel):
    """Cria um Painel para criar parede cortina"""
    bl_label = "Painel pricipal, contem entradas e botoes"
    bl_idname = "Cortina_PT_MainPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Add-on'

    def draw(self, context):
        layout = self.layout

        row = layout.row()

        row.label(text="Criar parede cortina")

        row = layout.row()
        row.operator("mesh.primitive_cube_add",
                     text="Um painel", icon='SNAP_FACE')

        row = layout.row()
        row.operator("mesh.primitive_plane_add",
                     text="Mais de um painel", icon='MOD_EXPLODE')

# ----------------------------------------------
# Register Addon
# ----------------------------------------------


class MESH_OT_parede_cortina(bpy.types.Operator):
    bl_idname = "mesh.parede_cortina"
    bl_label = "Rótulo deste painel"
    bl_options = {'REGISTER', 'UNDO'}

    dimensao_x: bpy.props.IntProperty(
        name="X",
        description="Dimensão no eixo X",
        default=1,
        min=1, soft_max=10,
    )
    dimensao_y: bpy.props.IntProperty(
        name="Y",
        description="Dimensão no eixo Y",
        default=2,
        min=1, soft_max=3,
    )

    def execute(self, context):
        print("O addon foi carregado com sucesso")
        return {'FINISHED'}


def register():
    bpy.utils.register_class(Painel_Principal)


def unregister():
    bpy.utils.unregister_class(Painel_Principal)


if __name__ == "__main__":
    register()

    # debug ? apagar depois dos testes
    # bpy.ops.mesh.parede_cortina()
