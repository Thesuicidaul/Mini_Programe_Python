import json
import maya.cmds as cmds

def realiser(file):
    """
    Lit un fichier JSON, recrée les objets avec `C_Curve`, applique les hiérarchies et les verrouille.
    """
    try:
        with open(file, 'r') as json_file:
            data = json.load(json_file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        cmds.warning(f"Erreur lors de la lecture du fichier : {e}")
        return

    created_objects = {}  # Stocke les objets créés pour le parentage
    parent_relations = []  # Stocke les relations de parentage à appliquer plus tard

    # Étape 1 : Création des objets sans les verrouiller
    for obj_data in data:
        obj_type = obj_data.get('type')
        name = obj_data.get('name')
        position = obj_data.get('position', [0, 0, 0])
        orientation = obj_data.get('orientation', [0, 0, 0])
        color = obj_data.get('color', [1, 1, 1])  # Blanc par défaut

        # Création de l'objet via C_Curve
        created_obj = C_Curve(obj_type, name, position, orientation, color)
        if not created_obj:
            cmds.warning(f"Impossible de créer l'objet {name}")
            continue

        created_objects[name] = created_obj  # Stocker l'objet

        # Gestion du parentage
        hierarchy = obj_data.get('hierarchy', [])
        if hierarchy:
            parent_name = hierarchy[-1]  # Le parent immédiat
            parent_relations.append((created_obj, parent_name))

    # Étape 2 : Application du parentage après la création des objets
    for child_obj, parent_name in parent_relations:
        if parent_name in created_objects:
            cmds.parent(child_obj, created_objects[parent_name])
        else:
            cmds.warning(f"Parent {parent_name} non trouvé pour {child_obj}")

    # Étape 3 : Verrouillage des transformations après le parentage
    for obj in created_objects.values():
        for attr in ["translateX", "translateY", "translateZ",
                     "rotateX", "rotateY", "rotateZ",
                     "scaleX", "scaleY", "scaleZ"]:
            cmds.setAttr(f"{obj}.{attr}", lock=True)

    print(f"Les objets ont été créés et parentés à partir de {file}.")












def C_Curve(obj_type, name, position, orientation, color_num):
    """
    Crée une forme en fonction du type et applique position, orientation et couleur via le drawing override.

    :param obj_type: Type de la forme ("Circle", "CubL", "SphL")
    :param name: Nom de l'objet
    :param position: Position sous forme de liste [x, y, z]
    :param orientation: Orientation sous forme de liste [x, y, z]
    :param color_num: Numéro de la couleur dans le drawing override
    :return: Nom de l'objet créé
    """

    obj = None

    if obj_type == "Circle":
        obj = cmds.circle(n=name, radius=3, normal=[0, 1, 0], constructionHistory=False)[0]

    elif obj_type == "CubL":
        obj = cmds.group(empty=True, name=name)
        
        # Création d'un cube en NURBS (taille 0.15)
        cube_size = 0.075  # La moitié de la taille du cube
        cube = cmds.curve(d=1, p=[[-cube_size, -cube_size, -cube_size], [-cube_size, -cube_size,  cube_size], 
                                  [ cube_size, -cube_size,  cube_size], [ cube_size, -cube_size, -cube_size], 
                                  [-cube_size, -cube_size, -cube_size], [-cube_size,  cube_size, -cube_size], 
                                  [ cube_size,  cube_size, -cube_size], [ cube_size,  cube_size,  cube_size], 
                                  [-cube_size,  cube_size,  cube_size], [-cube_size,  cube_size, -cube_size], 
                                  [-cube_size,  cube_size,  cube_size], [-cube_size, -cube_size,  cube_size], 
                                  [ cube_size, -cube_size,  cube_size], [ cube_size,  cube_size,  cube_size], 
                                  [ cube_size,  cube_size, -cube_size], [ cube_size, -cube_size, -cube_size]
        ], k=list(range(16)))
        cmds.parent(cmds.listRelatives(cube, shapes=True)[0], obj, shape=True, relative=True)
        cmds.delete(cube)

        # Création des axes en croix (taille 0.25)
        for axis in [[1, 0, 0], [0, 1, 0], [0, 0, 1]]:
            cross = cmds.curve(d=1, p=[[-0.125 * axis[0], -0.125 * axis[1], -0.125 * axis[2]], 
                                       [0.125 * axis[0], 0.125 * axis[1], 0.125 * axis[2]]], 
                               k=[0, 1])
            cmds.parent(cmds.listRelatives(cross, shapes=True)[0], obj, shape=True, relative=True)
            cmds.delete(cross)

    elif obj_type == "SphL":
        obj = cmds.group(empty=True, name=name)
        
        # Création des trois cercles pour la sphère (radius = 0.15)
        for axis in [[1, 0, 0], [0, 1, 0], [0, 0, 1]]:
            circle = cmds.circle(nr=axis, radius=0.15, constructionHistory=False)[0]
            cmds.parent(cmds.listRelatives(circle, shapes=True)[0], obj, shape=True, relative=True)
            cmds.delete(circle)

        # Création des axes en croix (taille = 0.25)
        for axis in [[1, 0, 0], [0, 1, 0], [0, 0, 1]]:
            cross = cmds.curve(d=1, p=[[-0.125 * axis[0], -0.125 * axis[1], -0.125 * axis[2]], 
                                       [0.125 * axis[0], 0.125 * axis[1], 0.125 * axis[2]]], 
                               k=[0, 1])
            cmds.parent(cmds.listRelatives(cross, shapes=True)[0], obj, shape=True, relative=True)
            cmds.delete(cross)

    else:
        cmds.warning(f"Type inconnu : {obj_type}")
        return None

    # Appliquer position et orientation
    cmds.xform(obj, translation=position, rotation=orientation, worldSpace=True)

    # Appliquer la couleur via le drawing override
    shape_nodes = cmds.listRelatives(obj, shapes=True, fullPath=True) or []
    for shape in shape_nodes:
        cmds.setAttr(f"{shape}.overrideEnabled", 1)
        cmds.setAttr(f"{shape}.overrideColor", color_num)  # Utilisation du numéro de couleur

    return obj











def get_color(obj):
    """
    Récupère la couleur d'un objet en trouvant son shader.
    """
    shading_engines = cmds.listConnections(obj, type='shadingEngine')
    if shading_engines:
        shader = cmds.listConnections(f"{shading_engines[0]}.surfaceShader")
        if shader:
            try:
                return cmds.getAttr(f"{shader[0]}.color")[0]  # Récupérer la couleur RGB
            except ValueError:
                cmds.warning(f"Impossible d'obtenir la couleur pour {obj}")
    return None  # Retourne None si aucune couleur trouvée

def get_hierarchy(obj):
    """
    Récupère la hiérarchie d'un objet en listant ses parents.
    """
    hierarchy = []
    parent = cmds.listRelatives(obj, parent=True)
    while parent:
        hierarchy.append(parent[0])
        parent = cmds.listRelatives(parent[0], parent=True)
    
    return hierarchy[::-1] if hierarchy else None  # Retourne None si pas de parent

def get_type(obj):
    """
    Détermine le type réel de l'objet en vérifiant s'il est un transform contenant un shape.
    """
    obj_type = cmds.objectType(obj)
    
    if obj_type == "transform":
        shapes = cmds.listRelatives(obj, shapes=True, fullPath=True)  # Récupérer les formes attachées
        if shapes:
            return cmds.objectType(shapes[0])  # Retourne le type du premier shape
    return obj_type

def enregistrer(file):
    """
    Enregistre les informations des objets sélectionnés dans un fichier JSON.
    """
    data = []

    # Récupérer les objets sélectionnés dans la scène
    selected_objects = cmds.ls(selection=True)
    
    if not selected_objects:
        cmds.warning("Aucun objet sélectionné pour l'enregistrement.")
        return
    
    for obj in selected_objects:
        obj_data = {
            "name": obj,
            "position": cmds.xform(obj, query=True, worldSpace=True, translation=True),
            "orientation": cmds.xform(obj, query=True, worldSpace=True, rotation=True),
            "color": get_color(obj),
            "type": get_type(obj),
            "hierarchy": get_hierarchy(obj)
        }
        data.append(obj_data)

    # Sauvegarder les données dans un fichier JSON
    try:
        with open(file, 'w') as json_file:
            json.dump(data, json_file, indent=4)
        print(f"Les données ont été enregistrées dans {file}")
    except IOError as e:
        cmds.warning(f"Erreur lors de l'enregistrement du fichier : {e}")



def get_shape_override_color(obj):
    """Récupère la couleur du premier shape node avec override activé."""
    shapes = cmds.listRelatives(obj, shapes=True, fullPath=True) or []
    
    for shape in shapes:
        override_enabled = cmds.getAttr(f"{shape}.overrideEnabled")
        if override_enabled:
            return cmds.getAttr(f"{shape}.overrideColor")  # Retourne la couleur de l’override

    return None  # Retourne None si aucun shape valide n’a été trouvé

def update_json_colors(json_file=None):
    """Met à jour les couleurs des objets JSON avec celles des objets sélectionnés dans Maya."""
    with open(json_file, "r") as file:
        data = json.load(file)

    selected_objs = cmds.ls(selection=True, long=True)  # Récupère les objets sélectionnés avec chemin complet
    if not selected_objs:
        cmds.warning("Aucun objet sélectionné !")
        return

    name_to_color = {}  # Stocke les couleurs des objets sélectionnés
    for obj in selected_objs:
        color = get_shape_override_color(obj)
        short_name = obj.split("|")[-1]  # Récupère juste le nom sans le chemin complet
        if color is not None:
            name_to_color[short_name] = color

    updated = False
    for obj in data:
        obj_name = obj["name"]
        if obj_name in name_to_color:
            print(f"🔹 Mise à jour : {obj_name} → Couleur {name_to_color[obj_name]}")  # DEBUG
            obj["color"] = name_to_color[obj_name]
            updated = True

    if updated:
        with open(json_file, "w") as file:
            json.dump(data, file, indent=4)
        print(f"✅ Fichier {json_file} mis à jour avec les couleurs des objets sélectionnés.")
    else:
        print("⚠️ Aucun objet correspondant trouvé dans le JSON, aucun changement effectué.")







#Test fonction 
#obj1 = C_Curve("Circle", "MyCircle", [0, 0, 0], [0, 0, 0], [1, 0, 0])  # Rouge
#obj2 = C_Curve("CubL", "MyCube", [5, 0, 0], [0, 45, 0], [0, 1, 0])  # Vert
#obj3 = C_Curve("SphL", "MySphere", [-5, 0, 0], [0, 0, 45], [0, 0, 1])  # Bleu
#update_json_colors()


