FROM python:3.12

WORKDIR /app

# Install Poetry with increased timeout and configure it
RUN pip install --default-timeout=100 poetry && \
    poetry config virtualenvs.create false && \
    poetry config installer.parallel false

# Copy only dependency files first to leverage Docker cache
COPY pyproject.toml ./

# Install dependencies with increased timeout
RUN pip install --default-timeout=100 certifi && \
    poetry install --no-root --no-interaction

# Copy the rest of the application
COPY . .

# Run the bot
CMD ["poetry", "run", "python", "bot.py"]