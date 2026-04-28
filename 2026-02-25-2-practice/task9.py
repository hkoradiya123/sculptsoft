'''
Task 9: Robust Input Validator
Write a program that:
Prompts the user to enter an integer.
Uses exception handling to catch invalid inputs (e.g., non-integer inputs like "abc").
Keeps prompting until a valid integer is entered.
Once a valid integer is received, checks if it’s even or odd and prints the result.
'''


while True:
    try:
        inp = int(input("enter a integer : "))
        print("zero" if inp==0 else "even" if inp%2==0 else "odd")
        break
    except Exception:
        print("invlid input")