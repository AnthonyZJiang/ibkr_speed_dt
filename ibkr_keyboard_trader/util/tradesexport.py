from pathlib import Path
from ibkr_keyboard_trader.tws_app.datastore.order import Order, OrderStatus, OrderAction
from .twslogging import setup_logger


def export_trades_tradesviz(destination: str, orders: dict[int, Order]):
    logger = setup_logger()
    header = "Date,STK,Time,Action,OrderType,Price,Quantity,Value,Position,Profit,Fee\n"
    if Path(destination).exists():
        with open(destination, "r") as f:
            first_line = f.readline()
        write_header = first_line == header
    else:
        write_header = True
    n = 0
    with open(destination, "a") as f:
        if write_header:
            f.write(header)
        for order in orders.values():
            if order.status == OrderStatus.CANCELLED and order.filled == 0:
                continue
            f.write("%s,%s,%s,stock,%.3f,USD,%d,%.3f,%s,\n" % (
                    order.date_time_last_update.strftime('%Y%m%d'),
                    order.date_time_last_update.strftime('%H:%M:%S'),
                    order.symbol,
                    order.avg_price,
                    order.filled if order.action == OrderAction.BUY else -order.filled,
                    order.fee,
                    ''))
            n += 1
            
    logger.info(f"Exported {n} orders to {destination}.")
    

def export_trades_tradervue(destination: str, orders: dict[int, Order]):
    logger = setup_logger()
    header = "Date,Time,Symbol,Quantity,Price,Side\n"
    if Path(destination).exists():
        with open(destination, "r") as f:
            first_line = f.readline()
        write_header = first_line == header
    else:
        write_header = True
    n = 0
    with open(destination, "a") as f:
        if write_header:
            f.write(header)
        for order in orders.values():
            if order.status == OrderStatus.CANCELLED and order.filled == 0:
                continue
            f.write("%s,%s,%s,%d,%.4f,%s\n" % (
                    order.date_time_last_update.strftime('%d/%m/%Y'),
                    order.date_time_last_update.strftime('%H:%M:%S'),
                    order.symbol,
                    order.filled,
                    order.avg_price,
                    'Buy' if order.action == OrderAction.BUY else 'Sell'
                    ))
            n += 1
            
    logger.info(f"Exported {n} orders to {destination}.")
    

export_funcs = {
    'tradesviz': export_trades_tradesviz,
    'tradervue': export_trades_tradervue
}