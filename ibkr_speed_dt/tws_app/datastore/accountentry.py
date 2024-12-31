from .order import Order, OrderStatus, OrderAction

class TWSAccountEntry():
    
    def __init__(self, quantity: int = 0):
        self.quantity = quantity
        self.quantity_in_sell_orders = 0
        self.open_sell_orders: dict[int, int] = {} # order_id: quantity
        
    @property
    def projected_quantity(self):
        return self.quantity - self.quantity_in_sell_orders
    
    def update_sell_order(self, order: Order):
        if order.action != OrderAction.SELL:
            return
        if order.id not in self.open_sell_orders:
            self._add_sell_order(order)
            return
        self.quantity_in_sell_orders -= self.open_sell_orders[order.id]
        if order.status == OrderStatus.FILLED:
            del self.open_sell_orders[order.id]
        elif order.status == OrderStatus.CANCELLED:
            self.quantity_in_sell_orders -= order.unfilled
            del self.open_sell_orders[order.id]
        else:
            unfilled = order.unfilled
            self.open_sell_orders[order.id] = unfilled
            self.quantity_in_sell_orders += unfilled
        
    def _add_sell_order(self, order: Order):
        if order.status == OrderStatus.FILLED or order.status == OrderStatus.CANCELLED or order.status == OrderStatus.INACTIVE:
            return
        self.open_sell_orders[order.id] = order.unfilled
        self.quantity_in_sell_orders += order.unfilled