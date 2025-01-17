from .order import Order, OrderAction, OrderStatus


class TWSAccountEntry():
    
    def __init__(self, quantity: int = 0):
        self.quantity = quantity
        self.open_sell_orders: dict[int, int] = {} # order_id: quantity
        
    @property
    def projected_quantity(self):
        qty_in_sell_orders = sum(self.open_sell_orders.values())
        return self.quantity - qty_in_sell_orders
    
    def update_sell_order(self, order: Order):
        if order.action != OrderAction.SELL:
            return
        if order.status == OrderStatus.SUBMITTED or order.status == OrderStatus.PRE_SUBMITTED:
            if order.id not in self.open_sell_orders:
                self._add_sell_order(order)
            else:
                # Partial fill
                self.open_sell_orders[order.id] = order.unfilled
            return
        if order.status == OrderStatus.FILLED or order.status == OrderStatus.CANCELLED or order.status == OrderStatus.INACTIVE:
            if order.id not in self.open_sell_orders:
                # Probably an active order that was not submitted in this session
                return
            del self.open_sell_orders[order.id]
        elif order.status == OrderStatus.PENDING_CANCEL or order.status == OrderStatus.PENDING_SUBMIT or order.status == OrderStatus.API_CANCELLED:
            return
        else:
            raise ValueError(f"Unexpected order status: {order.status}")
        
    def _add_sell_order(self, order: Order):
        if order.status == OrderStatus.FILLED or order.status == OrderStatus.CANCELLED or order.status == OrderStatus.INACTIVE:
            return
        self.open_sell_orders[order.id] = order.unfilled