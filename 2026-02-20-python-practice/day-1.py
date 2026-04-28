"""
Task 1:
Take a sentence as input and print:
Total characters (including spaces)
Total characters (excluding spaces)
Total vowels
Total consonants
Whether the sentence is palindrome (ignore spaces)
"""

# inp = input("ENTER A SENTENCE : ")
# out_with_space = {}
# out_without_space = {}
# out_vowels = set()
# out_consonents = set()
# vowels_count = 0
# consonent_count = 0

# for i in inp:
#     if i not in out_with_space:
#         out_with_space[i]= inp.count(i)
#     if i not in out_without_space and i != ' ':
#         out_without_space[i]=  inp.count(i)
#     if i in "AEIOUaeiou":
#         out_vowels.add(i)
#         vowels_count+=1
#     elif i != ' ':
#         consonent_count+=1
#         out_consonents.add(i)
    

# print(f'Total count with space : ',out_with_space)
# print(f'Total count without space : ',out_without_space)
# print(f'vovels : ',*out_vowels)
# print(f'consonents : ',*out_consonents)
# print("total vovles : ",vowels_count)
# print("total consonents : ",consonent_count)

# if inp.replace(' ','') == inp.replace(' ','')[::-1]:
#     print(f'string {inp} is pelindrome')
# else:
#     print(f'string {inp} is not pelindrome')
    


    




"""
Task 2:
Take a sentence.
Store each word and its frequency in dictionary.

Example:-
Input:
python is easy and python is powerful

Output:
python : 2
is : 2
easy : 1
and : 1
powerful : 1
"""

# inp = input("enter a sentence : ")
# out = {}
# for i in inp.split(" "):
#     if i not in out:
#         out[i]=inp.count(i)
# print(out)




"""
Task 3:-
Smart Calculator
Take 3 inputs:
First number
Operator (+, -, *, /)
Second number
Perform operation manually.
Rules:
If division and second number is 0 → print "Cannot divide by zero"
If operator invalid → print "Invalid Operator"

Example:-
Input:
10
*
5

Output:
50
"""

# print(eval(input()))



while(True):
    try:  
        print(f'----------tap ctrl c to exit -------')

        op1 = int(input("enter oprand one :"))
        op2 = int(input("enter oprand two :"))
        opr = input("enter oprator :")

        if opr in '/*%+^-':
            if (opr == "/" and op2 ==0):
                print(f'--zero devision error--')  # handle zero devision error
                continue
            result = eval(f"{op1}{opr}{op2}")
            print(f"Result: {result}")
    except KeyboardInterrupt:
        print("\nExiting the program")
        break
    except Exception:
        continue


        # if (opr == '*'):
        #     print(f'{op1} {opr} {op2} = {op1*op2}')
        # elif(opr=="/"):
        #     if op2 != 0:
        #         print(f'{op1} {opr} {op2} = {op1/op2}')
        #     else:
        #         print("oprator two is zero try again")
        # elif(opr=="+"):
        #     print(f'{op1} {opr} {op2} = {op1+op2}')
        # elif(opr=="-"):
        #     print(f'{op1} {opr} {op2} = {op1-op2}')
        # elif(opr=="%"):
        #     print(f'{op1} {opr} {op2} = {op1%op2}')

# while(True):
#     try:     
#         print(f'----------tap ctrl c to exit -------')
#         op1 = int(input("enter oprand one :"))
#         op2 = int(input("enter oprand two :"))
#         opr = input("enter oprator :")

#         if (opr == '*'):
#             print(f'{op1} {opr} {op2} = {op1*op2}')
#         elif(opr=="/"):
#             if op2 != 0:
#                 print(f'{op1} {opr} {op2} = {op1/op2}')
#             else:
#                 print("oprator two is zero try again")
#         elif(opr=="+"):
#             print(f'{op1} {opr} {op2} = {op1+op2}')
#         elif(opr=="-"):
#             print(f'{op1} {opr} {op2} = {op1-op2}')
#         elif(opr=="%"):
#             print(f'{op1} {opr} {op2} = {op1%op2}')
#     except KeyboardInterrupt:
#         print("exiting the program")
#         break
#     except Exception:
#         continue
    