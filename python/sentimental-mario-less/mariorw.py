# Recreate the half pyramid from Super Mario Bros


while height > 1 and height < 8:
    height = int(input("Height: "))
#return(height)

for i in range(height):
    for j in range(height - 2):
        print(" ")
        j += 1
    for k in range(i + 1):
        print("#")
        k += 1
    i += 1