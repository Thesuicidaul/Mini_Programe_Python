import maya.cmds as cmds

# Création des locators pour mesurer la distance
loc_start = cmds.spaceLocator(name="start_LOC")[0]
loc_end = cmds.spaceLocator(name="end_LOC")[0]
cmds.move(5, 0, 0, loc_end)

# Création du node distanceBetween
distance_node = cmds.createNode("distanceBetween", name="distanceNode")
cmds.connectAttr(f"{loc_start}.translate", f"{distance_node}.point1")
cmds.connectAttr(f"{loc_end}.translate", f"{distance_node}.point2")

# Création du node multiplyDivide pour normaliser la valeur
normalize_node = cmds.createNode("multiplyDivide", name="normalizeNode")
cmds.setAttr(f"{normalize_node}.operation", 2)  # Mode Divide
cmds.connectAttr(f"{distance_node}.distance", f"{normalize_node}.input1X")
cmds.setAttr(f"{normalize_node}.input2X", 5)  # Longueur initiale

# Création du node pour conserver le volume
squash_node = cmds.createNode("multiplyDivide", name="squashNode")
cmds.setAttr(f"{squash_node}.operation", 3)  # Mode Power
cmds.setAttr(f"{squash_node}.input2X", 0.5)  # Racine carrée
cmds.connectAttr(f"{normalize_node}.outputX", f"{squash_node}.input1X")

# Appliquer le stretch sur un joint (exemple)
joint = cmds.joint(name="stretch_JNT")
cmds.connectAttr(f"{normalize_node}.outputX", f"{joint}.scaleX")
cmds.connectAttr(f"{squash_node}.outputX", f"{joint}.scaleY")
cmds.connectAttr(f"{squash_node}.outputX", f"{joint}.scaleZ")

print("Squash & Stretch Setup Completed!")
