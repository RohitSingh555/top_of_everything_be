import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from app.database import SessionLocal, engine, Base
import app.users.models
import app.entities.models
import app.rankings.models
from app.entities.models import Entity

STARTER_ENTITIES = [
    # Movies (50)
    {"name": "Interstellar", "type": "movie", "description": "Sci-Fi epic directed by Christopher Nolan"},
    {"name": "The Dark Knight", "type": "movie", "description": "Superhero film directed by Christopher Nolan"},
    {"name": "Inception", "type": "movie", "description": "Sci-Fi heist film directed by Christopher Nolan"},
    {"name": "The Godfather", "type": "movie", "description": "Crime masterpiece by Francis Ford Coppola"},
    {"name": "Pulp Fiction", "type": "movie", "description": "Cult crime film by Quentin Tarantino"},
    {"name": "Fight Club", "type": "movie", "description": "Psychological thriller directed by David Fincher"},
    {"name": "The Matrix", "type": "movie", "description": "Sci-Fi action film by the Wachowskis"},
    {"name": "Goodfellas", "type": "movie", "description": "Crime drama directed by Martin Scorsese"},
    {"name": "The Lord of the Rings: The Return of the King", "type": "movie", "description": "Fantasy epic directed by Peter Jackson"},
    {"name": "Star Wars: Episode V - The Empire Strikes Back", "type": "movie", "description": "Classic Sci-Fi fantasy film"},
    {"name": "Spirited Away", "type": "movie", "description": "Anime masterpiece by Hayao Miyazaki"},
    {"name": "Parasite", "type": "movie", "description": "Thriller directed by Bong Joon-ho"},
    {"name": "Whiplash", "type": "movie", "description": "Drama directed by Damien Chazelle"},
    {"name": "Oppenheimer", "type": "movie", "description": "Biographical drama by Christopher Nolan"},
    {"name": "Blade Runner 2049", "type": "movie", "description": "Sci-Fi thriller directed by Denis Villeneuve"},
    {"name": "Dune: Part Two", "type": "movie", "description": "Sci-Fi epic directed by Denis Villeneuve"},
    {"name": "Spider-Man: Into the Spider-Verse", "type": "movie", "description": "Animated superhero film"},
    {"name": "Wall-E", "type": "movie", "description": "Pixar animated Sci-Fi film"},
    {"name": "Gladiator", "type": "movie", "description": "Historical drama directed by Ridley Scott"},
    {"name": "Alien", "type": "movie", "description": "Sci-Fi horror directed by Ridley Scott"},
    {"name": "The Shawshank Redemption", "type": "movie", "description": "Drama film starring Tim Robbins and Morgan Freeman"},
    {"name": "Forrest Gump", "type": "movie", "description": "Drama starring Tom Hanks"},
    {"name": "Schindler's List", "type": "movie", "description": "Historical drama by Steven Spielberg"},
    {"name": "Saving Private Ryan", "type": "movie", "description": "War drama by Steven Spielberg"},
    {"name": "Jurassic Park", "type": "movie", "description": "Sci-Fi adventure by Steven Spielberg"},

    # Games (50)
    {"name": "The Legend of Zelda: Breath of the Wild", "type": "game", "description": "Open world action-adventure game by Nintendo"},
    {"name": "Elden Ring", "type": "game", "description": "Action RPG by FromSoftware"},
    {"name": "The Witcher 3: Wild Hunt", "type": "game", "description": "Open world RPG by CD Projekt Red"},
    {"name": "Red Dead Redemption 2", "type": "game", "description": "Western epic by Rockstar Games"},
    {"name": "God of War Ragnarök", "type": "game", "description": "Action-adventure game by Santa Monica Studio"},
    {"name": "Grand Theft Auto V", "type": "game", "description": "Open world action game by Rockstar Games"},
    {"name": "Minecraft", "type": "game", "description": "Sandbox game by Mojang"},
    {"name": "Portal 2", "type": "game", "description": "Puzzle-platformer game by Valve"},
    {"name": "Half-Life 2", "type": "game", "description": "First-person shooter by Valve"},
    {"name": "Super Mario Odyssey", "type": "game", "description": "Platformer game by Nintendo"},
    {"name": "Dark Souls III", "type": "game", "description": "Action RPG by FromSoftware"},
    {"name": "Hollow Knight", "type": "game", "description": "Metroidvania game by Team Cherry"},
    {"name": "Cyberpunk 2077", "type": "game", "description": "Sci-Fi RPG by CD Projekt Red"},
    {"name": "Baldur's Gate 3", "type": "game", "description": "Turn-based RPG by Larian Studios"},
    {"name": "Persona 5 Royal", "type": "game", "description": "JRPG by Atlus"},

    # Pokémon (50)
    {"name": "Charizard", "type": "pokemon", "description": "#0006 Fire/Flying Pokémon"},
    {"name": "Mewtwo", "type": "pokemon", "description": "#0150 Psychic Pokémon"},
    {"name": "Gengar", "type": "pokemon", "description": "#0094 Ghost/Poison Pokémon"},
    {"name": "Pikachu", "type": "pokemon", "description": "#0025 Electric Pokémon"},
    {"name": "Rayquaza", "type": "pokemon", "description": "#0384 Dragon/Flying Pokémon"},
    {"name": "Lucario", "type": "pokemon", "description": "#0448 Fighting/Steel Pokémon"},
    {"name": "Greninja", "type": "pokemon", "description": "#0658 Water/Dark Pokémon"},
    {"name": "Umbreon", "type": "pokemon", "description": "#0197 Dark Pokémon"},
    {"name": "Dragonite", "type": "pokemon", "description": "#0149 Dragon/Flying Pokémon"},
    {"name": "Garchomp", "type": "pokemon", "description": "#0445 Dragon/Ground Pokémon"},
    {"name": "Gardevoir", "type": "pokemon", "description": "#0282 Psychic/Fairy Pokémon"},
    {"name": "Gyaraos", "type": "pokemon", "description": "#0130 Water/Flying Pokémon"},
    {"name": "Blastoise", "type": "pokemon", "description": "#0009 Water Pokémon"},
    {"name": "Venusaur", "type": "pokemon", "description": "#0003 Grass/Poison Pokémon"},
    {"name": "Tyranitar", "type": "pokemon", "description": "#0248 Rock/Dark Pokémon"},

    # Technology / AI Tools (50)
    {"name": "Python", "type": "technology", "description": "Popular programming language"},
    {"name": "TypeScript", "type": "technology", "description": "Typed superset of JavaScript"},
    {"name": "Claude", "type": "technology", "description": "AI assistant by Anthropic"},
    {"name": "ChatGPT", "type": "technology", "description": "AI assistant by OpenAI"},
    {"name": "Cursor", "type": "technology", "description": "AI-first code editor"},
    {"name": "PostgreSQL", "type": "technology", "description": "Open source relational database"},
    {"name": "FastAPI", "type": "technology", "description": "Modern Python web framework"},
    {"name": "Next.js", "type": "technology", "description": "React framework for web development"},
    {"name": "Tailwind CSS", "type": "technology", "description": "Utility-first CSS framework"},
    {"name": "Docker", "type": "technology", "description": "Containerization platform"},
    {"name": "Redis", "type": "technology", "description": "In-memory data structure store"},
    {"name": "Rust", "type": "technology", "description": "Systems programming language focused on safety"},
    {"name": "Go", "type": "technology", "description": "Open source programming language by Google"},
    {"name": "React", "type": "technology", "description": "JavaScript library for building user interfaces"},
    {"name": "Linux", "type": "technology", "description": "Open source operating system kernel"}
]

def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        count = 0
        for item in STARTER_ENTITIES:
            existing = db.query(Entity).filter(Entity.name == item["name"], Entity.type == item["type"]).first()
            if not existing:
                e = Entity(
                    name=item["name"],
                    type=item["type"],
                    description=item.get("description"),
                    is_verified=True
                )
                db.add(e)
                count += 1
        db.commit()
        print(f"Successfully seeded {count} entities into database.")
    finally:
        db.close()

if __name__ == "__main__":
    seed()
