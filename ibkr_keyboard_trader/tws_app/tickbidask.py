from ibapi.client import EClient
from ibapi.wrapper import *

from .twscommon import TWSCommon


class TWSTickBidAsk():

    def __init__(self, tws_common: TWSCommon):
        self.tws_common = tws_common

    def request_tick_bid_ask(self, symbol: str):
        contract = Contract()
        contract.symbol = symbol
        contract.secType = "STK"
        contract.exchange = "smart"
        contract.currency = "USD"
        self.request_tick_bid_ask_by_contract(contract)

    def request_tick_bid_ask_by_contract(self, contract: Contract):
        symbol = contract.symbol
        if symbol in self.tws_common.tick_req_id_symbol_map.values():
            return
        if len(self.tws_common.tick_req_id_symbol_map) >= 3:
            # can track only 3 symbols at a time
            self.free_up_track_symbol()
        EClient.reqTickByTickData(self, self.tws_common.tick_req_id, contract, "BidAsk", 1, False)
        self.tws_common.tick_req_id_symbol_map[self.tws_common.tick_req_id] = symbol
        self.tws_common.tick_req_id += 1

    def cancel_tick_bid_ask(self, reqId):
        EClient.cancelTickByTickData(self, reqId)
        try:
            self.tws_common.tick_req_id_symbol_map.pop(reqId)
        except KeyError:
            pass

    def free_up_track_symbol(self):
        for reqId, symbol in self.tws_common.tick_req_id_symbol_map.items():
            if symbol != self.tws_common.current_symbol:
                self.cancel_tick_bid_ask(reqId)
                self.tws_common.logger.warn(f"Max number of symbol tracking reached. Untracking symbol: {symbol}...")
                return
