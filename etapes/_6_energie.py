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


