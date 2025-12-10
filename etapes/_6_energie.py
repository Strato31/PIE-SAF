"""
Paramètres et hypothèses sourcées pour le calcul des émissions lié à la consommation énergétique et thermique, puis fonctions de calcul des émissions.

Hypothèses sur un mix énergétique pour 2050 :				
    le plus pertinent est de calculer les émissions sur la base du mix électrique cible français en 2050, hypothèse nucléaire "moyenne" (14 EPR2)					
    la production des pays voisins sera entièrement renouvelable. Elle aura une empreinte légèrement plus élevée car le nucléaire à l'empreinte la plus basse.					
    mais on va négliger cet effet. En plus, l'empreinte carbone du solaire aura probablement baissée à cette échéance (amélioration des rendements), ce qui renforce cette simplification					
    les émissions seront sous-estimées à la mise en service, mais devraient être représentatives dès 2035					
    source : base ADEME V23.2 pour nucléaire, éolien, photovoltaïque et hydraulique. Site "Electricity Maps" pour biomasse		

"""

###############################################################
# Stockage des paramètres avec les hypothèses sourcées
###############################################################		

param_mix_2050 = {
    "nucleaire": 0.38,    # Part du nucléaire dans le mix énergétique 
    "eolien": 0.304,      # Part de l'éolien dans le mix énergétique 
    "solaire" : 0.198,    # Part du solaire dans le mix énergétique 
    "hydraulique" : 0.2,  # Part de l'hydraulique dans le mix énergétique 
    "biomasse" : 0.2,     # Part du la biomasse dans le mix énergétique 
}

# Facteur d'émission de chaque filière en gCO2eq/kWh
facteur_emission = {
    "nucleaire" : 5,   # moyenne ADEME / EDF
    "eolien" : 15,
    "solaire" : 32,    # ADEME "Europe"
    "hydraulique" : 6, 
    "biomasse" : 230,  # Electricity Maps
}

##############################################################
# Fonctions de calcul des émissions
##############################################################

#Calcul des émission en CO2 (en gCO2eq) pour une consomation énergétique (en kWh) d'un processus 
def emissions_energetique_processus(conso_energie): 
    emission_mix=0
    for energie in facteur_emission : 
        emission_mix += param_mix_2050[energie] * facteur_emission[energie]

    # Calcul des émissions totales pour le processus de gazeification
    emissions = conso_energie * emission_mix
    return emissions

# Calculs des émissions de CO2 à partir d'une liste de consomation
def emissions_energie_totale(consos_energies):
    emissions_tot = 0
    emissions = []
    for conso in consos_energies :
        emissions_processus = emissions_energetique_processus (conso)
        emissions.append(emissions_processus)
        emissions_tot += emissions_processus
    
    emissions.append(emissions_tot)
    return emissions

# Calcul des émissions liées à la production de chaleur (en gCO2eq) pour une consomation thermique (en MJ) d'un processus
'''
hypothèse : on considère que la chaleur résiduelle générée par le procédé Fischer-Tropsch est réinjectée dans la phase de torréfaction et est suffisante pour l'assurer 							
Source de cette chaleur : injection d'eau dans le réacteur Fischer-Tropsch pour refroidir le catalyseur et le conserver dans la bonne plage de température							
d’où génération de vapeur d'eau (680 kt/an) dont la chaleur va être utilisée pour apporter des calories aux phases de torréfaction et de création de syngaz							
'''
def verif_hypothèse(consos_thermiques):
    # on vérifie que la consommation thermique totale est inférieure à la chaleur récupérable
    conso_therm_totale = 0

    for conso_therm in consos_thermiques :
        conso_therm_totale += conso_therm # La consommation thermique est positive pour les étapes qui consomment de l'énergie et négative si elle en produit.
    if conso_therm_totale <= 0:
        return True
    else:
        return False