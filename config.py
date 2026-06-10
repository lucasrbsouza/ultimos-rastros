"""Estado de configuração ajustável em tempo de execução (modo GOD)."""


class _GameConfig:
    def __init__(self):
        self.god_mode = False


CONFIG = _GameConfig()


def apply_god_powers(player):
    """Concede ao jogador todos os poderes da loja (usado pelo modo GOD)."""
    player.can_shoot = True
    player.sussurro_comprado = True
    player.active_powers = ['voz_floresta', 'sombra_mata']
    player.active_power_index = 0
    if not player.guardiao_vida_bought:
        player.guardiao_vida_bought = True
        player.max_health += 2
    player.current_health = player.max_health
    player.chama_ancestral_charges = max(player.chama_ancestral_charges, 99)
    player.update_stage()
