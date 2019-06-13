class LaudoSigep():
    def __init__(self, id_num, laudo_num, nic, descr=""):
        self.id_num = id_num
        self.laudo_num = laudo_num
        self.nic = nic
        self.descr = descr

    def set_register_date(self, d):
        self.reg_date = d

    def set_conclusion_date(self, d):
        self.con_date = d

    def __str__(self):
        return """Laudo number: {}\nLaudo ID: {}\nNIC: {}\n\nRegistered in: {}\nConcluded in: {}\n\nDescription: {}""".format(self.laudo_num, self.id_num, self.nic, self.reg_date, self.con_date, self.descr)
