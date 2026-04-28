import math
import timeit
# Task 1: String Manipulation
# Write a program that:
# Takes a user's full name as input.
# Converts the name to uppercase, lowercase, and title case.
# Counts the number of vowels in the name.
# Reverses the name and prints it.


# inp = input("Enter Full Name : ")
# print(f'upper case : {inp.upper()}')
# print(f'lower case : {inp.lower()}')
# print(f'first letter upper case : {inp.capitalize()}')

# vovel_count = 0
# consonent_count = 0

# for i in inp:
#     if i == " " :
#         continue
#     if i in "aeiouAEIOU":
#         vovel_count+=1

#     elif i in "bcdfghjklmpqrstvwxyz"+"bcdfghjklmpqrstvwxyz".upper():
#         consonent_count+=1

# print(f'total vovels in name : {vovel_count}')
# print(f"total consonent in name : {consonent_count}")
# print(f"Reversed name : {inp[::-1]}")


# Task 2: Grade Calculator (Using Conditional Statements and loops only)
# Write a program that accepts a student's score (0–100) as input.
# Assign a letter grade based on the following criteria:
# 90–100: A
# 80–89: B
# 70–79: C
# 60–69: D
# Below 60: F
# Print the score and the corresponding grade.
# Validate the input to ensure it’s between 0 and 100.


inp = int(input("enter grade ( 1-100 ) : "))
if  (0 <= inp >= 100):
    print("enter number between 1 to 100")
else:
    if (inp < 60): print("student have failed")
    elif(60 <= inp <= 69): print("grade D")
    elif(70 <= inp <= 79): print("grade C")
    elif(80 <= inp <= 89): print("grade B")
    elif(90 <= inp <= 100): print("grade A")


# Task 3: Prime Number Checker (Using Conditional Statements and loops only)
# Write a program that takes a number as input and checks if it is a prime number.
# A prime number is a natural number greater than 1 that has no positive divisors other than 1 and itself.
# Use a loop to check for divisibility and optimize the loop to run only up to the square root of the number.
# Kavish Shah, 3 min
# Programs Using Functions ONLY:-

import math
inp = int (input("enter a prime number : "))
for i in range (2,math.floor(math.sqrt(inp))):#2,3.112
    if inp % i == 0 :                          #2,3
        print("not prime number ",inp)
        break
else:
    print("prime number")


# Task 4: Factorial Calculator
# Write a function factorial(n) that calculates the factorial of a non-negative integer n using both iterative and recursive approaches.
# Compare the performance of both methods for a user-provided input (e.g., using time module).
# Handle invalid inputs (e.g., negative numbers).

def factorial(num):
    fact = 1
    for i in range (1,num+1):
        fact *= i
    return fact

def rec_fact(num):
    if num == 1: return 1
    else:
        return rec_fact(num-1) * num

try:
    num = int(input('enter positive number for factorial : '))

    if num < 0:
        print("invalid number : ", num)
    else:
        time_one = timeit.timeit(
            lambda: factorial(num), number=1000
        )

        # Time the execution of method_two
        time_two = timeit.timeit(
            lambda: rec_fact(num), number=1000
        )

        print(f"Method One average time: {time_one:.6f} seconds")
        print(f"Method Two average time: {time_two:.6f} seconds")

        if time_one < time_two:
            print("Method One is faster.")
        else:
            print("Method Two is faster.")

        print(f'{num} : {factorial(num)}')
        # print(rec_fact(num))
except Exception :
    print("invalid Number")

# Task 5: Palindrome Checker
# Write a function is_palindrome(s) that checks if a given string is a palindrome (ignoring spaces, case, and punctuation).
# Example: "A man a plan a canal Panama" should return True.
# Test the function with at least 5 different inputs.

test = [
    "madam",
    "python",
    "level",
    "world",
    "radar",
    "code",
    "refer",
    "data",
    "civic",
    "hello",
    "A man a plan a canal Panama"
]
# inp = input("enter pelindrome string : ")

def pelidrome(inp):
    inp= str(inp)
    new = inp.replace(" ",'').lower()

    if new == new[::-1]:
        print('--pelindrom--')
        print(inp)
        # return True
    else:
        print('--not pelindrom--')
        print(inp)
        # return False

for i in test : print(pelidrome(i))
