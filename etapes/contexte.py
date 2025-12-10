"""Hypothèses de contexte pour les calculs des émissions liées à la biomasse.
Facteurs importants :
- Mix énergétique du pays de production
- Infrastructures disponibles
- Réglementations environnementales
- Pratiques agricoles et forestières
- Conditions climatiques locales
- Distance aux marchés principaux
- Technologies de conversion utilisées
- Échelle de production (petite, moyenne, grande)
- Durabilité des sources de biomasse
- Impacts indirects (changement d'affectation des sols, biodiversité, etc.)
"""
# Exemple de paramètre de contexte
contexte = {
    "mix_énergétique": "éolien_majoritaire",  # Mix énergétique du pays de production
    "infrastructures": "modernes",            # Infrastructures disponibles
    "réglementations": "strictes",            # Réglementations environnementales
    "pratiques_agricoles": "durables",        # Pratiques agricoles et forestières
    "conditions_climatiques": "tempérées",     # Conditions climatiques locales
    "distance_marchés": 500,                  # Distance aux marchés principaux (km)
    "technologies_conversion": "FT_modernes", # Technologies de conversion utilisées
    "échelle_production": "grande",          # Échelle de production (petite, moyenne, grande)
    "durabilité_sources": "certifiées",       # Durabilité des sources de biomasse
    "impacts_indirects": "minimisés"               # Impacts indirects (changement d'affectation des sols, biodiversité, etc.)
}   