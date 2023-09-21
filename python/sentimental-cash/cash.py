from cs50 import get_float


# Prompt for input
while True:
    usd = get_float("Change owed in dollars: ")
    if usd > 0:
        break
    else:
        print("Invalid Input")

change = round(int(usd * 100))

# Add to coins counter for each coin allocated
coins = 0
while change > 0:
    while change >= 25:
        coins += 1
        change -= 25
    while change >= 10:
        coins += 1
        change -= 10
    while change >= 5:
        coins += 1
        change -= 5
    while change >= 1:
        coins += 1
        change -= 1

print(coins)