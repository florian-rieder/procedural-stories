FROM python:3.12

WORKDIR /app

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Copy dependency files first (for better caching)
COPY pyproject.toml poetry.lock README.md ./

# Configure Poetry and install dependencies
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi

# Copy the rest of the application
COPY . .

# Run the bot
CMD ["poetry", "run", "python", "src/bot.py"]