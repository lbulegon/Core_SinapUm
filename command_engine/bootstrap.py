"""Registo de handlers built-in (`AppSinapcoreConfig.ready`)."""

from __future__ import annotations

from command_engine.handlers.environmental.normalize import NormalizeHandler
from command_engine.handlers.environmental.pause_orders import PauseOrdersHandler
from command_engine.handlers.environmental.reduce_load import ReduceLoadHandler
from command_engine.handlers.menu.analisar_cardapio import AnalisarCardapioHandler
from command_engine.registry import CommandRegistry


def register_handlers() -> None:
    CommandRegistry.register(PauseOrdersHandler)
    CommandRegistry.register(ReduceLoadHandler)
    CommandRegistry.register(NormalizeHandler)
    CommandRegistry.register(AnalisarCardapioHandler)
