from enum import Enum
import datetime
from ibapi.order import Order as IBOrder
from ibapi.wrapper import *
from ibapi.const import UNSET_DOUBLE


class OrderType(Enum):
    ERROR = 'ERR'
    MARKET = 'MKT'
    LIMIT = 'LMT'
    STOP = 'STP'
    STOP_LIMIT = 'STP LMT'
    
    def __str__(self):
      return self.value
    
    
class OrderAction(Enum):
    BUY = 'B'
    SELL = 'S'
    
    def __str__(self):
      return self.value
    
    
class OrderStatus(Enum):
    PENDING_SUBMIT = 'PendingSubmit'
    PENDING_CANCEL = 'PendingCancel'
    PRE_SUBMITTED = 'PreSubmitted'
    SUBMITTED = 'Submitted'
    API_CANCELLED = 'ApiCancelled'
    CANCELLED = 'Cancelled'
    FILLED = 'Filled'
    INACTIVE = 'Inactive'
    PARTIAL = 'Part' # Partially filled, not an official Order status
    
    def __str__(self):
      return self.value
    

class Order:
    
    def __init__(self, symbol:str | None, action:OrderAction, quantity:int, limit:float=None, stop:float=None):
        if symbol is None:
            # return an empty order for user to fill in.
            return
        self.date_time = datetime.datetime.now()
        self.id = 0
        self.symbol = symbol
        self.action = action
        self.quantity = quantity
        self.limit = round(limit,2) if limit is not None else limit
        self.stop = round(stop,2) if stop is not None else stop
        self.order_type = OrderType.ERROR
        if self.action == OrderAction.BUY:
            if self.stop is None:
                self.order_type = OrderType.MARKET if self.limit is None else OrderType.LIMIT
            else:
                self.order_type = OrderType.STOP if self.limit is None else OrderType.STOP_LIMIT
        elif self.action == OrderAction.SELL:
            if self.stop is None:
                self.order_type = OrderType.MARKET if self.limit is None else OrderType.LIMIT
            else:
                self.order_type = OrderType.STOP if self.limit is None else OrderType.STOP_LIMIT

        self.date_time_last_update = self.date_time
        self.value = 0.0
        self.avg_price = 0.0
        self.fee = 0.0
        self.filled = 0
        self.unfilled = quantity
        self.status = OrderStatus.PENDING_SUBMIT
        
        self.ib_order = IBOrder()
        self.ib_order.action = 'BUY' if self.action == OrderAction.BUY else 'SELL'
        self.ib_order.totalQuantity = self.quantity
        self.ib_order.orderType = self.order_type.value
        self.ib_order.lmtPrice = self.limit if self.limit is not None else UNSET_DOUBLE
        self.ib_order.auxPrice = self.stop if self.stop is not None else UNSET_DOUBLE
        self.ib_order.outsideRth = True
        
        self.contract = Contract()
        self.contract.symbol = symbol
        self.contract.exchange = "smart"
        self.contract.currency = "USD"
        self.contract.secType = "STK"
    
    def __str__(self):
        return "Order#%-3d %-4s %s %-6s | %-12s | LMT: %3.2f STP: %3.2f FILLED: %4d/%4d | AVG_PRC: %5.2f | FEE: %5.2f" % (
            self.id, 
            self.symbol, 
            self.action, 
            self.order_type,
            self.status,
            self.limit if self.limit is not None else 0.0, 
            self.stop if self.stop is not None else 0.0, 
            self.filled, 
            self.quantity, 
            self.avg_price,
            self.fee)
        
    def to_csv(self):
        return "%s,%s,%d,%s,%s,%s,%s,%.2f,%.2f,%d,%d,%.2f,%.2f" % (
            self.date_time.strftime("%Y-%m-%d %H:%M:%S"),
            self.date_time_last_update.strftime("%Y-%m-%d %H:%M:%S"),
            self.id, 
            self.symbol, 
            self.action, 
            self.order_type,
            self.status,
            self.limit if self.limit is not None else 0.0, 
            self.stop if self.stop is not None else 0.0,
            self.quantity,
            self.filled,
            self.avg_price,
            self.fee)
        
    def finalise(self):
        self.date_time_last_update = datetime.datetime.now()
        self.value = self.avg_price * self.filled
        self.fee = 0.005 * self.filled
        self.unfilled = self.quantity - self.filled
        if self.unfilled == 0:
            self.status = OrderStatus.FILLED
        elif self.filled != 0:
            self.status = OrderStatus.PARTIAL
        return self