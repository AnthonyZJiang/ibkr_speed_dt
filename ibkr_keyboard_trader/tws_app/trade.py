from queue import Queue
from decimal import Decimal
from threading import Thread
import time
import copy

from ibapi.wrapper import *
from ibapi.client import EClient
from ibapi.order_cancel import OrderCancel
from ibapi.order import Order as IBOrder

from .datastore.order import Order, OrderStatus, OrderAction
from .twscommon import TWSCommon
from .tickbidask import TWSTickBidAsk


class TWSTrade():
    
    def __init__(self, tws_common: TWSCommon):
        self.tws_common = tws_common
        
        self.new_orders: Queue[Order] = Queue()
        self.allow_short = False
        self.housekeeping_thread = Thread(target=self.housekeeping_thread_run)
        self.housekeeping_thread.start()
        self.is_next_id_ready = False
        self.next_id = 0
        
    def nextValidId(self, orderId: int):
        self.next_id = orderId
        self.is_next_id_ready = True
    
    def orderStatus(self, orderId: int, status: str, filled: Decimal, remaining: Decimal, avgFillPrice: float, permId: int, parentId: int, lastFillPrice: float, clientId: int, whyHeld: str, mktCapPrice: float):
        if orderId not in self.tws_common.open_orders:
            return
        order = self.tws_common.open_orders[orderId]
        status = OrderStatus(status)
        changed = order.status != status or order.filled != filled
        if not changed:
            return
        order.status = status
        order.filled = int(filled)
        order.unfilled = int(remaining)
        order.avg_price = avgFillPrice
        self.log_order(order)
        if order.symbol in self.tws_common.current_positions and order.action == OrderAction.SELL:
            self.tws_common.current_positions[order.symbol].update_sell_order(order)
        if status == OrderStatus.FILLED or status == OrderStatus.CANCELLED:
            order.finalise()
            del self.tws_common.open_orders[order.id]
            self.tws_common.completed_orders[order.id] = order
        elif status == OrderStatus.INACTIVE:
            del self.tws_common.open_orders[order.id]
        
    def request_complete_orders(self):
        EClient.reqCompletedOrders(self, True)
        
    def place_order(self, order: Order):
        if not self.check_shorting(order):
            return
        id = self.get_next_id()
        order.ib_order.account = self.tws_common.ibkr_account
        EClient.placeOrder(self, orderId = id, contract=order.contract, order=order.ib_order)
        self.tws_common.open_orders[id] = order
        order.id = id
        self.is_next_id_ready = False
        EClient.reqIds(self, -1)
        
    def check_shorting(self, order: Order):
        if self.tws_common.allow_short:
            return True
        if order.action == OrderAction.BUY:
            return True
        projected_quantity = self.tws_common.current_positions[order.symbol].projected_quantity if order.symbol in self.tws_common.current_positions else 0
        if projected_quantity == 0:
            self.tws_common.logger.info(f"Short selling not allowed. Order not submitted.")
            return False
        if projected_quantity < order.quantity:
            order.quantity = projected_quantity
            self.tws_common.logger.info(f"Short selling not allowed. Adjusting quantity to {order.quantity}.")
        return True
        
    def get_next_id(self):
        if self.is_next_id_ready:
            return self.next_id
        self.next_id += 1
        return self.next_id
        
    def cancel_order(self, order_id: int):
        EClient.cancelOrder(self, order_id, OrderCancel())

    def cancel_all_orders(self):
        EClient.reqGlobalCancel(self)

    def cancel_last_order(self):
        if len(self.tws_common.open_orders) > 0:
            order_id = list(self.tws_common.open_orders.keys())[-1]
            self.cancel_order(order_id)
            
    def process_bid_ask_tick(self, reqId: int, time_: int, bidPrice: float, askPrice: float, bidSize: Decimal, askSize: Decimal, attrib: TickAttribBidAsk):
        if reqId not in self.tws_common.tick_req_id_symbol_map:
            TWSTickBidAsk.cancel_tick_bid_ask(self, reqId)
            return
        sym = self.tws_common.tick_req_id_symbol_map[reqId]
        if sym == self.tws_common.current_symbol:
            self.tws_common.current_ask = askPrice
            self.tws_common.current_bid = bidPrice
                
    def log_order(self, order: Order):
        if order.status == OrderStatus.FILLED:
            self.tws_common.logger.info(f"Order filled    : {order}")
            self.tws_common.trade_logger.info(order.to_csv())
        elif order.status == OrderStatus.CANCELLED:
            self.tws_common.logger.info(f"Order cancelled : {order}")
            self.tws_common.trade_logger.info(order.to_csv())
        else:
            self.tws_common.logger.info(f"Order updated   : {order}")
            
    def clear_unused_tick_req(self):
        sym_map = copy.deepcopy(self.tws_common.tick_req_id_symbol_map)
        for req_id, sym in sym_map.items():
            if sym != self.tws_common.current_symbol:
                    TWSTickBidAsk.cancel_tick_bid_ask(self, req_id)

    def housekeeping_thread_run(self):
        while not self.tws_common.exit_flag:
            if not self.tws_common.is_ready:
                continue
            self.clear_unused_tick_req()
            time.sleep(0.5)
