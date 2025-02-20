# Confessor Notebook

Confessor Notebook is a CLI application designed for journaling and structured reporting on daily activities.

## Features

- Two modes: **confession** (structured reports) and **meditation** (personal reflections)
- Supports **English (en)** and **Russian (ru)**
- Advanced input validation
- Saves records in an SQLite database
- Event and error logging
- Enhanced CLI interface with Rich (colors, animations, interactive prompts)
- Extended profile configuration with dynamic profile management
- (Stub) Cloud synchronization functionality

## Installation

   ```bash

   git clone https://github.com/looksawful/confessor-notebook.git
   cd confessor-notebook
   pip install typer rich pyyaml
   python confessor-notebook.py --help
  
   ```

## Commands
- **run** – Start a journaling session

  ```bash

  python confessor-notebook.py run -m confession -l ru -p default

  ```

- **report** – Generate a daily or weekly report

Example:

  ```bash

  python confessor-notebook.py report -w -l en -p default

  ```

- **add-question** – Add a new question

Example:

  ```bash

python confessor-notebook.py add-question -l ru -m confession -p default "What new things happened today?"

  ```

- - **list-questions** – Display all questions

Example:

  ```bash

  python confessor-notebook.py list-questions -l en -m meditation -p default

  ```

- **add-profile** – Create a new profile

Example:

  ```bash

  python confessor-notebook.py add-profile work

  ```

- **remove-profile** – Remove an existing profile

Example:

  ```bash

  python confessor-notebook.py remove-profile work

  ```
