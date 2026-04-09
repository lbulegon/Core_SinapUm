from core.simulator.stations.base import Station


class PrepStation(Station):
    def __init__(self, capacidade: int = 2, duracao_padrao: int = 3):
        super().__init__("prep", capacidade, duracao_padrao)
