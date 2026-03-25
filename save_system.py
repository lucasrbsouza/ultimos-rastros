import json
import os

SAVE_PATH = 'save.json'

def save_game(player, collected_positions):
    """
    Salva o estado do jogador e a lista de posições das memórias já coletadas.

    collected_positions: set de tuplas (x, y) — posição rect.topleft de cada
    Memory coletada. Usamos topleft porque é o que setup_level() usa ao criar
    os sprites (col * TILE_SIZE, row * TILE_SIZE).
    """
    data = {
        'health':   player.current_health,
        'memories': player.memories,
        'collected_positions': [list(pos) for pos in collected_positions],
    }
    with open(SAVE_PATH, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"Jogo salvo: {data}")

def load_game():
    """Carrega o save. Retorna None se não existir."""
    if not os.path.exists(SAVE_PATH):
        return None
    try:
        with open(SAVE_PATH, 'r') as f:
            data = json.load(f)
        print(f"Save carregado: {data}")
        return data
    except (json.JSONDecodeError, KeyError):
        print("Save corrompido — ignorando.")
        return None

def delete_save():
    """Apaga o save — útil ao iniciar nova partida."""
    if os.path.exists(SAVE_PATH):
        os.remove(SAVE_PATH)
        print("Save apagado.")

def has_save():
    """Retorna True se existe um save válido."""
    return load_game() is not None
