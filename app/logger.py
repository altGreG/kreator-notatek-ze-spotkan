from loguru import logger as log

"""
Uwaga: Jeśli chcemy po prostu wypisać coś w kosoli bez aktualizacji statusu aplikacji GUI, to po prostu użyjmy print() lub
       metod z klasy logger z biblioteki loguru, klasy u nas przemianowanej na log. Przykładowo można użyć:
    
    log.debug(msg)
    log.trace(msg)
    log.info(msg)
    log.success(msg)
    log.warning(msg)
    log.error(msg)
    log.critical(msg)
"""

def log_status(msg, level,  update_status):
    """
    Funkcja wypisuje logi w konsoli i uaktualnia status aplikacji GUI

    :param msg: wiadomość do wyświetlenia
    :param level: poziom określający znaczenie wiadomości
    :param update_status: metoda aplikacji gui służąca do aktualizacji wiadomości statusu w GUI
    """

    # wartość typu str, oznacza,że tylko testujemy bez udziału GUI
    if type(update_status) != str:
        update_status(msg)
    match level:
        case "trace":
            log.opt(depth=1).trace(msg)
        case "debug":
            log.opt(depth=1).debug(msg)
        case "info":
            log.opt(depth=1).info(msg)
        case "success":
            log.opt(depth=1).success(msg)
        case "warning":
            log.opt(depth=1).warning(msg)
        case "error":
            log.opt(depth=1).error(msg)
        case "critical":
            log.opt(depth=1).critical(msg)
        case "_":
            log.critical("Nie ma takiego poziomu.")

