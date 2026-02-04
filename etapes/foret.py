###############################################################
# Stockage des paramètres avec les hypothèses sourcées
###############################################################

param_foret = {

    # hypothèses pour convertir des données forestières exprimée en Mm3/an (dans le rapport IGN 2024) en MtC/an puis en MtCO2/an 

    "densité_bois_vert": 0.95, # (en t/m3) densité moyenne entre feuillus et résineux 

    "taux_humidité_bois_vert": 50, # (en %)  % de masse d'eau dans le bois vert

    "taux_carbone_bois_sec": 50, # (en %)  % de masse de carbone dans le bois sec

    "ratio_masse_C02_C": 44/12, # ratio de la masse de CO2 produite par unité de masse de carbone brûlée 

    "productivité_brute_2005_2013":91.5, # (en Mm3/an) croissance des arbres de la forêt française moyenne entre 2005 et 2013

    "productivité_brute_2014_2022":87.9, # (en Mm3/an) croissance des arbres de la forêt française moyenne entre 2014 et 2022

    "Mortalité_2005_2013": 7.4, # (en Mm3/an) mortalité des arbres de la forêt française entre 2005 et 2013

    "Mortalité_2014_2022": 15.2, # (en Mm3/an) mortalité des arbres de la forêt française entre 2014 et 2022

    "récolte_totale_2005_2013": 47.2, # (en Mm3/an) récolte totale de bois moyenne entre 2005 et 2013

    "récolte_totale_2014_2022": 53.1, # (en Mm3/an) récolte totale de bois moyenne entre 2005 et 2013

    "cible_production_SAF_2050": 3500, # (en kt/an) masse de e-bio kérosène cible en 2050 en France dans le cadre de ReFuel EU Aviation 

    "cible_production_BioTjet": 87, # (en kt/an) masse de production cible de e-bio-kérosène du projet BioTjet par an

    "cible_recolte_bois": 600, # (en kt/an) masse de bois nécessaire pour le projet BioTjet

    "réchauffement_moyen_France_2005_2013": 1.0, # (en K) réchauffement moyen mesuré entre 2005 et 2013

    "réchauffement_moyen_France_2014_2022": 1.6, # (en K) réchauffement moyen mesuré entre 2014 et 2022

    "T_2018": 1.65, # (en K) réchauffement moyen mesuré en 2018

    "T_2025":1.85, # (en K) projection de réchauffement pour la trajectoire TRACC en 2030 en France

    "T_2030":2.00, # (en K) projection de réchauffement pour la trajectoire TRACC en 2030 en France

    "T_2050":2.70, # (en K) projection de réchauffement pour la trajectoire TRACC en 2050 en France

    "T_2100":4, # (en K) projection de réchauffement pour la trajectoire TRACC en 2100 en France
    
    "coefficient_bonne_pratique_2025":1.00, # (pas d'unité) coefficient multiplicatif de la productivité   
                                             # lié à la généralisation des bonnes pratiques sylvicoles

    "coefficient_bonne_pratique_2100":2.00, # (pas d'unité) coefficient multiplicatif de la productivité   
                                             # lié à la généralisation des bonnes pratiques sylvicoles

    "année_début_bonne_pratique":2025,  # année où l'on commence à améliorer les bonnes pratiques avec interpolation
                                        # linéaire jusqu'à l'année où l'on atteint le coefficient maximal de bonne pratique

    "année_bonne_pratique_max":2100,  # année où l'on atteint le coefficient maximal de bonne pratique

    "rapport_capacité_sequestration_sol_aerien":2.121 # rapport entre la capacité de stockage du carbone d'un arbre
                                                      # pour la partie sol et la partie aérienne 
}



# FONCTIONS


 
# fonction qui détermine la productivité et la mortalité de la forêt française, pour l'année spécifiée en entrée. Le paramètre béta quantifie 
# l'impact du changement climatique sur l'état de la forêt 

#### Cette fonction marche pour 2030,2050 et 2100 (commentaire à supprimmer)
def impact_changement_climatique_foret(année,beta):

    # coefficient directeur de décroissance de la productivité de la forêt française entre 2005 et 2022 
    alpha_productivité = (param_foret["productivité_brute_2014_2022"]- param_foret["productivité_brute_2005_2013"]) \
    /((param_foret["réchauffement_moyen_France_2014_2022"]-param_foret["réchauffement_moyen_France_2005_2013"])**(beta))
    
     # coefficient directeur de décroissance de la productivité de la forêt française entre 2005 et 2022 
    alpha_mortalité = (param_foret["Mortalité_2014_2022"]- param_foret["Mortalité_2005_2013"]) \
    /(param_foret["réchauffement_moyen_France_2014_2022"]-param_foret["réchauffement_moyen_France_2005_2013"])**(beta)
    
    productivité = param_foret["productivité_brute_2005_2013"] + alpha_productivité* \
    (param_foret["T_"+str(année)]-param_foret["T_2018"] \
     +param_foret["réchauffement_moyen_France_2014_2022"]-param_foret["réchauffement_moyen_France_2005_2013"])**(beta)                     
                                 
    mortalité = param_foret["Mortalité_2005_2013"]+alpha_mortalité* \
    (param_foret["T_"+str(année)]-param_foret["T_2018"] \
     +param_foret["réchauffement_moyen_France_2014_2022"]-param_foret["réchauffement_moyen_France_2005_2013"])**(beta)



    return  productivité, mortalité  # résultats en Mm3/an

