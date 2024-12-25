# IBKR Speed Day Trader
Interactive Broker Trader Workstation (IBKR TWS) isn't well tuned for fast paced momo day trading. This is my attempt to make it right.

### Features
- Fast keyboard based trading
- Fast fundamentals exploring
- (Planned) Spread warning
- (Planned) Technical indicator warning (MACD cross, EMAs, Volume etc.)

## Dependencies
- Python >= 3.13
- `python -m pip install -r requirements.txt`

## Use
Make your own copy of `config.json.example` and rename it to `config.json`. Edit accordingly to your preference. You must replace the values for IBKR accounts with your account numbers.

Then open a terminal in the current folder and type:
```
python run.py
```

## Commands
```
help
    Shows a quick command help.
    
link {id}
    Link with display group by id. The default value can be changed in config.json.
    e.g. "link 1" will link with display group 1, i.e. the red group.

t {symbol} or track {symbol}
    Track {symbol}. This changes the symbol that the linked display group is currently tracking.
    e.g. "t aapl" will switch all linked charts and panels to AAPL.

x
    Buy {default_quantity} shares of the tracked symbol at a limit price 1% higher than the current ask,
    essentially a safe market order. {default_quantity} is 100 by default and can be changed by
    "set default_quantity {quantity}". In all examples, I assume {default_quantity} is 100.

    -- Variant 1: x{k}
        Buy {k} x {default_quantity} shares
        e.g. "x10" will buy 1000 shares by default.

    -- Variant 2: x{k} {limit}
        Buy shares at {limit} price. {k} is optional.
        e.g. "x10 10.2" will buy 1000 shares at limit price $10.2. 
        Note that {limit} must be exactly the first argument after the space.

    -- Arguments:
        l{limit}
            Buy shares at {limit} price. e.g. "x l10.2" will buy 100 shares at limit price $10.2. 
            Note that this allows limit price to be attached at any place.

        qm{k}
            Same as "x{k}" but this allows {k} to be attached to the command at any place. 
            e.g. "x qm10" will buy 1000 shares. "qm" is short for quantity multiplier.

        q{a}
            Buy {a} amount of shares. 
            e.g. "x q10" will buy 10 shares.

        st{stop}
            Attach a stop order at {stop} price. 
            e.g. "x st9.2" will buy 100 shares and attach a stop order at $9.2 to the buy order.

        All these arguments can be used in combination in any orders. 
        However, "qm" and "q" will override each other depending on which comes later.
        e.g. "x q200 l10.2 st9.2" will buy 200 shares at a limit price of $10.2 attached with a stop order at $9.2. 
        A quicker way to write this would be: "x2 10.2 st9.2".

        Note that there must not be space between letters and numbers.

s
    Sell {default_quantity} shares of the tracked symbol at a limit price 2% lower than the current bid,
    essentially a safe market order. "s" command has the same variants and arguments:
    
cl
    Close the current position for the tracked symbol with a **market order**. 
    Note that this will not cancel existing sell orders.
    And the quantity to close will be the remaining quantity after all open sell orders are filled.

c
    Cancel order. When no argument is supplied, this cancels the latest order.

    -- Arguments:
        a
            Cancels all orders. e.g. "c a" will cancel all open orders.

        {order_id}
            Cancels a specific order identified by {order_id}. 
            e.g. "c 10" will cancel order #10.

get
    Get various information.

    -- Arguments:
        f
            Displays fundamentals for the tracked symbol.

        f {symbol}
            Displays fundamentals for the specified {symbol}. e.g. "get f aapl".
set
    Sets various configurations. Note the configuration is not saved to the "config.json" file
    and is only valid for the current session.

    -- Arguments:
        default_quantity {quantity}
            Sets the default quantity. e.g. "set default_quantity 100".

        allow_short {1|0}
            Set 1 to allow short selling or 0 to disable. e.g. "set allow_short 0".

exit
    To exit the program, with the prompt to export trades.
```

## TODO
1. `cl`: add an `oca` or `o` argument, i.e. one cancel all, to cancel all sell orders to close the full quantity.
2. `cl`: limit order instead of market order for extended trading hours.
3. `set`: save configurations to `config.json`
4. `exit`: option to bypass export.
