from game import Game
from config import TURNS_PER_DAY, STARTING_CASH

def main():
    print("=== BOBA TYCOON — ONE DAY SIMULATION TEST ===\n")

    game = Game()

    print(f"Starting Day {game.day} with ${game.cash:.2f} cash.\n")
    print(f"Simulating {TURNS_PER_DAY} turns...\n")

    served_total = 0
    lost_queue = 0
    lost_stock = 0
    lost_patience = 0

    # Run one day manually using single_turn()
    for turn in range(TURNS_PER_DAY):
        served, lostQ, lostS, lostP = game.single_turn()

        served_total   += served
        lost_queue     += lostQ
        lost_stock     += lostS
        lost_patience  += lostP

        print(f"Turn {turn+1:02d}: "
              f"Served={served}, "
              f"LostQ={lostQ}, "
              f"LostStock={lostS}, "
              f"LostPat={lostP}, "
              f"Cash=${game.cash:.2f}")

    # End-of-day accounting (same logic as run_days but only 1 day)
    wages = sum(e.wage for e in game.employees)
    rent = game.venue.rent
    revenue_today = game.cash - STARTING_CASH
    profit = revenue_today - wages - rent

    game.cash -= (wages + rent)

    print("\n=== DAY SUMMARY ===")
    print(f"Served total         : {served_total}")
    print(f"Lost from queue      : {lost_queue}")
    print(f"Lost from stock      : {lost_stock}")
    print(f"Lost from patience   : {lost_patience}")

    print(f"\nRevenue generated    : ${revenue_today:.2f}")
    print(f"Wages cost           : -${wages:.2f}")
    print(f"Rent cost            : -${rent:.2f}")
    print(f"PROFIT               : ${profit:.2f}")
    print(f"Ending cash          : ${game.cash:.2f}\n")

    print("Test simulation complete.")

if __name__ == "__main__":
    main()