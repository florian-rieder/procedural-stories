import asyncio
from generator.models import model

from generator.story.converse import StoryConverse
from generator.trivial.converse import TrivialConverse


first_message = """
Vous vous trouvez dans une communauté isolée, barricadée et surveillée, où quelques
dizaines de survivants comme vous ont trouvé refuge. Vous avez perdu des proches lors de
l'épidémie et vous êtes déterminé à trouver un moyen de vaincre les Errants et de
reconstruire votre monde. Vous avez reçu une mission, et vous savez que votre seul
espoir de survie réside dans la découverte d'un remède contre l'épidémie. Vous devez
partir à la recherche d'informations sur ce remède, mais pour cela, vous devrez quitter
la sécurité relative de votre communauté et affronter les dangers du monde extérieur.
""".strip()

setting = "Post-apocalypse zombie mondiale, 1 an après le début de l'épidémie"

ontology_file = "story_poptest70b.rdf"

language = "french"


trivial_converse = TrivialConverse(model, first_message, setting, language)

story_converse = StoryConverse(
    model,
    first_message,
    setting,
    language,
    ontology_file,
)

current_chain = story_converse


async def main():
    while True:
        message = input("You: ")

        if message.strip() == "":
            continue

        if message.lower() == "quit" or message.lower() == "exit":
            break

        response = await current_chain.converse(message)
        print("Game:", response)


if __name__ == "__main__":
    asyncio.run(main())
