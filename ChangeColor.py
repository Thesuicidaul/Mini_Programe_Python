import maya.cmds as cmds

def set_shape_nodes_color():
  """
  change les couleur des shape des objets sélectionné
  """
    # Obtenir les objets sélectionnés
    selected_objects = cmds.ls(selection=True)

    if not selected_objects:
        cmds.error("Aucun objet sélectionné.")

    # je parcoure chaque objet sélectionné
    for obj in selected_objects:
        # je mets dans shape_nodes tous les shape nodes associés à l'objet
        shape_nodes = cmds.listRelatives(obj, shapes=True)
        
        if shape_nodes:
            for shape in shape_nodes:
                # Vérifier si l'attribut 'overrideEnabled' existe avant de le modifier
                if cmds.attributeQuery("overrideEnabled", node=shape, exists=True):
                    # j'activer le drawing override pour chaque shape node
                    cmds.setAttr(f"{shape}.overrideEnabled", 1)
                    # je définie la couleur
                    cmds.setAttr(f"{shape}.overrideColor", 17)

    print("Les objets sélectionnés ont été mis en couleur verte claire avec le drawing override.")


set_shape_nodes_color()
