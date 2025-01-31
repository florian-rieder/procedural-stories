# Procedural Stories

This repository contains the code and implementation for my master's thesis titled "Machines à Histoires: Les LLM comme partenaires en fiction interactive", conducted under the supervision of Isaac Pante (ISH, SLI, UNIL) and Davide Picca (ISH, SLI, UNIL).

## Overview

This project explores the generation of interactive fiction using Large Language Models (LLMs) and semantic web technologies. The system combines:

- **Semantic Knowledge Base**: Uses [Owlready2](https://owlready2.readthedocs.io/) as a graph backend for logical inferences and triple store
- **Story World Generation**: Automated creation of rich, consistent story worlds using LLMs
- **Interactive Interface**: Available through both Discord bot, Jupyter notebook (legacy) and CLI interfaces


### Key Components

- **`ontology/`**: Contains the foundational ontology that defines the structure and rules for all story worlds
- **`world_generation/`**: Tools and notebooks for creating new story worlds using LLMs
- **`generator/`**: Core conversation systems implementing different interaction modes:
  - `story/`: Story-aware system that uses the ontology and world model
  - `trivial/`: Basic conversation system for baseline comparison
- **Interfaces**:
  - `cli.py`: Main command-line interface for interacting with the system
  - `bot.py` & `cogs/`: Discord bot implementation for running experiments
  - `chat.ipynb`: Legacy notebook interface (may be outdated)
- **`analysis/`**: Tools for analyzing and visualizing results
- **`data/`**: Experimental data and results

Note: While `chat.ipynb` was initially used to develop the interactive gameplay loop, this functionality has since been moved to `generator/story/converse.py` and `generator/trivial/converse.py`. The notebook may be outdated.


## Installation

The installation script will create a virtual environment and install all dependencies with poetry. Python 3.11 is required.

```bash
bash install.sh
```

## Story World Generation

The process of generating a story world is done in the [`world_generation.ipynb`](world_generation.ipynb) notebook. You'll need to:

1. Define the setting of the story and the language output in the first cell
2. The world generation uses large open models using Fireworks serverless inference
3. Create an account on Fireworks and get the API key
4. Create a `.env` file in the root of the repository with:

```
FIREWORKS_API_KEY=your_fireworks_api_key
```

## Interactive Story Mode

### Option 1: Discord Bot

1. Create a discord bot account with the [Discord Developer Portal](https://discord.com/developers/applications) and get the token
2. Add to your `.env` file:
```
DISCORD_TOKEN=your_discord_token
```

Run the bot with:
```bash
python bot.py
```

#### Bot Commands

The bot supports the following commands:

- `/start` - Start a new adventure with the current mode
- `/stop` - End the current adventure session
- `/reset` - Clear the bot's memory of the current conversation
- `/set_mode <mode> <session_id>` - Set the conversation mode to either "trivial" or "story"
- `/start_experiment` - Start an experimental session that randomly assigns either trivial or story mode
- `/switch_mode` - Switch between trivial and story modes during an experiment (switch to the second experiment)

After starting a session with `/start` or `/start_experiment`, you can simply type your actions or dialogue in the channel and the bot will respond accordingly.

### Option 2: Jupyter Notebook
Alternatively, you can use [`chat.ipynb`](chat.ipynb) to interact with the system without using the Discord bot.

## Technical Architecture

The system uses a hybrid approach combining semantic web technologies with LLMs:

- **Owlready2 Backend**: Acts as the "graph backend" for logical inferences and triple store. Uses the ontology developed to structure the story world, both for the generation of the world and the responses during play.

- **LLM-Graph Interface**: 
  - To interface between the graph backend and the LLM, we make the LLM generate JSON objects that describe the state of the story world
  - The JSON is then converted programmatically into RDF using owlready2 and stored in the graph backend
  - During play, we enrich the context of the LLM with information from the graph

## Project Structure

```
.
├── ontology/                     # Core ontology definitions
│   └── story_world_ontology.rdf  # Base story world ontology (T-box)
│
├── worlds/                       # Generated story worlds
│   ├── story_world_fantasy.rdf   # Example fantasy world, used for the experiments
│   └── ...                       # Additional story worlds
│
├── generator/                    # Core conversation generation systems
│   ├── story/                    # Story-aware conversation system
│   │   ├── converse.py           # Main story conversation logic
│   │   └── ...                   # Additional story mode components
│   ├── trivial/                  # Basic conversation system
│   │   ├── converse.py           # Main trivial conversation logic
│   │   └── ...                   # Additional trivial mode components
│   └── models.py                 # Shared model definitions
│
├── analysis/                     # Analysis and visualization tools
│   ├── visualize_results.ipynb   # Results analysis
│   └── visualize_graph.py        # Graph visualization utilities
│
├── data/                         # Experimental data
│   ├── raw_results/              # Raw conversation logs
│   └── processed_results/        # Processed experimental data
│
├── bot.py                        # Discord bot implementation
├── cogs/                         # Discord bot command modules
├── chat.ipynb                    # Interactive notebook interface (legacy)
└── world_generation.ipynb        # Main notebook for world generation
```
