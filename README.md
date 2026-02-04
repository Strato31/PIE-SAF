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

## Détails des étapes :

---
**Partie 7 : Compression des gaz**

Le module de compression des gaz est organisé en deux parties principales :

1. ***Gestion des données physico-chimiques**  
2. ***Calcul de la consommation énergétique**

***Partie données***

Les propriétés physico-chimiques des gaz sont regroupées dans une structure de type dictionnaire :

- `carac_physico_chimiques`  
  Ce dictionnaire contient l’ensemble des caractéristiques physico-chimiques associées à chaque gaz.

Les valeurs utilisées proviennent du fichier Excel des Shifters, en considérant :

- un comportement de gaz parfait,
- des conditions de référence de **288,15 K** et **1 bar**.

***Partie calcul***

Plusieurs fonctions permettent de réaliser les calculs thermodynamiques et d’estimer la consommation énergétique liée à la compression.

*param_temp_variable* : Calcule les caractéristiques physico-chimiques des gaz en fonction de la température. Cette fonction implémente les équations des capacités calorifiques propres à chaque gaz. Elle calcule également : le coefficient adiabatique γ (gamma), la constante spécifique du gaz Rs, car ces paramètres dépendent de Cp et sont nécessaires aux calculs ultérieurs.

*calcul_echauffement_isentropique* : Calcule l’échauffement isentropique lors d’une compression allant de la pression P1 à la pression P2, à partir d’une température initiale T0 (K). Cette fonction s’appuie sur l’application de la **loi de Laplace** pour les gaz parfaits.

*compression_isentropique* : Renvoie la température finale obtenue après une compression isentropique permettant de passer de la pression P1 (bar) à la pression P2 (bar). Le calcul est réalisé de manière itérative afin de déterminer précisément l’échauffement lié à la compression du gaz.

*conso_compression* : Calcule la consommation électrique (en **MWh**) nécessaire pour comprimer une masse de gaz donnée (en **kg**) de la pression P1 (bar) à la pression P2 (bar) à partir d’une température initiale T0_K. La consommation électrique est estimée à partir de l’échauffement réel. Les équations détaillées utilisées pour ce calcul sont documentées dans le fichier Excel de référence.

*conso_compression_syngaz* : Calcule la consommation électrique (en **MWh**) nécessaire à la compression du syngaz. renvoie la consommation électrique (en MWh) nécessaire pour comprimer du syngaz (en kg). Il s’agit d’un calcul spécifique prenant en compte les trois gaz constituant le mélange. La procédure de calcul est la suivante : calcul de l’échauffement pour chacun des gaz, détermination de la température moyenne du mélange, calcul d’un Cp moyen pondéré par la composition et calcul de la puissance moyenne absorbée.

Le processus de calcul suit les étapes détaillées dans le document technique associé.
La consommation finale d’énergie liée à la compression d’un gaz est obtenue via la fonction conso_compression. Pour le cas particulier du syngaz, il est nécessaire d’utiliser la fonction conso_compression_syngaz, car ce dernier étant composé de plusieurs gaz, il faut pondérer les échauffements de chacun d’eux par leur proportion massique.
