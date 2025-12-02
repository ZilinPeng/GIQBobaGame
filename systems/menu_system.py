def choose_price(drink):
    try:
        new_price = float(input(f"New price for {drink.name}: "))
        if new_price >= 0:
            drink.setPrice(new_price)
            print("Price updated.")
    except ValueError:
        print("Invalid price.")