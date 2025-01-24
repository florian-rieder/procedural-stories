# Procedural Stories

This repository contains the code and data for my master's thesis on the topic of "Generating interactive fictions with LLMs", under the supervision of Isaac Pante (ISH, SLI, UNIL) and Davide Picca (ISH, SLI, UNIL).

## Installation

Will create a virtual environment and install the dependencies with poetry.

```bash
bash install.sh
```

## Generating a story world

The process of generating a story world is done in the `world_generation.ipynb` notebook.
Define the setting of the story and the language output in the first cell.

The world generation uses large open models using Fireworks serverless inference.
To use it, you need to create an account on Fireworks and get the API key.
Then, you need to create a `.env` file in the root of the repository with the following content:

```
FIREWORKS_API_KEY=your_fireworks_api_key
```

## Discord bot

Create a discord bot account with the Discord Developer Portal and get the token.
Add the following to the `.env` file:

```
DISCORD_TOKEN=your_discord_token
```

Alternatively, you can use the `chat.ipynb` notebook to interact with the system without using the discord bot.

Run the discord bot with

```bash
python run bot.py
```

### Bot Commands

The bot supports the following commands:

- `/start` - Start a new adventure with the current mode
- `/stop` - End the current adventure session
- `/reset` - Clear the bot's memory of the current conversation
- `/set_mode <mode> <session_id>` - Set the conversation mode to either "trivial" or "story"
- `/start_experiment` - Start an experimental session that randomly assigns either trivial or story mode
- `/switch_mode` - Switch between trivial and story modes during an experiment (switch to the second experiment)

After starting a session with `/start` or `/start_experiment`, you can simply type your actions or dialogue in the channel and the bot will respond accordingly.

## Broad lines

Owlready2: "graph backend": logical inferences, triple store. Uses the ontology developed to structure the story world, both for the generation of the world and of the responses during play.

To interface between the graph backend and the LLM, we make the LLM generate JSON objects that describe the state of the story world. The JSON is then converted programmatically into RDF using owlready2 and stored in the graph backend.
The other way around, to enrich the context of the LLM during play, we 