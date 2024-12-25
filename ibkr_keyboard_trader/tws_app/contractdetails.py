from ibapi.wrapper import *

from .twscommon import TWSCommon


class TWSContractDetails():

    def __init__(self, tws_common: TWSCommon):
        self.tws_common = tws_common
        self.contract_detail_req_id = 19000
        self._contract_detail_list: dict[int, list[ContractDetails]] = {}
        self.contract_details: dict[int, Contract] = {}
        self.contract_details_by_id: dict[int, Contract] = {}
        self.contract_detail_req_id_to_track = 0

    def contractDetails(self, reqId, contractDetails):
        if reqId not in self._contract_detail_list:
            self._contract_detail_list[reqId] = []
        self._contract_detail_list[reqId].append(contractDetails)

    def contractDetailsEnd(self, reqId: int):
        if reqId in self._contract_detail_list:
            contract = self._contract_detail_list[reqId][0].contract
            self.contract_details[reqId] = contract
            self.contract_details_by_id[contract.conId] = contract
        if reqId in self.tws_common.req_id_callback_map:
            self.tws_common.req_id_callback_map[reqId](contract)
