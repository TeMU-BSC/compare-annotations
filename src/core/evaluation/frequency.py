from unidecode import unidecode


class FreqCalculator:
    def __init__(self):
        self.acceptance_rate = dict()


    @staticmethod
    def normolized_text(text_original):
        normolized_whitespace = " ".join(text_original.split())
        unaccented_string = unidecode(normolized_whitespace)

        return unaccented_string.lower()


    def update_notacceptance_freq(self, text_original, lable_original):
        if lable_original.startswith("_SUG_"):
            label = lable_original.replace("_SUG_", "").replace("_previa", "").replace("_alta", "").replace("_hab", "")
            unaccented_string = self.normolized_text(text_original)
            if self.acceptance_rate.get(unaccented_string + "_" + label) is None:
                self.acceptance_rate[unaccented_string + "_" + label] = {"accepted": 0, "notaccepted": 1}
            else:
                temp_word = self.acceptance_rate.get(unaccented_string + "_" + label)
                temp_counter = temp_word.get("notaccepted")
                update = {"accepted": temp_word.get("accepted"), "notaccepted": temp_counter + 1}
                self.acceptance_rate.update({unaccented_string + "_" + label: update})

    def update_acceptance_freq(self, text_original, lable_original):
        if not (lable_original.startswith("SECCION_") or lable_original.startswith("Hora_")
                or lable_original.startswith("Fecha_") or lable_original.startswith("Tiempo_")):

            label = lable_original.replace("_previa", "").replace("_alta", "").replace("_hab", "")
            unaccented_string = self.normolized_text(text_original)
            if self.acceptance_rate.get(unaccented_string + "_" + label) is None:
                self.acceptance_rate[unaccented_string + "_" + label] = {"accepted": 1, "notaccepted": 0}
            else:
                temp_word = self.acceptance_rate.get(unaccented_string + "_" + label)
                temp_counter = temp_word.get("accepted")
                update = {"accepted": temp_counter + 1, "notaccepted": temp_word.get("notaccepted")}
                self.acceptance_rate.update({unaccented_string + "_" + label: update})





