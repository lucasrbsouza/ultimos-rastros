import json
import os

SAVE_PATH = 'save.json'

def save_game(health, memories, position):
    """Salva o estado atual do jogo em JSON."""
    data = {
        'health':   health,
        'memories': memories,
        'pos_x':    position[0],
        'pos_y':    position[1],
    }
    with open(SAVE_PATH, 'w') as f:
        json.dump(data, f)
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
