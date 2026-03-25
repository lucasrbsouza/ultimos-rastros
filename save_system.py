import json
import os

SAVE_PATH = 'save.json'

def save_game(player, collected_positions, world_offset=0):
    """
    Salva o estado do jogador e a lista de posições das memórias já coletadas.

    collected_positions: set de tuplas (x, y) — posição ORIGINAL do mapa
    (map_pos), que não muda com a câmera.

    world_offset: deslocamento acumulado do mundo (para recalcular a posição
    real do jogador no mapa).
    """
    # Posição real do jogador no mapa = posição na tela - deslocamento acumulado
    player_map_x = player.rect.x - world_offset
    player_map_y = player.rect.y

    data = {
        'health':   player.current_health,
        'memories': player.memories,
        'collected_positions': [list(pos) for pos in collected_positions],
        'player_x': player_map_x,
        'player_y': player_map_y,
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