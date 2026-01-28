# PIE-SAF
<img width="1088" height="698" alt="image" src="https://github.com/user-attachments/assets/28f3b4d7-7b81-400b-ac4c-fe46b5fc0a16" />
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
- emissions carbone : tCO2e
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
- rendre globales les variables qui le sont
- faire un main fonctionnel

------------------------------------------

Détails des étapes :

**Partie 7 : Compression des gaz**
La partie compression des gaz s'organise en deux parties : une partie de donné physico chimique et une partie du calcul de l'énergie consommée.

La partie zone de donnée :
un dictionnaire *carac_physico_chimiques* regroupant les informations physico-chimique par gaz. 
Les données du dictionnaires sont tirés de celles de l'excel des shifters, en considérant les gaz parfaits et aux conditions de référence 288,15K et 1 bar.

La partie calcul des émissions : 
*param_temp_variable* : calcul les caractéristiques physico-chimique des gaz en fonction de la température 
*calcul_echauffement_isenthropique* : ces calculs ne sont utiles que dans le cas où E-CHO/BioTJet serait reconverti et fabriquerait du e-kérosène, le carbone venant de captation de CO2 : pas pris en compte pour l'instant
*compression_isentropique* : Renvoie la temperature de la compression isentropique pour passer de la pression P1 (en bar) à la pression P2 (en bar).
*conso_compression* : Renvoie la consommation électrique (en MWh) pour comprimer une masse de gaz (en kg) de la pression P1 (en bar) à la pression P2 (en bar) à la température initiale T0_K.
*conso_compression_syngaz* : Renvoie la consommation électrique (en MWh) pour comprimer le syngas (en kg), calcul spécifique car il prend en compte les trois gaz. procédure de calcul de l'échauffement du mélange : calcul de l'échauffement de chacun des gaz, puis calcul de la T° moyenne et du Cp moyen pondéré par la composition, enfin calcul de la puissance moyenne absorbée. 

Le processus de calcul suit les étapes détaillées dans le document technique, dans un premier temps on calcul de manière itérative l'échauffement thermique lié à la compression puis l'échauffement réel et enfin l
