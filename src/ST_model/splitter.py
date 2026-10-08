

from src.base.converter import AccountingConverter

class AccountingSplitter(AccountingConverter):

    def __init__(self, name, inlet, outlet1, outlet2, system):
        super().__init__(name, "splitter", system, note="显式分流；支路流量不平均分配")
        self.add_inlet(inlet)
        self.add_outlet(outlet1)
        self.add_outlet(outlet2)


