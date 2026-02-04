"""
Partie présentant la calcul complet des émissions évitées par le projet BioTJet d'E-CHO par rapport à des carburants fossiles,
en suivant deux méthodes principales : 
- La méthode RED II (directive européenne sur les énergies renouvelables)
- La méthode ACV complète (Analyse du Cycle de Vie)
Le projet Elyse raisonne suivant cette directive RED II. Le groupe local des Shifters de Pau raisonne  
en termes d'ACV. 
"""

### Kérosène fossile de référence
'''
Les émissions éitées sont calculées par rapport à un kérosène fossile de référence. 
Deux sources de facteurs d'émission sont utilisées pour rester cohérents avec les méthodes citées ci-dessus. 
- Valeurs de l'ADEME (Base ADEME V23.2)
- Valeurs de la directive RED II (Académie Technologies)

Les paramètres utilisés sont : 
- Le PCI : Pouvoir Calorifique Inférieur, en MJ/kg
- Les émissions amont, en kgCO2eq/kg
- Les émissions liées à la combustion, en kgCO2eq/kg
'''

kerosene_fossile_ADEME = {
    "PCI" : 43.105,                 # en MJ/kg
    "emissions_amont" : 0.661,      # en kgCO2eq/kg
    "emissions_combustion" : 3.15,   # en kgCO2eq/kg
    "emissions_totales" : 3.811     # en kgCO2eq/kg, somme des deux facteurs précédents
}

kerosene_fossile_REDII = {
    "PCI" : 44.0,                    # en MJ/kg
    "emissions_amont" : None,        # en kgCO2eq/kg, à calculer
    "emissions_combustion" : None,   # en kgCO2eq/kg, à calculer
 }

naphta_fossile_REDII = {
    "PCI" : 42,                     # en MJ/kg
    "emissions_amont" : 0.661,      # en kgCO2eq/kg
    "emissions_combustion" : 3.300, # en kgCO2eq/kg
    "emissions_totales" : 3.961     # en kgCO2eq/kg, somme des deux facteurs précédents
}

### Hypothèses RED II
'''
La directice RED II fixe plusieurs  simplifées pour le calcul des émissions évitées :
- On raisonne sur l'ensemble des coproduits, donc ici sur le kérosène et le naphta. 
- On ne prend pas en compte les émissions liées à la production d'électricité décarbonée. 
- On ne prend pas en compte les émissions de combustion du biocarburant (considérées comme neutres, le carbone a déjà été consommé précédemment).
- On ne prend pas en compte le stockage du carbone forestier (dans la biomasse).
- On considère uniquement la logistique (bois et carburant). 
'''


### Données Elyse

'''
Valeurs des émissions évitées revendiquées par Elyse pour différents projets, 
en tCO2e/an.
'''
emissions_evitees_Elyse = {
    "siteECHO" : 430000,  # tCO2e/an, total revendiqué par Elyse pour le site ECHO
    "BioTJet" : 348000,   # tCO2e/an, total revendiqué par Elyse pour le projet BioTJet
    "eM-Lacq"  : 274000   # tCO2e/an, total revendiqué par Elyse pour le projet eM-Lacq
    }


''' 
Valeurs d'objectifs de production par année.
'''
objectifs_production_2025 = {
    "bio_kerosene" : 87000, # en tonnes/an
    "naphta"       : 28000,  # en tonnes/an
}


### Paramètre de conversion 
conversion_kwh_mj = 3.6  # 1 kWh = 3.6 MJ


######################################################################
## Fonction de calcul 
######################################################################


def calcul_emissions_evitees(total_emissions_projet_tco2, production_biokerosene, production_naphta): 

    # Calcul des émissions fossiles de référence (base ADEME):
    emissions_fossiles_kerosene = kerosene_fossile_ADEME["emissions_totales"]  * production_biokerosene   # en kgCO2eq/an
    emissions_fossiles = emissions_fossiles_kerosene + naphta_fossile_REDII["emissions_totales"] * production_naphta   # en kgCO2eq/an

    ## Pourcentage de réduction des émissions de GES par rapport au fossile :

    reduction = (emissions_fossiles - total_emissions_projet_tco2) / emissions_fossiles * 100   # en %

    ## Quantité totale évitée par an :

    emissions_evites =  (emissions_fossiles - total_emissions_projet_tco2)   # en tCO2e/an

    print(f"Réduction des émissions de GES par rapport au fossile : " f"{reduction:.2f} %")
    print(f"Émissions évitées par an : " f"{emissions_evites:.2f} tCO2e/an")

