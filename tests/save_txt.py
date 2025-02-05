from app.utilities.saving import save_text_to_txt
from loguru import logger as log

log.info("Test funkcji służącej do zapisu text w pliku txt o nazwie podanej w argumencie filename funkcji.")

text =  "o zjawisku fotoelektrycznym, które jest zjawiskiem, które się nie da wyjaśnić wprost za pomocą teorii falowej.\n"\
        "Z kilku względów, o których była mowa wcześniej, natomiast zostało to wyjaśnione przy \n"\
        "pomocy pojęcia fotonów, czyli przy pomocy pojęcia cząsteczek, porcji energii, które poruszają się,\n"\
        "mają pewną prędkość, mają pewną energię i wobec tego, zderzając się z elektronami, potrafią je poruszyć, to \n"\
        "znaczy poruszyć."

update_status = "placeholder"
path_to_txt = save_text_to_txt("test_txt",text,update_status)

if path_to_txt == None:
    log.info("Nie udało się zapisać tekstu w pliku txt.")
else:
    log.info("Sukces.")