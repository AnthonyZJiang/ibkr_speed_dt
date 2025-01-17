from decimal import Decimal

from ibapi.client import *
from ibapi.common import TickAttribBidAsk
from ibapi.contract import ContractDetails
from ibapi.wrapper import *
from ibapi.account_summary_tags import AccountSummaryTags

from .twscommon import TWSCommon
from .contractdetails import TWSContractDetails
from .displaygroup import TWSDisplayGroup
from .tickbidask import TWSTickBidAsk
from .trade import TWSTrade
from .account import TWSAccount


class TWSApp(EWrapper, EClient, TWSContractDetails, TWSDisplayGroup, TWSTrade, TWSTickBidAsk, TWSAccount):
    
    def __init__(self, platform_type: str):
        EClient.__init__(self, self)
        
        self.tws_common = TWSCommon(platform_type)
        
        self.req_id_callback_map: dict[int, callable] = {}
        TWSContractDetails.__init__(self, self.tws_common)
        TWSDisplayGroup.__init__(self, self.tws_common)
        TWSTickBidAsk.__init__(self, self.tws_common)
        TWSTrade.__init__(self, self.tws_common)
        TWSAccount.__init__(self, self.tws_common)
        
    def tickByTickBidAsk(self, reqId: int, time_: int, bidPrice: float, askPrice: float, bidSize: Decimal, askSize: Decimal, tickAttribBidAsk: TickAttribBidAsk):
        return TWSTrade.process_bid_ask_tick(self, reqId, time_, bidPrice, askPrice, bidSize, askSize, tickAttribBidAsk)
    
    def contractDetails(self, reqId: int, contractDetails: ContractDetails):
        return TWSContractDetails.contractDetails(self, reqId, contractDetails)
    
    def contractDetailsEnd(self, reqId: int):
        return TWSContractDetails.contractDetailsEnd(self, reqId)
        
    def displayGroupUpdated(self, reqId: int, contractInfo: str):
        TWSDisplayGroup.displayGroupUpdated(self, reqId, contractInfo)
    
    def nextValidId(self, orderId: int):
        self.tws_common.is_ready = True
        self.reqAccountUpdates(True, self.tws_common.ibkr_account)
        TWSTrade.nextValidId(self, orderId)
        self.reqAccountSummary(9001, "All", AccountSummaryTags.BuyingPower)
        
    def orderStatus(self, *args):
        TWSTrade.orderStatus(self, *args)
        
    def updatePortfolio(self, *args):
        TWSAccount.updatePortfolio(self, *args)
        
    def  accountSummary(self, *args):
        TWSAccount.accountSummary(self, *args)

    def error(self, reqId, errorCode, errorString, placeholder=None):
        if reqId == -1:
            self.tws_common.logger.debug(f"{errorString}")
        elif errorCode == 202:
            if len(errorString) > 24: # If reason is empty, i.e. errorString == 'Order Canceled - reason:', skip logging
                self.tws_common.logger.info(f"Order#{reqId}: {errorString}.")
        else:
            self.tws_common.logger.error(f"Error {errorCode}: {reqId}, {errorString}")
        