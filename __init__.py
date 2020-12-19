# -*- coding:utf-8 -*-

# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# <pep8 compliant>

# ----------------------------------------------------------
# Primeiros passos
# https://wiki.blender.org/wiki/Process/Addons/Guidelines

# ----------------------------------------------------------------------------
# Author: André Meireles Barbosa
# ----------------------------------------------------------------------------

import os

if "bpy" in locals():
    import importlib as imp
    imp.reload(operacoes)
else:
    from . import operacoes

import bmesh

import bpy

# ----------------------------------------------------------------------------
# Informações sobre o Add-on
# ----------------------------------------------------------------------------

bl_info = {
    "name": "Parede Cortina",
    "description": "Permite criar parede cortina.",
    "author": "André Meireles Barbosa",
    "version": (1, 0, 1, 1),
    "blender": (2, 83, 0),
    "location": "View3D > Sidebar > Add-on",
    # used for warning icon and text in addons panel
    "warning": "Versão em estágio alpha, portanto erros podem acontecer com mais frequência",
    "wiki_url": "https://github.com/andremeireles/Blender-Parede-Cortina/wiki/",
    "tracker_url": "https://github.com/andremeireles/Blender-Parede-Cortina/issues",
    "support": "COMMUNITY",
    "category": "Add Mesh",
}


# ----------------------------------------------------------------------------
# Proriedades que serão usadas
# ----------------------------------------------------------------------------


class Propriedades(bpy.types.PropertyGroup):

    nome: bpy.props.StringProperty(
        name="Nome",
        default="Sem nome"
    )

    selecao: bpy.props.BoolProperty(
        name="Usar face selecionada",
        description="Parede terá as dimensões e a posição da face selecionada",
        default=False
    )

    largura: bpy.props.FloatProperty(
        name="Largura",
        description="Dimensão no eixo horizontal",
        default=1,
        precision=2,
        min=.5, soft_max=10,
    )

    altura: bpy.props.FloatProperty(
        name="Altura",
        description="Dimensão no eixo vertical",
        default=1,
        min=.55, soft_max=20,
    )

    espessura: bpy.props.FloatProperty(
        name="Espessura",
        description="Espessura do montante",
        default=.15,
        min=.05, soft_max=1,
    )

    horizontal: bpy.props.IntProperty(
        name="Horizontal",
        description="Divisão na horizontal",
        default=1,
        min=1, soft_max=10,
    )

    vertical: bpy.props.IntProperty(
        name="Vertical",
        description="Divisão na vertical",
        default=2,
        min=1, soft_max=10,
    )

# ----------------------------------------------------------------------------
# Classe para o painel ser criado.
# ----------------------------------------------------------------------------


class CORTINA_PT_MainPanel(bpy.types.Panel):
    bl_region_type = 'UI'
    bl_space_type = 'VIEW_3D'
    bl_category = 'Add-on'
    bl_idname = "CORTINA_PT_MainPanel"
    bl_label = "Parede Cortina"
    bl_options = {'DEFAULT_CLOSED'}

# ----------------------------------------------------------------------------
# O painel não aparece se o arquivo está vazio
# ----------------------------------------------------------------------------
    @classmethod
    def poll(cls, context):
        return (context.object is not None)

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        variavel = scene.variaveis

        layout.prop(variavel, "nome")
        layout.prop(variavel, "selecao")
        layout.label(text="N° de divisões:")

        row = layout.row()
        row.prop(variavel, "horizontal")
        row.prop(variavel, "vertical")

        layout.prop(variavel, "espessura")

# ----------------------------------------------------------------------------
# Exibir dimensões apenas no modo objeto
# ----------------------------------------------------------------------------

        if not (variavel.selecao):
            layout.label(text="Dimensões da parede:")
            row = layout.row()
            row.prop(variavel, "largura")
            row.prop(variavel, "altura")

# ----------------------------------------------------------------------------
# Mudança de botões e icones, de acordo com o tipo da operação
# ----------------------------------------------------------------------------

        if not (variavel.selecao):
            layout.operator("cortina.criar_parede_cortina", icon="MESH_PLANE")
            if (context.mode == 'EDIT_MESH'):
                layout.label(
                    text="Para ativar o botão, entre em modo objeto ou"
                    f" marque a opção \"Usar face selecionada\"")
            if not (variavel.nome and variavel.nome.strip()):
                layout.label(text="Preencha o campo nome")

        else:
            layout.operator("cortina.criar_apartir_selecao", icon="SNAP_FACE")
            if (context.mode == 'OBJECT'):
                layout.label(
                    text="Para ativar o botão, entre em modo de edição ou "
                    f"desmarque a opção selecionada")
            if not (variavel.nome and variavel.nome.strip()):
                layout.label(text="Preencha o campo nome")

