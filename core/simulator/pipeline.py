"""
Pipeline linear: prep → grill → assembly → dispatch.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from core.simulator.scheduler import ordenar_fila
from core.simulator.stations.assembly import AssemblyStation
from core.simulator.stations.dispatch import DispatchStation
from core.simulator.stations.grill import GrillStation
from core.simulator.stations.prep import PrepStation


class KitchenPipeline:
    def __init__(
        self,
        *,
        prep_cap: int = 2,
        grill_cap: int = 1,
        assembly_cap: int = 2,
        dispatch_cap: int = 1,
        prep_dur: int = 3,
        grill_dur: int = 5,
        assembly_dur: int = 4,
        dispatch_dur: int = 2,
    ) -> None:
        self.prep = PrepStation(prep_cap, prep_dur)
        self.grill = GrillStation(grill_cap, grill_dur)
        self.assembly = AssemblyStation(assembly_cap, assembly_dur)
        self.dispatch = DispatchStation(dispatch_cap, dispatch_dur)

    def admitir(
        self,
        pedido: Dict[str, Any],
        *,
        aplicar_chef_agno: bool = True,
        estado_operacional: Optional[Dict[str, Any]] = None,
        tempo_entrada: int = 0,
    ) -> None:
        if aplicar_chef_agno:
            from core.simulator.chef_agno_bridge import aplicar_prioridade_chef_agno

            aplicar_prioridade_chef_agno(
                pedido,
                estado_operacional=estado_operacional,
                tempo_espera=float(tempo_entrada),
            )
        self.prep.adicionar(pedido)
        ordenar_fila(self.prep)

    def step(self, tempo: int) -> List[Dict[str, Any]]:
        ordenar_fila(self.prep)
        final_prep = self.prep.processar(tempo)
        for p in final_prep:
            self.grill.adicionar(p)

        ordenar_fila(self.grill)
        final_grill = self.grill.processar(tempo)
        for p in final_grill:
            self.assembly.adicionar(p)

        ordenar_fila(self.assembly)
        final_assembly = self.assembly.processar(tempo)
        for p in final_assembly:
            self.dispatch.adicionar(p)

        ordenar_fila(self.dispatch)
        return self.dispatch.processar(tempo)

    def tick_inerte(self) -> bool:
        for st in (self.prep, self.grill, self.assembly, self.dispatch):
            if st.fila or st.em_producao:
                return False
        return True

    def executar(
        self,
        max_ticks: int = 500,
        *,
        ate_pedidos_completos: Optional[int] = None,
        pedidos_completados: Optional[List[Dict[str, Any]]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Avança o relógio até esvaziar a linha ou atingir max_ticks.
        Acumula pedidos que saíram de dispatch (expedição concluída).
        """
        saida: List[Dict[str, Any]] = [] if pedidos_completados is None else pedidos_completados
        for t in range(max_ticks):
            done = self.step(t)
            for p in done:
                saida.append(p)
            if self.tick_inerte():
                break
            if ate_pedidos_completos is not None and len(saida) >= ate_pedidos_completos:
                break
        return saida
