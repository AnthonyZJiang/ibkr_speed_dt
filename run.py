from ibkr_keyboard_trader import Trader
import sys

if __name__ == '__main__':
    while True:
        ans = input("Simulation or live account? (sim/live/cancel): ")
        if ans in ['sim', 'live']:
            break
        elif ans == 'cancel':
            sys.exit(0)
        else:
            print("Invalid input")
    front = Trader(ans)
    front.run()