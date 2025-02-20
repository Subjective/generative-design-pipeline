import bpy

def main(heightmap_path, color_texture_path):
    # ------------------------------------------------------------------------
    # 1) Get the active object and verify it's a Mesh
    # ------------------------------------------------------------------------
    obj = bpy.context.active_object
    if not obj or obj.type != 'MESH':
        raise ValueError("Please select a mesh object (e.g., a cube) before running this script.")

    mesh = obj.data

    # ------------------------------------------------------------------------
    # 2) Identify the top face (highest center.z)
    # ------------------------------------------------------------------------
    top_face_index = None
    max_z = float('-inf')
    for poly in mesh.polygons:
        if poly.center.z > max_z:
            max_z = poly.center.z
            top_face_index = poly.index

    if top_face_index is None:
        raise ValueError("No faces found in this mesh!")

    # ------------------------------------------------------------------------
    # 3) Enter Edit Mode and deselect all
    # ------------------------------------------------------------------------
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.object.mode_set(mode='OBJECT')

    # ------------------------------------------------------------------------
    # 4) Programmatically select ONLY the top face
    # ------------------------------------------------------------------------
    for p in mesh.polygons:
        p.select = False
    mesh.polygons[top_face_index].select = True

    # ------------------------------------------------------------------------
    # 5) Go back to Edit Mode, ensure Face Select Mode, and subdivide
    # ------------------------------------------------------------------------
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_mode(type='FACE')
    bpy.ops.mesh.subdivide(number_cuts=100)  # Adjust cuts as needed

    # Return to Object Mode
    bpy.ops.object.mode_set(mode='OBJECT')

    # ------------------------------------------------------------------------
    # 6) Create a vertex group for the top face (now subdivided)
    # ------------------------------------------------------------------------
    mesh.update()
    new_top_face_index = None
    max_z2 = float('-inf')
    for poly in mesh.polygons:
        if poly.center.z > max_z2:
            max_z2 = poly.center.z
            new_top_face_index = poly.index

    if new_top_face_index is None:
        raise ValueError("Top face not found after subdivision!")

    # Gather the vertex indices for that top face
    top_face_verts = mesh.polygons[new_top_face_index].vertices

    # If a "TopFaceGroup" exists, remove it first
    group_name = "TopFaceGroup"
    if group_name in obj.vertex_groups:
        obj.vertex_groups.remove(obj.vertex_groups[group_name])

    # Create a new group & add those vertices
    vg = obj.vertex_groups.new(name=group_name)
    vg.add([v for v in top_face_verts], 1.0, 'ADD')

    # ------------------------------------------------------------------------
    # 7) Add a Displace Modifier (limit to the TopFaceGroup)
    # ------------------------------------------------------------------------
    disp_mod = obj.modifiers.new(name="TopDisplacement", type='DISPLACE')
    disp_mod.vertex_group = group_name
    disp_mod.direction = 'Z'
    disp_mod.strength = 1.0  

    # ------------------------------------------------------------------------
    # 8) Invert the Vertex Group influence in the modifier
    # ------------------------------------------------------------------------
    disp_mod.invert_vertex_group = True

    # ------------------------------------------------------------------------
    # 9) Create/Load a Texture for the Displacement
    # ------------------------------------------------------------------------
    disp_tex = bpy.data.textures.new("DisplaceTexture", type='IMAGE')
    disp_img = bpy.data.images.load(heightmap_path)
    disp_tex.image = disp_img
    disp_mod.texture = disp_tex

    print("Successfully subdivided ONLY the top face and inverted its displacement using:", heightmap_path)

    # ------------------------------------------------------------------------
    # 10) CREATE & ASSIGN A COLOR TEXTURE (Martian Landscape.png) TO THE TOP FACE
    # ------------------------------------------------------------------------
    # - We will create a new material with nodes.
    # - Load "Martian Landscape.png" as an Image Texture.
    # - Assign it only to the same top face.
    # ------------------------------------------------------------------------

    # Create a new material with node-based shaders
    top_mat = bpy.data.materials.new(name="TopFaceMaterial")
    top_mat.use_nodes = True

    # Get the Principled BSDF node
    bsdf_node = top_mat.node_tree.nodes.get("Principled BSDF")

    # Create an Image Texture node to load the color texture
    color_tex_node = top_mat.node_tree.nodes.new("ShaderNodeTexImage")
    color_tex_node.image = bpy.data.images.load(color_texture_path)
    color_tex_node.location = (-300, 0)

    # Link the texture Color to the Principled BSDF Base Color
    top_mat.node_tree.links.new(color_tex_node.outputs["Color"], bsdf_node.inputs["Base Color"])

    # Append this new material to the object
    obj.data.materials.append(top_mat)

    # Make sure we assign the material slot only to that top face
    bpy.ops.object.mode_set(mode='OBJECT')
    for p in mesh.polygons:
        p.select = False
    mesh.polygons[new_top_face_index].select = True

    bpy.ops.object.mode_set(mode='EDIT')
    obj.active_material_index = len(obj.data.materials) - 1
    bpy.ops.object.material_slot_assign()

    # Simple UV unwrap for the top face so the texture is mapped nicely
    bpy.ops.uv.smart_project()

    bpy.ops.object.mode_set(mode='OBJECT')

    print("Assigned color texture to top face from:", color_texture_path)


# ----------------------------------------------------------------------------
# USAGE:
# 1. In Blender, select a Cube (or any mesh) in OBJECT MODE.
# 2. Open the Text Editor, paste this script.
# 3. Update 'heightmap_path' and 'color_texture_path' to your actual PNG paths.
# 4. Click 'Run Script'.
# ----------------------------------------------------------------------------
heightmap_path = r"/Users/joshua/Downloads/Martian Landscape Heightmap.png"
color_texture_path = r"/Users/joshua/Downloads/Martian Landscape.png"

main(heightmap_path, color_texture_path)
