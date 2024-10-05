from owlready2 import *

from ontology_manager import list_onto, add_location
from generator.models import LocationData

# Create an ontology
onto = get_ontology("http://www.florianrieder.com/story.owl")

with onto:
    # Class Definitions
    class Entity(Thing):
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
        pass

    class Consequence(Thing):
        pass

    class Emotion(Thing):
        pass

    class Goal(Thing):
        pass

    class PersonalityTrait(Thing):
        pass

    class Role(Thing):
        pass

    class Condition(Thing):
        pass

    class Information(Thing):
        pass

    # Object Properties

    class containsCharacter(Location >> Character):
        """Indicates that a location contain a characters."""
        pass

    class containsItem(Location >> Item):
        """Indicates that a location contains an item"""
        pass

    class hasActionPlan(Character >> Action):
        """Indicates that a character has a plan."""
        pass

    class hasConsequences(Event >> Consequence):
        """Indicates that an action has a consequence"""
        pass

    class hasEffectOn(Action >> Entity):
        """Indicates that a an action has an effect on an entity"""
        pass

    class hasEmotionalState(Character >> Emotion):
        """Indicates that a character has an emotional state"""
        pass

    class hasGoal(Entity >> Goal):
        """Indicates that a character has a goal"""
        pass

    class hasPersonalityTrait(Character >> PersonalityTrait):
        """Indicates that a character has a personality trait"""
        pass

    class hasRelationshipWith(Character >> Character):
        pass

    class hasRole(Character >> Role):
        pass

    class hasTrigger(Event >> Condition):
        pass

    class involvesCharacter(Event >> Character):
        pass

    # A Character can only be in one Location
    class isAtLocation(ObjectProperty, FunctionalProperty):
        domain = [Character]
        range = [Location]
        inverse_property = containsCharacter

    class knowsInformation(Character >> Information):
        rdfs.domain = Character
        rdfs.range = Information

    class isLinkedToLocation(ObjectProperty, SymmetricProperty):
        domain = [Location]
        range = [Location]

    class ownedByCharacter(Item >> Character):
        pass

    class ownsItem(Character >> Item):
        inverse_property = ownedByCharacter

    class performedByCharacter(Action >> Character):
        pass

    class requiresItem(Action >> Item):
        pass

    class isFactionMember(Character >> Faction):
        pass

    class hasMember(Faction >> Character):
        inverse_property = isFactionMember

    class isControlledByFaction(Location >> Faction):
        pass

    class hasControlOfLocation(Faction >> Location):
        inverse_property = isControlledByFaction

    # Data properties

    class hasStanceTowardsPlayer(DataProperty, FunctionalProperty):
        domain: [Entity]
        range: [str]

    class hasName(DataProperty, FunctionalProperty):
        domain: [Thing]
        range: [str]

    class hasDescription(DataProperty, FunctionalProperty):
        domain: [Thing]
        range: [str]

    # Create neutral faction
    neutral_faction = Faction("Neutre")
    neutral_faction.hasStanceTowardsPlayer = 'neutre'
    

    # Test
    # loc = LocationData(name="Raven's thorpe",
    #                    description="La ville côtière la plus importante de la Normandie, où les Vikings se rassemblent pour commercer et se ravitailler.",
    #                    relationships=["Rouen", "Rivière magique"],
    #                    stance='friendly')

    # add_location(onto, loc)

    list_onto(onto)

    # # Save the ontology to a file if needed
    # onto.save(file="story_ontology2.owl", format="rdfxml")
