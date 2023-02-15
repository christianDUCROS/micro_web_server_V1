def modifications_dico_valeurs_dynamiques(dico) :
    import random
####################################"
#    pass #pour ne rien faire
####################################
    #simulation capteurs random 
    valeur_temperature = random.randint(19,24) 

    # insertion ou modification  valeurs dico_valeurs_dynamiques  
    dico["temperature"] = str(valeur_temperature)#str car texte

    #modification valeurs {{couleur_background}} du CSS et images{{carre_couleur}} du HTML
    if valeur_temperature > 22 :
       dico["couleur_background"] = "#1E90FF"
       dico["carre_couleur"] = "images/carre_rouge.jpg"
       
    else :
       dico["couleur_background"] = "#FFDC33"
       dico["carre_couleur"] = "images/carre_vert.jpg"
####################################
    return(dico)
