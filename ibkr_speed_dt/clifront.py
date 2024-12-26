from rich.console import Console
from rich.prompt import Confirm, Prompt
from threading import Thread
import logging
import time

from .tws_app import TWSApp
from .util.twslogging import setup_logger
from .tws_app.datastore.order import Order, OrderAction
from .util.fundamentals import StockFundamentals
from .util.tradesexport import export_funcs


DEFAULT_ORDER_SIZE = 100

class CLIFront:
    
    def __init__(self, platform_type: str):
        self.logger = setup_logger('sim_cli', logging.INFO, logging.DEBUG, 'sim.log')
        self.logger.info("Simulator initialising...")
        self.tws_app = None
        self.app_thread = None
        self.order = None
        self.default_quantity = DEFAULT_ORDER_SIZE
        self.console = Console()
        self.platform_type = platform_type
        
    def run(self):
        self.tws_app = TWSApp(self.platform_type)
        self.tws_app.tws_common.gui_update_callback_tracked_symbol = self._gui_update_callback_tracked_symbol
        self.tws_app.connect("127.0.0.1", self.tws_app.tws_common.ibkr_port, clientId=0)
        self.app_thread = Thread(target=self.tws_app.run)
        self.app_thread.start()
        self.logger.info("Waiting for TWSApp...")
        while not self.tws_app.tws_common.is_ready:
            time.sleep(0.1)
        self.logger.info("TWSApp ready.")
        self.tws_app.link_display_group(self.tws_app.tws_common.config['default_display_group'])
        exit_flag = False
        self.print_tracking_symbol = False
        while not exit_flag:
            try:
                exit_flag = not self._take_command()
            except ValueError as e:
                print("Invalid argument")
                self.logger.error(e)
            except Exception as e:
                print("An unknown error occurred, check log for details.")
                self.logger.error(e, exc_info=True)
        self.tws_app.tws_common.exit_flag = True
        self.tws_app.disconnect()
        self.app_thread.join()
        
    def _gui_update_callback_tracked_symbol(self, symbol):
        print(f"Platform: {self.platform_type.upper()} | Tracking: {symbol}")

    def _place_order(self, order: Order):
        if order.symbol is None:
            return
        if not self._confirm_order_instant_exe(order):
            return
        self.tws_app.place_order(order)

    def _confirm_order_instant_exe(self, order: Order):
        # if order.action == OrderAction.BUY:
        #     if order.limit is not None and order.limit > self.tws_app.tws_common.current_ask:
        #         self.console.print("[yellow]Instant execution because limit price is higher than the ask price! Proceed? [y/n]")
        #         if input().lower() != "y":
        #             return False
        #     if order.stop is not None and order.stop < self.tws_app.tws_common.current_ask:
        #         self.console.print("[yellow]Instant execution because stop price is lower than the ask price! Proceed? [y/n]")
        #         if input().lower() != "y":
        #             return False
        # elif order.action == OrderAction.SELL:
        #     if order.limit is not None and order.limit < self.tws_app.tws_common.current_bid:
        #         self.console.print("[yellow]Instant execution because limit price is lower than the bid price! Proceed? [y/n]")
        #         if input().lower() != "y":
        #             return False
        #     if order.stop is not None and order.stop > self.tws_app.tws_common.current_bid:
        #         self.console.print("[yellow]Instant execution because stop price is lower than the bid price! Proceed? [y/n]")
        #         if input().lower() != "y":
        #             return False
        return True

    def _take_command(self):
        if self.print_tracking_symbol:
            print(f"Platform: {self.platform_type.upper()} | Tracking: {self.tws_app.tws_common.current_symbol}")
        self.print_tracking_symbol = True
        val = input("")
        if val == "exit":
            ans = Confirm.ask("Do you want to export the trades?")
            if ans:
                ans = Prompt.ask("Enter the file name", default="trades.csv")
                self.export_trades(ans)
            self.logger.info("Exiting")
            self.tws_app.disconnect()
            return False
        return self._process_command(val.lower().split())
    
    def _process_command(self, args: dict[str]):
        nargs = len(args)

        match args[0]:
            case "help":
                self._print_help()
            case "set":
                self._set_parameters(*args[1:])
            case "track":
                self._set_track(*args[1:])
            case "t":
                self._set_track(*args[1:])
            case "link":
                if nargs == 1:
                    print("No value provided")
                    return True
                self.print_tracking_symbol = False
                id = int(args[1])
                self.tws_app.link_display_group(id)
            case "x":
                order = self._get_order(OrderAction.BUY, *args[1:])
                self._place_order(order)
            case "s":
                order = self._get_order(OrderAction.SELL, *args[1:])
                self._place_order(order)
            case "cl":
                pos = self.tws_app.tws_common.current_positions.get(self.tws_app.tws_common.current_symbol)
                if pos is None or pos.projected_quantity <= 0:
                    print("No position to close")
                    return True
                order = Order(self.tws_app.tws_common.current_symbol, OrderAction.SELL, pos.projected_quantity)
                self._place_order(order)
            case "c":
                if nargs == 1:
                    self.tws_app.cancel_last_order()
                    return True
                if args[1] == 'a':
                    self.tws_app.cancel_all_orders()
                    return True
                order_id = int(args[1])
                self.tws_app.cancel_order(order_id)
            case "export":
                if nargs == 1:
                    dest = "trades.csv"
                else:
                    dest = args[1]
                self.export_trades(dest)
            case "get":
                if nargs == 1:
                    print("No value provided")
                    return True
                if args[1] == "f":
                    if nargs > 2:
                        _sym = args[2]
                    else:   
                        _sym = self.tws_app.tws_common.current_symbol
                    if not _sym in self.tws_app.tws_common.fundamentals:
                        self.tws_app.tws_common.fundamentals[_sym] = StockFundamentals.from_fl(_sym)
                    print("==========Fundamentals for", _sym)
                    self.tws_app.tws_common.fundamentals[_sym].print()
                    print("==========")
                elif args[1] == "ask":
                    print("Current ask:", self.tws_app.tws_common.current_ask)
                elif args[1] == "bid":
                    print("Current bid:", self.tws_app.tws_common.current_bid)
                elif args[1] == "symbol":
                    print("Current symbol:", self.tws_app.tws_common.current_symbol)
            case _:
                if args[0].startswith("s") or args[0].startswith("x"):
                    return self._process_command([args[0][0], f"qm{args[0][1:]}"] + args[1:])
                else:
                    print("Invalid command")
        return True
    
    def _set_track(self, *args):
        if len(args) == 0:
            print("No value provided")
            return
        symbol = args[0].upper()
        self.tws_app.update_linked_group_by_symbol(symbol)

    def _get_order(self, action: OrderAction, *args):
        quantity = self.default_quantity
        if action == OrderAction.SELL:
            limit = self.tws_app.tws_common.current_bid * 0.98
        else:
            limit = self.tws_app.tws_common.current_ask * 1.01
        stop = None
        for arg in args:
            if arg.startswith("qm"):
                quantity = int(float(arg[2:]) * self.default_quantity)
            elif arg.startswith("q"):
                quantity = int(float(arg[1:]))
            elif arg.startswith("l"):
                limit = float(arg[1:])
            elif arg.startswith("st"):
                stop = float(arg[2:])
            else:
                limit = float(arg)
        return Order(self.tws_app.tws_common.current_symbol, action, quantity, limit, stop)

    def _set_parameters(self, *args):
        nargs = len(args)
        if nargs == 0:
            return
        match args[0]:
            case "default_quantity":
                if nargs == 1:
                    print("No value provided")
                    return
                self.default_quantity = int(args[1])
                print("Default quantity set to", self.default_quantity)
            case "allow_short":
                if nargs == 1:
                    print("No value provided")
                    return
                self.tws_app.tws_common.allow_short = True if args[1] == "1" else False
                print("Short selling is", "enabled" if self.tws_app.tws_common.allow_short else "disabled")
            case _:
                print("Unknown parameter")
        
    def export_trades(self, dest: str):
        export_funcs[self.tws_app.tws_common.config['export_csv_style']](dest, self.tws_app.tws_common.completed_orders)

    def _print_help(self):
        self.console.rule("Commands")
        self.console.print("link <id> [green]Link to a display group")
        self.console.print("t <symbol> [green]Track a symbol")
        self.console.print("x<quantity> <limit> st<stop> [green]Buy the tracked symbol")
        self.console.print("s<quantity> <limit> st<stop> [green]Sell the tracked symbol")
        self.console.print("cl [green]Close the current position for the tracked symbol")
        self.console.print("c [green]Cancel the last order")
        self.console.print("c <order_id> [green]Cancel order by id")
        self.console.print("c a [green]Cancel all orders")
        self.console.print("get f [green]Get fundamentals for the current symbol")
        self.console.print("get f <symbol> [green]Get fundamentals for the specified symbol")
        self.console.print("set <default_quantity <quantity>> [green]Set the default quantity, default is 100")
        self.console.print("set <allow_short <1|0>> [green]Set 1 to allow short selling")
        self.console.print("exit [green]Exit the program")
