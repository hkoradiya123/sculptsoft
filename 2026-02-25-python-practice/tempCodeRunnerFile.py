
inp = int(input("enter grade ( 1-100 ) : "))
if  (0 <= inp >= 100):
    print("enter number between 1 to 100")
else:
    if (inp < 60): print("student have failed")
    elif(60 <= inp <= 69): print("grade D")
    elif(70 <= inp <= 79): print("grade C")
    elif(80 <= inp <= 89): print("grade B")
    elif(90 <= inp <= 100): print("grade A")