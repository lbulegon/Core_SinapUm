from core.simulator.stations.base import Station


class DispatchStation(Station):
    def __init__(self, capacidade: int = 1, duracao_padrao: int = 2):
        super().__init__("dispatch", capacidade, duracao_padrao)
