from rich.prompt import Prompt

from ibkr_speed_dt import Trader
import sys

if __name__ == '__main__':
    ans = Prompt.ask("Simulation or live account", choices=["sim","live", "cancel"], default="sim")
    if ans == 'cancel':
        sys.exit(0)
    front = Trader(ans)
    front.run()