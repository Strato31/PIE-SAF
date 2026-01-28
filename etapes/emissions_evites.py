"""
Partie calculant les émissions évitées par le projet en lien avec la directive RED II. 

"""

### Paramètres RED II
emissions_fossiles = 94  # gCO2eq/MJ pour le kérosène fossile
conversion_kwh_mj = 3.6  # 1 kWh = 3.6 MJ

## Fonction de calcul 

def calcul_emissions_evitees(total_emissions_projet_tco2, production): 

    ## Pourcentage de réduction des émissions de GES par rapport au fossile :

    reduction = (emissions_fossiles - total_emissions_projet_tco2) / emissions_fossiles * 100   # en %

    ## Quantité totale évitée par an :

    emissions_evites = production * (emissions_fossiles - total_emissions_projet_tco2) / 1000   # en tCO2e/an

    print(f"Réduction des émissions de GES par rapport au fossile : " f"{reduction:.2f} %")
    print(f"Émissions évitées par an : " f"{emissions_evites:.2f} tCO2e/an")

