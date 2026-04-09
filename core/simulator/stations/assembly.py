from core.simulator.stations.base import Station


class AssemblyStation(Station):
    def __init__(self, capacidade: int = 2, duracao_padrao: int = 4):
        super().__init__("assembly", capacidade, duracao_padrao)
