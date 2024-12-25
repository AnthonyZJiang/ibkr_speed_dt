from rich import print

from finvizlite import *

class StockFundamentals():
    
    def __init__(self, symbol) -> None:
        self.symbol = symbol
        self.mark_cap = 0
        self.float = 0
        self.shortable_shares = 0
        self.short_ratio = 0
        self.country = ""
        self.exchange = ""
        self.short_name = ""
        self.ceo = ""
        self.sector = ""
    
    @staticmethod
    def from_yf(ticker_info):
        def get_key_value(key, dict, default=None):
            return dict[key] if key in dict else default
        f = StockFundamentals(ticker_info["symbol"])
        f.symbol != ticker_info["symbol"]
        f.mark_cap = get_key_value("marketCap", ticker_info, -1)
        f.float = get_key_value("floatShares", ticker_info, -1)
        f.shortable_shares = get_key_value("shortableShares", ticker_info, -1)
        f.country = get_key_value("country", ticker_info, "Unknown")
        f.exchange = get_key_value("exchange", ticker_info, "Unknown")
        f.short_name = get_key_value("shortName", ticker_info, "Unknown")
        f.sector = get_key_value("sector", ticker_info, "Unknown")
        ceo_found = False
        for officer in get_key_value("companyOfficers", ticker_info, []):
            title = get_key_value("title", officer, "").lower()
            if title and 'ceo' in title:
                f.ceo = get_key_value("name", officer, "Unknown")
                ceo_found = True
                break
        if not ceo_found and "companyOfficers" in ticker_info and len(ticker_info["companyOfficers"]) > 0:
            f.ceo = get_key_value("name", ticker_info["companyOfficers"][0], "Unknown")
        return f
    
    @staticmethod
    def from_fl(sym):
        def get_key_value(key, dict, default=None):
            return dict[key] if key in dict else default
        f = StockFundamentals(sym)
        ticker_info = FinvizLite(sym).ticker_fundament()
        f.mark_cap = get_key_value(FKey.market_cap, ticker_info, -1)
        f.float = get_key_value(FKey.shs_float, ticker_info, -1)
        f.shortable_shares = get_key_value(FKey.short_float, ticker_info, -1)
        f.short_ratio = get_key_value(FKey.short_ratio, ticker_info, -1)
        f.country = get_key_value(FKey.country, ticker_info, "Unknown")
        f.exchange = get_key_value(FKey.exchange, ticker_info, "Unknown")
        f.short_name = get_key_value(FKey.company, ticker_info, "Unknown")
        f.sector = get_key_value(FKey.sector, ticker_info, "Unknown")
        f.ceo = "Unknown"
        return f
        
    def print(self) -> None:
        float_val = self.numeric_description_to_num(self.float)
        float_color = "[green]" if float_val < 2000000 else "[orange]" if float_val< 5000000 else "[red]"
        country_color = "[red]" if self.country.lower() == "china" else "[green]"
        print(f"Symbol: [green]{self.symbol}")
        print(f"Short Name: [green]{self.short_name}")
        print(f"Sector: [green]{self.sector}")
        print(f"Market Cap: [green]${self.mark_cap}")
        print(f"Float: {float_color}{self.float}")
        print(f"Shortable Shares: [green]{self.shortable_shares}")
        print(f"Short ratio: [green]{self.short_ratio}")
        print(f"Country: {country_color}{self.country}")
        print(f"CEO: [green]{self.ceo}")
        print(f"Exchange: [green]{self.exchange}")
        
    @staticmethod
    def numeric_description_to_num(num):
        try:
            '30B, 30M, 30K, 30'
            if num[-1] == 'B':
                return float(num[:-1]) * 1000000000
            elif num[-1] == 'M':
                return float(num[:-1]) * 1000000
            elif num[-1] == 'K':
                return float(num[:-1]) * 1000
            else:
                return float(num)
        except ValueError:
            return None
        except TypeError:
            return None
        except Exception as e:
            print(f"Error converting {num} to number: {e}")
            return None