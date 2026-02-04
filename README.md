# PIE-SAF

<img width="979" height="697" alt="Capture d&#39;écran 2025-12-10 113726" src="https://github.com/user-attachments/assets/d1ca5bff-e6a6-48c2-926e-e78b1d7a69fa" />
___________________________

Diagramme présentant les données d'entrée et de sortie pour chaque module "étape" du code. En plus de ces données, les modules étape prendront également en entrée une série de variables et d'hypothèses qu'on ne détaille pas ici. Attention : ce ne sont pas les entrées et sorties physiques de ces étapes, mais bien les arguments et retours des fonctions qui composent chaque module. 
Par exemple, l'hydrogène est une sortie pour FT car l'algorithme calcule la quantité d'hydrogène nécessaire à produire par l'électrolyseur.

Les entrées/sorties peuvent être résumées comme suit :

**BIOMASSE**
- Entrées : type/masse/humidité des biomasses utilisées
- Sorties : élec, chaleur, masse_biomasse_seche

**GASIFICATION**
- Entrées : masse_biomasse_seche, oxygene
- Sorties : élec, chaleur, CO2, quantités CO et H2 dans le syngas, déchets

**FT**
- Entrées : quantités CO et H2 dans le syngas
- Sorties :  élec, chaleur, H2 à produire par électrolyseur, kérosène produit, autres produits liquides

**ELECTROLYSE**
- Entrées : eau, quantité H2 à produire
- Sorties : élec

**ENERGIES**
- Entrées : consommations chaleur et élec
- Sortie : émissions
________________________________________

UNITES : 
- masse : en tonnes
- électricité : kWh
- énergie : MJ (positive si consommée, négative si produite)
- --> Conversion : 1 kWh = 3.6 MJ

________________________________________

Etapes a inclure :
- convoyage et broyage du bois
- mix électrique (hypothèses)
- origine du bois
- données E-CHO
- consommation énergétique production
- oxygène
- chaleur (pour l'instant ignorée)
- consommation électrique fonctionnement
- transport du bois
- CO2
- raffinage
    - rendement carbone
    - fonctionnement pompes à eau
        - transfert de vapeur vers l'extérieur
- electrolyseur (très long oscour) (H2)



LA SUITE :
- permettre de faire les calculs dans l'autre sens (biomasse->kérosène et kérosène->biomasse)
- créer format dictionnaire de données par projet
- rendre globale les variables qui le sont
- ...

**Foret**

La partie "foret.py" a pour but d'effectuer un travail prospectif consistant à estimer la capacité de séquestration carbone
de la forêt française à différentes horizons (2030,2050,2100)

la première partie du code comporte un dictionnaire où l'on trouve un certain nombre de données issues principalement de 
l'inventaire forestier 2024 de l'IGN, mais aussi de Météo France pour la trajectoire TRACC... Ces valeurs pourraient être  
amenées à être modifiées si des données plus récentes sont disponibles.

Ensuite vient les fonctions

La fonction "impact_changement_climatique_foret" détermine la productivité et la mortalité de la forêt française, pour l'année spécifiée en entrée. Le paramètre béta quantifie l'impact du changement climatique sur l'état de la forêt. Les résultats sont donnés en Mm3/an.

La fonction  "besoin_biomasse_generalisation" calcule la masse de biomasse nécessaire en fonction de la généralisation partielle 
ou totale du procédé BioTjet pour atteindre les objectifs de ReFuel-EU en 2050.
En cas de généralisation, en France, besoin de 3500 kt de SAF. Les résultats sont en Mt de bois.

La fonction "impact_recolte_capacité_sequestration" calcule la variation de la capacité totale de séquestration carbone de la forêt française (en MtCO2/an) en fonction de la généralisation partielle ou non du procédé BioTJet pour atteindre les objectifs de ReFuel-EU en 2050.

La fonction "impact_bonne_pratique_capacité_sequestration" détermine la productivité de la forêt française et la mortalité, pour l'année spécifiée en entrée en fonction du coefficient coeff_bonne_pratique qui quantifie l'amélioration des pratiques sylvicoles. Les résultats sont donnés en Mm3/an.

la fonction "impact_total_sequestration" détermine la capacité de séquestration carbone de la forêt française en prenant en compte le changement climatique (avec un impact linéaire ou non), l'amélioration des pratiques sylvicoles et la généralisation (en %) du procédé BioTjet 
pour atteindre les objectifs de ReFuel-EU en 2050. A mettre en regard des objectifs de séquestration carbone de la SNBC 3 à horizon 2050.
Cette fonction utilise la plupart des autres fonctions de ce fichier python. Les résultats sont en Mt de CO2. 




