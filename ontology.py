from owlready2 import *

from ontology_manager import list_onto, add_location
from generator.models import LocationData

# Create an ontology
onto = get_ontology("http://www.florianrieder.com/story.owl")

with onto:
    # Class Definitions
    class Entity(Thing):
        label = "Entité"
        pass

    class Character(Entity):
        """Represents a character in the story, such as a player or NPC."""
        label = "Personnage"
        pass

    class Player(Character):
        label = "Joueur"
        pass

    class Faction(Entity):
        label = "Faction"

    class Location(Thing):
        label = "Lieu"

    class Item(Entity):
        label = "Objet"

    class Action(Thing):
        """Represents an action that can be performed by a character."""
        label = "Action"
        comment = "Une action que peut prendre un personnage"

    class Event(Thing):
        label = "Evènement"
        pass

    class Consequence(Thing):
        label = "Conséquence"
        pass

    class Emotion(Thing):
        label = "Emotion"
        pass

    class Goal(Thing):
        label = "Objectif"
        pass

    class PersonalityTrait(Thing):
        label = "Trait de personnalité"
        pass

    class Role(Thing):
        label = "Role"
        pass

    class Condition(Thing):
        label = "Condition"
        pass

    class Information(Thing):
        label = "Information"
        pass

    # Object Properties

    class containsCharacter(Location >> Character):
        """Indicates that a location contain a characters."""
        label = "contient le personnage"
        pass

    class containsItem(Location >> Item):
        """Indicates that a location contains an item"""
        label = "contient l'objet"
        pass

    class hasActionPlan(Character >> Action):
        """Indicates that a character has a plan."""
        label = "planifie"
        pass

    class hasConsequences(Event >> Consequence):
        """Indicates that an action has a consequence"""
        label = "a comme conséquence"
        pass

    class hasEffectOn(Action >> Entity):
        """Indicates that a an action has an effect on an entity"""
        label = "a un effet sur"
        pass

    class hasEmotionalState(Character >> Emotion):
        """Indicates that a character has an emotional state"""
        label = "a l'état emotionnel"
        pass

    class hasGoal(Entity >> Goal):
        """Indicates that a character has a goal"""
        label = "a comme objectif"
        pass

    class hasPersonalityTrait(Character >> PersonalityTrait):
        """Indicates that a character has a personality trait"""
        label = "a le trait de personnalité"
        pass

    class hasRelationshipWith(Character >> Character):
        label = "a une relation avec"
        pass

    class hasRole(Character >> Role):
        label = "a le rôle de"
        pass

    class hasTrigger(Event >> Condition):
        label = "est déclenché par"
        pass

    class involvesCharacter(Event >> Character):
        label = "implique le personnage"
        pass

    # A Character can only be in one Location
    class isAtLocation(ObjectProperty, FunctionalProperty):
        label = "est situé à"
        domain = [Character]
        range = [Location]
        inverse_property = containsCharacter
    
    class hasVisited(Entity >> Location):
        label = "a visité"
        pass

    class wasVisitedBy(Location >> Entity):
        label = "a été visité par"
        inverse_property = hasVisited

    class knows(Entity >> Entity):
        """Does entity A know entity B ?"""
        label = "connaît"
        pass

    class knowsInformation(Character >> Information):
        label = "connaît l'information"
        rdfs.domain = Character
        rdfs.range = Information

    class isLinkedToLocation(ObjectProperty, SymmetricProperty):
        label = "est connecté à"
        domain = [Location]
        range = [Location]
    
    # More evolved version of isLinkedToLocation
    # class isNorthOf(Location >> Location):
    #     pass

    # class isSouthOf(Location >> Location):
    #     inverse_property = isNorthOf

    # class isWestOf(Location >> Location):
    #     pass

    # class isEastOf(Location >> Location):
    #     inverse_property = isWestOf

    class ownedByCharacter(Item >> Character):
        label = "est possédé par"
        pass

    class ownsItem(Character >> Item):
        label = "possède"
        inverse_property = ownedByCharacter

    class performedByCharacter(Action >> Character):
        label = "est exécuté par"
        pass

    class requiresItem(Action >> Item):
        label = "requiert l'objet"
        pass


    # Data properties

    class hasStanceTowardsPlayer(DataProperty, FunctionalProperty):
        label = "a une attitude envers le joueur"
        domain: [Entity]
        range: [str]

    class hasName(DataProperty, FunctionalProperty):
        label = "est nommé"
        domain: [Thing]
        range: [str]

    class hasDescription(DataProperty, FunctionalProperty):
        label = "est décrit comme"
        domain: [Thing]
        range: [str]

    

    # Test
    # loc = LocationData(name="Raven's thorpe",
    #                    description="La ville côtière la plus importante de la Normandie, où les Vikings se rassemblent pour commercer et se ravitailler.",
    #                    relationships=["Rouen", "Rivière magique"],
    #                    stance='friendly')

    # add_location(onto, loc)

    list_onto(onto)

    # # Save the ontology to a file if needed
    onto.save(file="story_ontology2.owl", format="rdfxml")