# ----------------------------------------------------------------------------
# Classe para botão no modo objeto
# ----------------------------------------------------------------------------


class CORTINA_OT_operator(bpy.types.Operator):
    bl_label = "Criar parede"
    bl_idname = "cortina.criar_parede_cortina"
    bl_description = "Constroi o painel"
    bl_options = {'REGISTER', 'UNDO'}

# ----------------------------------------------------------------------------
# Botão só ativa no modo objeto e possui um nome definido
# ----------------------------------------------------------------------------
    @classmethod
    def poll(cls, context):
        scene = context.scene
        variavel = scene.variaveis
        return (context.mode == 'OBJECT') \
            and (variavel.nome and variavel.nome.strip())

    def execute(self, context):
        scene = context.scene
        variavel = scene.variaveis

        # vertices = [(x, y, z), (x, y, z)...]
        vertices = [
            (variavel.largura, variavel.espessura, 0.0),
            (variavel.largura, 0.0, 0.0),
            (0.0, 0.0, 0.0),
            (0.0, variavel.espessura, 0.0),
            (variavel.largura, variavel.espessura, variavel.altura),
            (variavel.largura, 0.0, variavel.altura),
            (0.0, 0.0, variavel.altura),
            (0.0, variavel.espessura, variavel.altura)
        ]
        arestas = []

        # ordem dos vertices define a normal da face criada
        # sentido horario ==> normal apontará pra baixo, fundo e direita
        # sentido anti-horário ==> normal apontará pra cima, frente e esquerda
        faces = [
            (0, 1, 2, 3),
            (4, 7, 6, 5),
            (0, 4, 5, 1),
            (1, 5, 6, 2),
            (2, 6, 7, 3),
            (4, 0, 3, 7)
        ]

        nova_mesh = bpy.data.meshes.new("nova_mesh")
        nova_mesh.from_pydata(vertices, arestas, faces)
        nova_mesh.update()

        novo_objeto = bpy.data.objects.new(variavel.nome, nova_mesh)

        view_layer = bpy.context.view_layer
        view_layer.active_layer_collection.collection.objects.link(novo_objeto)

        # print(vertices)
        # print(
        #     f"A parede cortina de nome \"{variavel.nome}\" terá a dimensão"
        #     f" de {round(variavel.largura, 2)}m"
        #     f" x {round(variavel.altura, 2)}m. \n"
        #     f"Terá {variavel.horizontal * variavel.vertical} painéis, na "
        #     f"dimensão {round(variavel.largura / variavel.horizontal, 3)}m x"
        #     f" {round(variavel.altura / variavel.vertical, 3)}m")

        return {'FINISHED'}


# ----------------------------------------------------------------------------
# Classe para botão no modo de edição
# ----------------------------------------------------------------------------


class SELECAO_OT_operator(bpy.types.Operator):
    bl_label = "Criar parede"
    bl_idname = "cortina.criar_apartir_selecao"
    bl_description = "Constroi parede a partir da selecao de face"
    bl_options = {'REGISTER', 'UNDO'}

# ----------------------------------------------------------------------------
# Botão só ativa no modo de edição, com uma face selecionada
# e com um nome dado ao objeto
# ----------------------------------------------------------------------------
    @ classmethod
    def poll(cls, context):
        scene = context.scene
        variavel = scene.variaveis
        return (context.mode == 'EDIT_MESH') \
            and (context.object.data.polygons.data.total_face_sel > 0) \
            and (variavel.nome and variavel.nome.strip())

    def execute(self, context):
        scene = context.scene
        variavel = scene.variaveis

        objeto = context.edit_object
        dados = objeto.data
        bm = bmesh.from_edit_mesh(dados)

# ----------------------------------------------------------------------------
# Contagem de faces selecionadas numa lista de faces
# ----------------------------------------------------------------------------

        faces_sel = [f for f in bm.faces if f.select]

        if len(faces_sel) == 1:
            print("1 face selecionada")
        else:
            print("%d faces selecionadas" % len(faces_sel))

        return {'FINISHED'}

# ----------------------------------------------------------------------------
# Registro para o script ser usado como add-on
# ----------------------------------------------------------------------------


classes = [Propriedades, CORTINA_PT_MainPanel,
           CORTINA_OT_operator, SELECAO_OT_operator]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
        bpy.types.Scene.variaveis = bpy.props.PointerProperty(
            type=Propriedades)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()

# posso chamar no console por bpy.ops.cortina.criar_parede_cortina()