# fonction qui calcule la masse de biomasse nécessaire en fonction de la généralisation partielle 
# ou totale du procédé BioTjet pour atteindre les objectifs de ReFuel-EU en 2050.
# En cas de généralisation, en France, besoin de 3500 kt de SAF 

#### Cette fonction marche ! (commentaire à effacer)
def besoin_biomasse_generalisation(généralisation): # généralisation en %
    cible_production_SAF_France = 3500 
    cible_production_bioTjet = 87
    cible_recolte_bois = 600

    besoin_masse_bois_2050 = généralisation/100 * cible_recolte_bois*(cible_production_SAF_France/cible_production_bioTjet)/1000 # en Mt

    return besoin_masse_bois_2050 # en Mt de bois

# fonction qui calcule la variation de la capacité totale de séquestration carbone de la forêt française (en MtCO2/an) 
# en fonction de la généralisation partielle ou non du procédé BioTJet pour atteindre les objectifs de ReFuel-EU en 2050 


#### Cette fonction marche ! (commentaire à effacer)
def impact_recolte_capacité_sequestration(productivité_nette, récolte_totale): 
    
    variation_stock_bois_aérien = productivité_nette - récolte_totale  # de la partie aérienne de l'arbre
    
    variation_capacité_séquestration_aerienne_CO2 = variation_stock_bois_aérien * param_foret["taux_humidité_bois_vert"]/100 \
    *param_foret["taux_carbone_bois_sec"]/100 * param_foret["ratio_masse_C02_C"]
    
    variation_capacité_séquestration_totale_CO2 = variation_capacité_séquestration_aerienne_CO2 * \
    param_foret["rapport_capacité_sequestration_sol_aerien"]   # en prenant en compte la partie du sol de l'arbre
    return variation_capacité_séquestration_totale_CO2

# fonction qui détermine la productivité de la forêt française et la mortalité, pour l'année spécifiée en entrée 
# en fonction du coefficient coeff_bonne_pratique qui quantifie l'amélioration des pratiques sylvicoles 

#### Cette fonction marche pour 2030,2050 et 2100 (commentaire à supprimmer)
def impact_bonne_pratique_capacité_sequestration(année, productivité):
    
    coefficient_bonne_pratique_année = param_foret["coefficient_bonne_pratique_2025"]+(param_foret["coefficient_bonne_pratique_2100"] \
    -param_foret["coefficient_bonne_pratique_2025"])/((param_foret["année_bonne_pratique_max"] \
    -param_foret["année_début_bonne_pratique"]))*(année-param_foret["année_début_bonne_pratique"])
                                                                                
    productivité_bonne_pratique = productivité*coefficient_bonne_pratique_année

    return productivité_bonne_pratique

# fonction qui détermine la capacité de séquestration carbone de la forêt française en prenant en compte le changement climatique
# (avec un impact linéaire ou non), l'amélioration des pratiques sylvicoles et la généralisation (en %) du procédé BioTjet 
# pour atteindre les objectifs de ReFuel-EU en 2050. A mettre en regard des objectifs de séquestration
# carbone de la SNBC 3 à horizon 2050.
def impact_total_sequestration(année,beta,généralisation):
    variation_sequestration_carbone = 0
    besoin_masse_bois_supplémentaire = 0 
    
    productivité, mortalité = impact_changement_climatique_foret(année,beta) # résultats en m3/an
    
    productivité_bonne_pratique = impact_bonne_pratique_capacité_sequestration(année,productivité) # résultats en m3/an
    
    besoin_masse_bois_supplémentaire = besoin_biomasse_generalisation(généralisation) # résultats en Mt
    
    récolte_totale = param_foret["récolte_totale_2014_2022"]*param_foret["densité_bois_vert"] + besoin_masse_bois_supplémentaire # résultats en Mt
    
    productivité_nette = param_foret["densité_bois_vert"]*(productivité_bonne_pratique - mortalité) # en Mt/an

    variation_sequestration_carbone = impact_recolte_capacité_sequestration(productivité_nette, récolte_totale)

    
    return variation_sequestration_carbone, besoin_masse_bois_supplémentaire





### PARTIE TEST à SUPRRIMER 

#print(impact_changement_climatique_foret(2100,1.5))
#print(impact_changement_climatique_foret(2050,1.5)[0])
#print(impact_bonne_pratique_capacité_sequestration(2100,impact_changement_climatique_foret(2100,1)[0]))
#print(besoin_biomasse_generalisation(100))
#print(impact_recolte_capacité_sequestration(50.0,74.6))
#print(impact_total_sequestration(2025,1.5,0))
### FIN PARTIE TEST


## faire une partie post-traitement pour tracer de jolis graphiques pour montrer que le code marche ! 
## Par exemple tracer la variation sequestration carbone avec généralisation BioTjet en fonction du temps et sur le même graphe
## mettre la variation sequestration carbone sans projet BioTjet
## aussi tracer la même chose mais juste pour la partie aérienne (si on utilise des déchets de bois)
## + mettre en oeuvre l'effet de de l'arbre qui "repousse" (qui n'est pas dans cette partie de code)
## faire plus d'années que 2030,2050 et 2100 ? A priori, il suffirait de trouver Température dans TRACC des années à ajouter

