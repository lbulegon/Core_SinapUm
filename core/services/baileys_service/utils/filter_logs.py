"""
Filtro de Logs - Baileys Service
=================================

Filtra logs internos do Baileys para reduzir ruído.
Equivalente ao filterLogs.js do projeto Node.js.
"""
import logging
import sys

# Padrões de logs a serem ignorados
IGNORE_PATTERNS = [
    "Bad MAC Error",
    "Decrypted message with closed session",
    "Closing stale open session",
    "SessionEntry",
    "Connection closed",
    "Connection error",
]


class LogFilter(logging.Filter):
    """Filtro para logs do Baileys"""
    
    def filter(self, record):
        """Filtra logs que contêm padrões ignorados"""
        message = str(record.getMessage())
        return not any(pattern in message for pattern in IGNORE_PATTERNS)


def setup_log_filter():
    """Configura filtro de logs para o logger do Baileys"""
    logger = logging.getLogger('baileys')
    logger.addFilter(LogFilter())
    
    # Também filtra no handler root se necessário
    root_logger = logging.getLogger()
    for handler in root_logger.handlers:
        handler.addFilter(LogFilter())


def filter_console():
    """Filtra logs no console (equivalente ao filterLogs.js)"""
    original_log = print
    original_error = print
    
    def filtered_log(*args, **kwargs):
        message = ' '.join(str(arg) for arg in args)
        if not any(pattern in message for pattern in IGNORE_PATTERNS):
            original_log(*args, **kwargs)
    
    def filtered_error(*args, **kwargs):
        message = ' '.join(str(arg) for arg in args)
        if not any(pattern in message for pattern in IGNORE_PATTERNS):
            original_error(*args, **kwargs)
    
    # Substitui print e sys.stderr.write se necessário
    # Nota: Em Python, é melhor usar logging com filtros do que substituir print
    return filtered_log, filtered_error
