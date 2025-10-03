import random
import sys

def play():
    health = 100
    treasure = 0
    print("\n🏰 Welcome to 'Escape the Dungeon'!")
    print("Explore rooms, find treasure, but beware of traps and monsters...\n")

    while health > 0:
        print(f"❤️ Health: {health} | 🪙 Treasure: {treasure}")
        choice = input("Do you want to (e)xplore or (q)uit with your loot? ").lower()

        if choice == "q":
            print(f"\n🎉 You escaped safely with {treasure} gold coins!")
            break

        event = random.choice(["treasure", "trap", "monster", "empty", "exit"])

        if event == "treasure":
            found = random.randint(10, 50)
            treasure += found
            print(f"🪙 You found {found} gold coins!")
        elif event == "trap":
            damage = random.randint(5, 20)
            health -= damage
            print(f"💀 A trap! You lose {damage} health.")
        elif event == "monster":
            damage = random.randint(10, 30)
            fight = random.choice([True, False])
            if fight:
                health -= damage
                print(f"🐉 A monster attacked! You fought bravely but lost {damage} health.")
            else:
                print("🐉 You escaped a monster safely!")
        elif event == "empty":
            print("...The room is empty. Nothing here.")
        elif event == "exit":
            print(f"🚪 You found an exit! Escaping with {treasure} treasure...")
            break

    if health <= 0:
        print("\n☠ You died in the dungeon... but legends remember your courage!")

def main():
    while True:
        play()
        again = input("\nPlay again? (y/n): ").lower()
        if again != "y":
            print("Thanks for playing Escape the Dungeon! 👋")
            sys.exit()

if __name__ == "__main__":
    main()
