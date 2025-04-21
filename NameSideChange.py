import maya.cmds as mc

def Change_Name():
    """
    change le nom des objet selectioner pour que le coter s'inverce
    """
    for obj in mc.ls(selection=1):
        print(obj.split("|"))
        obj_f = obj.split("|")[-1]
        Name_Split=obj_f.split("_")
        
        # obj = "(Info important)_(Nom de l'objet)_(Left, Right ou rien)_(Numéro de l'objet ou rien si il est seul)"
        if len(Name_Split) >= 3 and Name_Split[2] == "L":
            Name_Split[2] = "R"
        elif len(Name_Split) >= 3 and Name_Split[2] == "R":
            Name_Split[2] = "L"
        Name_Split = "_".join(Name_Split)
        
        cmds.rename(obj, Name_Split)
        print(f"Objet {obj} a étais renomée en : {Name_Split}")
        
Change_Name()
