from ibapi.client import *
from ibapi.wrapper import *

from .twscommon import TWSCommon
from .tickbidask import TWSTickBidAsk


class TWSDisplayGroup():

    def __init__(self, tws_common: TWSCommon):
        self.tws_common = tws_common
        self.display_group_req_id = 29000
        self.subscribed_group_id = -1

    def link_display_group(self, group_id: int):
        if group_id == self.subscribed_group_id:
            return
        if self.subscribed_group_id > 0:
            EClient.unsubscribeFromGroupEvents(self, self.display_group_req_id)
        if group_id > 0:
            self.display_group_req_id += 1
            EClient.subscribeToGroupEvents(self, self.display_group_req_id, group_id)
        self.subscribed_group_id = group_id

    def update_linked_group_by_symbol(self, symbol: str):
        contract = Contract()
        contract.symbol = symbol
        contract.exchange = "smart"
        contract.currency = "USD"
        contract.secType = "STK"
        if self.subscribed_group_id <= 0:
            self.tws_common.req_id_callback_map[self.tws_common.contract_detail_req_id] = self.contract_details_end_callback
        else:
            self.tws_common.req_id_callback_map[self.tws_common.contract_detail_req_id] = self.update_linked_group_by_contract
        EClient.reqContractDetails(self, self.tws_common.contract_detail_req_id, contract)
        self.tws_common.contract_detail_req_id += 1

    def update_linked_group_by_contract(self, contract: Contract):
        if self.subscribed_group_id <= 0:
            return
        contract_info = f"{contract.conId}@{contract.exchange}"
        EClient.updateDisplayGroup(self, self.display_group_req_id, contract_info)

    def displayGroupUpdated(self, reqId: int, contractInfo: str):
        if contractInfo == "none":
            self.tws_common.logger.warn(f"Display group updated but unable to get contract info")
            return
        id, exchange = contractInfo.split("@")
        contract = Contract()
        contract.conId = int(id)
        contract.exchange = exchange
        contract.currency = "USD"
        contract.secType = "STK"
        self.tws_common.req_id_callback_map[self.tws_common.contract_detail_req_id] = self.contract_details_end_callback
        EClient.reqContractDetails(self, self.tws_common.contract_detail_req_id, contract)
        self.tws_common.contract_detail_req_id += 1

    def contract_details_end_callback(self, contract: Contract):
        if self.tws_common.current_symbol == contract.symbol:
            return
        TWSTickBidAsk.request_tick_bid_ask_by_contract(self, contract)
        self.tws_common.current_symbol = contract.symbol
        self.tws_common.current_contract = contract
        self.tws_common.gui_update_callback_tracked_symbol(contract.symbol)
