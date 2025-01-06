import logging
import json

from ibkr_speed_dt.util.twslogging import setup_logger
from .datastore.order import Order
from ..util.fundamentals import StockFundamentals
from .datastore.accountentry import TWSAccountEntry

DEF_TICK_REQ_ID = 2000
DEF_CONTRACT_DETAIL_REQ_ID = 19000
DEF_SUB_GROUP_ID = -1

class TWSCommon:
    
    def __init__(self, platform_type: str):
        self.trade_logger = setup_logger('trade', None, logging.INFO, 'trade.log.csv')
        self.logger = setup_logger('twsapp', logging.INFO, logging.DEBUG, 'twsapp.log')
        
        self.platform_type = platform_type
        self.allow_short = False
        self.ibkr_port = 0
        self.ibkr_account = ''
        
        self.exit_flag = False
        self.is_ready = False
        self.tick_req_id: int = DEF_TICK_REQ_ID
        self.tick_req_id_symbol_map: dict[int, str] = {}
        self.fundamentals: dict[str, StockFundamentals] = {}
        self.completed_orders: dict[int, Order] = {}
        self.open_orders: dict[int, Order] = {}
        self.current_positions: dict[str, TWSAccountEntry] = {}
        
        self.contract_detail_req_id: int = DEF_CONTRACT_DETAIL_REQ_ID
        self.subscribed_group_id: int = DEF_SUB_GROUP_ID
        self.req_id_callback_map: dict[int, callable] = {}
        
        self.current_contract = None
        self.current_symbol = None
        self.current_bid = 0
        self.current_ask = 0
        
        self.gui_update_callback_tracked_symbol = None
        
        self.get_config()

    def get_config(self):
        with open('config.json') as f:
            self.config = json.load(f)
        
        self.allow_short = self.get_dict_value(self.config, 'allow_short', False)
        self.ibkr_port = self.get_dict_value(self.config, f'ibkr_port_{self.platform_type}', 7497)
        self.ibkr_account = self.get_dict_value(self.config, f'ibkr_account_{self.platform_type}', '')
        
    @staticmethod
    def get_dict_value(dict_obj: dict, key: str, default=None):
        return dict_obj[key] if key in dict_obj else default