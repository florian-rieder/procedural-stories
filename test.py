from generator.parsers.locations import parse_locations

from graph_locations import display_location_relationships


text = """**Création du monde**

Je vais commencer par réfléchir à voix haute au monde et à sa cohérence. L'histoire se déroule dans la Normandie viking du 9e siècle, à l'époque de l'exploration et de la colonisation de la Normandie par les Vikings. Je veux créer un monde cohérent et narrativement intéressant.

Les Vikings sont des navigateurs et des guerriers, ils ont besoin de villes côtières pour commercer et se ravitailler, mais aussi de forêts denses pour se cacher et se protéger de leurs ennemis. Les campements vikings sont des lieux de rassemblement et de préparation pour les batailles à venir.

Je vais créer des lieux qui reflètent ces besoins et ces caractéristiques. Je vais également créer des lieux de transition pour relier les lieux majeurs.

**Liste des lieux**

Voici la liste des lieux :

- **Rouen** [ami]: La ville côtière la plus importante de la Normandie, où les Vikings se rassemblent pour commercer et se ravitailler. (Bayeux, Caen)
- **Forêt de la Hague** [neutre]: Une forêt dense et mystérieuse où les Vikings se cachent pour se protéger de leurs ennemis. (Rouen, Cherbourg)
- **Campement de la Rivière** [ami]: Un campement viking situé près d'une rivière, où les Vikings se rassemblent pour préparer les batailles à venir. (Rouen, Forêt de la Hague)
- **Bayeux** [neutre]: Une ville côtière importante, où les Vikings se rassemblent pour commercer et se ravitailler. (Rouen, Cherbourg)
- **Cherbourg** [hostile]: Une ville côtière ennemie, où les Vikings se battent pour conquérir et contrôler les routes maritimes. (Rouen, Bayeux)
- **Route de la Côte** [neutre]: Une route côtière qui relie les villes côtières de la Normandie, où les Vikings se déplacent pour commercer et se ravitailler. (Rouen, Bayeux, Cherbourg)
- **Colline de la Bataille** [hostile]: Une colline qui domine la plaine de la bataille à venir, où les Vikings se préparent pour la bataille. (Campement de la Rivière, Forêt de la Hague)

Ces lieux créent un monde cohérent et narrativement intéressant, où les Vikings se rassemblent pour commercer, se ravitailler et se préparer pour les batailles à venir. Les lieux de transition relient les lieux majeurs et créent des chemins pour les personnages."""


locs = parse_locations(text)

for loc in locs:
    print(loc)

display_location_relationships(locs)