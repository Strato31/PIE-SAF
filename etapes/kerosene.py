"""
Paramètres et hypothèses sourcées pour le transport, puis fonctions de calcul des émissions."""

###############################################################
# Stockage des paramètres avec les hypothèses sourcées
###############################################################

param_kerosene = {
    # distance moyenne de transport du kérosène de l'usine jusqu'à l'aéroport
    "distance_transport_kerosene": 1000,  # (km) Distance moyenne de transport du kérosène

    # Ensemble articulé 40 tonnes PTRA – Citerne (source : https://www.webfleet.com/fr_fr/webfleet/blog/emission-co2-camion-km/)
    "emissions_transport_kerosene": 0.074,  # (kgCO2e/t.km) Émissions liées au transport du kérosène par camion citerne
}

##############################################################
# Fonctions de calcul des émissions
##############################################################

def emissions_transport_kerosene(param_kerosene, production_kerosene):
    """Calcule les émissions liées au transport du kérosène jusqu'à l'aéroport.

    Args:
        param_kerosene (dict): Dictionnaire contenant les paramètres liés au transport du kérosène.
        production_kerosene (float): Quantité de kérosène produite (t/an).

    Returns:
        float: Émissions liées au transport du kérosène (tCO2e/an).
    """
    emissions_transport = (production_kerosene *
                           param_kerosene['distance_transport_kerosene'] *
                           param_kerosene['emissions_transport_kerosene']/1000)  # Conversion kgCO2e en tCO2e
    
    return emissions_transport # en tCO2e/an



