from ibapi.wrapper import *

from .twscommon import TWSCommon
from .datastore.accountentry import TWSAccountEntry


class TWSAccount():

    def __init__(self, tws_common: TWSCommon):
        self.tws_common = tws_common
        
    def updatePortfolio(self, contract: Contract, position: Decimal,marketPrice: float, marketValue: float, averageCost: float, unrealizedPNL: float, realizedPNL: float, accountName: str):
        if contract.symbol in self.tws_common.current_positions:
            self.tws_common.current_positions[contract.symbol].quantity = int(position)
        else:
            self.tws_common.current_positions[contract.symbol] = TWSAccountEntry(int(position))
            
    def accountSummary(self, reqId: int, account: str, tag: str, value: str,currency: str):
        if account == self.tws_common.ibkr_account:
            if tag == 'CashBalance':
                self.tws_common.current_positions['cash'] = float(value)
