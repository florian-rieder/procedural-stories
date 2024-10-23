from owlready2 import *

from ontology_manager import list_onto, add_location

# Create an ontology
onto = get_ontology("http://www.florianrieder.com/story.owl")

with onto:
    # Class Definitions
    class Entity(Thing):
        label = "Entité"

    class Character(Entity):
        """Represents a character in the story, such as a player or NPC."""
        label = "Personnage"

    class Player(Character):
        label = "Joueur"

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

    class Consequence(Thing):
        label = "Conséquence"

    class Emotion(Thing):
        label = "Emotion"

    class Goal(Thing):
        label = "Objectif"

    class PersonalityTrait(Thing):
        label = "Trait de personnalité"

    class Role(Thing):
        label = "Role"

    class Condition(Thing):
        label = "Condition"

    class Information(Thing):
        label = "Information"

    # Object Properties

    class containsCharacter(Location >> Character):
        """Indicates that a location contain a characters."""
        label = "contient le personnage"

    class containsItem(Location >> Item):
        """Indicates that a location contains an item"""
        label = "contient l'objet"

    class hasActionPlan(Character >> Action):
        """Indicates that a character has a plan."""
        label = "planifie"

    class hasConsequences(Event >> Consequence):
        """Indicates that an action has a consequence"""
        label = "a comme conséquence"

    class hasEffectOn(Action >> Entity):
        """Indicates that a an action has an effect on an entity"""
        label = "a un effet sur"

    class hasEmotionalState(Character >> Emotion):
        """Indicates that a character has an emotional state"""
        label = "a l'état emotionnel"

    class hasGoal(Entity >> Goal):
        """Indicates that a character has a goal"""
        label = "a comme objectif"

    class hasPersonalityTrait(Character >> PersonalityTrait):
        """Indicates that a character has a personality trait"""
        label = "a le trait de personnalité"

    # Character relationships
    class hasFriendshipWith(Character >> Character, SymmetricProperty, TransitiveProperty):
        label = "a une amitié avec"

    class hasAllegiance(Character >> Faction, FunctionalProperty, TransitiveProperty):
        label = "a une allégeance à"

    class isEnemyWith(Character >> Character, IrreflexiveProperty, SymmetricProperty):
        label = "est ennemi de"

    class loves(Character >> Character):
        label = "aime"
        # No restrictions on love

    class hasFamilyTieWith(Character >> Character, SymmetricProperty, TransitiveProperty):
        label = "a un lien familial avec"

    class hasRivalryWith(Character >> Character, IrreflexiveProperty, SymmetricProperty):
        label = "est rival de"

    class hasRole(Character >> Role):
        label = "a le rôle de"

    class hasTrigger(Event >> Condition):
        label = "est déclenché par"

    class involvesCharacter(Event >> Character):
        label = "implique le personnage"

    # A Character can only be in one Location
    class isAtLocation(Character >> Location, FunctionalProperty):
        label = "est situé à"
        inverse_property = containsCharacter
    
    class hasVisited(Entity >> Location):
        label = "a visité"

    class wasVisitedBy(Location >> Entity):
        label = "a été visité par"
        inverse_property = hasVisited

    class knows(Entity >> Entity):
        """Does entity A know entity B ?"""
        label = "connaît"

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
    #
    # class isSouthOf(Location >> Location):
    #     inverse_property = isNorthOf

    # class isWestOf(Location >> Location):
    #
    # class isEastOf(Location >> Location):
    #     inverse_property = isWestOf

    class ownedByCharacter(Item >> Character):
        label = "est possédé par"

    class ownsItem(Character >> Item):
        label = "possède"
        inverse_property = ownedByCharacter

    class performedByCharacter(Action >> Character):
        label = "est exécuté par"

    class requiresItem(Action >> Item):
        label = "requiert l'objet"


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
    # from generator.models import LocationData
    # loc = LocationData(name="Raven's thorpe",
    #                    description="La ville côtière la plus importante de la Normandie, où les Vikings se rassemblent pour commercer et se ravitailler.",
    #                    relationships=["Rouen", "Rivière magique"],
    #                    stance='friendly')

    # add_location(onto, loc)

    list_onto(onto)

    # # Save the ontology to a file if needed
    onto.save(file="story_ontology2.owl", format="rdfxml")
