# PIE-SAF
________________________________________
--BIOMASSE--
- Entrées : type/masse/humidité des biomasses utilisées
- Sorties : élec, chaleur, masse_biomasse_seche

--GASIFICATION--
- Entrées : masse_biomasse_seche, oxygene
- Sorties : élec, chaleur, CO2, quantités CO et H2 dans le syngas, déchets

--FT--
- Entrées : quantités CO et H2 dans le syngas
- Sorties :  élec, chaleur, H2 à produire par électrolyseur, kérosène produit, autres produits liquides

--ELECTROLYSE--
- Entrées : eau, quantité H2 à produire
- Sorties : élec

--ENERGIES--
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

--> à grouper pour certaines, réfléchir comment organiser les données qui servent sur plusieurs étapes

