"""Exceptions."""
class ArchitectureIntelligenceError(Exception): pass
class CycleNotFoundError(ArchitectureIntelligenceError): pass
class InvalidCycleTypeError(ArchitectureIntelligenceError): pass
class StageExecutionError(ArchitectureIntelligenceError):
    def __init__(self, msg, stage=None, cause=None):
        super().__init__(msg)
        self.stage = stage
        self.cause = cause
