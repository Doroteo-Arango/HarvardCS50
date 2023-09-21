from cs50 import get_string

text = get_string("Text: ")

length = len(text)
letters = 0
words = 0
sentences = 0

# Loop for counting
for i in range(length):
    c = text[i]

    # Count letters
    if c.isalpha():
        letters += 1

    # Count words
    if c == " ":
        words += 1

    # Count sentences
    if c == "." or c == "!" or c == "?":
        sentences += 1

# Account for last word
words = words + 1

# Calculate Grade
l = letters / words * 100
s = sentences / words * 100

subindex = 0.0588 * l - 0.296 * s - 15.8
index = round(subindex)

if index > 16:
    print("Grade 16+")
elif index > 1 and index < 17:
    print(f"Grade {index}")
else:
    print("Before Grade 1")