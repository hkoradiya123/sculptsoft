# Welcome to Day-5
# This is your coding workspace
import random 
'''
Task 6: List Operations
Write a program that:
Creates a list of 10 random integers between 1 and 100 (use random module).
Finds the minimum, maximum, and average of the list.
Removes duplicates from the list without using a set.
Sorts the list in ascending and descending order.
'''


# myList = [random.randint(1,100) for i in range(10)]
# print(myList)

# print(f'max : {max(myList)}')
# print(f'min : {min(myList)}')

# myList_without_dublicates = [val for val in myList if myList.count(val)==1]
# print('list without dublicates : {myList_without_dublicates}')
# sorted_list = sorted(myList)
# print(f'sorted list : {sorted_list}')


# red ---------------------------------------------------------------------------------------------
# inp = input("Enter Full Name : ")
# print(f'upper case : {inp.upper()}')
# print(f'lower case : {inp.lower()}')
# print(f'first letter upper case : {inp.capitalize()}')

# vovel_count = 0
# consonent_count = 0
# vovel = 'aeiouAEIOU'
# for i in inp:
#     if i == " " :
#         continue
#     if i in vovel:
#         vovel_count+=1

#     elif i not in vovel and i.isalpha() == True:
#         consonent_count+=1

# print(f'total vovels in name : {vovel_count}')
# print(f"total consonent in name : {consonent_count}")
# print(f"Reversed name : {inp[::-1]}")
# red ---------------------------------------------------------------------------------------------


'''
Task 7: Dictionary-Based Inventory System
Create a simple inventory system using a dictionary where keys are item names and values are quantities.
Write functions to:
Add a new item to the inventory.
Update the quantity of an existing item.
Remove an item from the inventory.
Display the entire inventory in a formatted manner.
Handle cases where the user tries to update/remove a non-existent item.
'''


class MyInventory:
    Inventory = {
        "Laptop": 5,
        "Mouse": 20,
        "Keyboard": 15,
        "Monitor": 8,
        "USB Cable": 50
    }

    def addItem(self, item_name:str , Quantity:int):
        if item_name not in self.Inventory:
            self.Inventory[item_name] = Quantity
            print(f'\nitem {item_name} is added to inventry with quentity of {Quantity}')
        else:
            print(f'\n{item_name} is already exist in Inventory \n(use updateItem() to update value)')


    def updateItem(self , item_name:str , Quantity:int):
        if item_name in self.Inventory:
            self.Inventory[item_name] = Quantity
            print(f"\nitem {item_name} is updated to inventry with quentity of {Quantity}")
        else:
            print(f"\n{item_name} is not exist in Inventory \n(use addItem() to update value)")


    def removeItem(self , item_name:str):
        if item_name in self.Inventory:
            self.Inventory.pop(item_name)
            print(f"\nitem {item_name} is removed from inventry")
        else:
            print(f"\n{item_name} is not exist in Inventory \n(use addItem() to add item first)")


    def removeAllItem(self):
        if self.Inventory:
            self.Inventory.clear()
            print(f"\nall item is removed from inventry")
        else:
            print(f"\nInventory is already empty")


    def displayInventory(self):
        if self.Inventory:
            print("\nInventery : ")
            for item in list(self.Inventory.keys()):
                print(f"  {item} : {self.Inventory[item]}")
        else:
            print("\nInventery is empty.")



Inventory = MyInventory()

Inventory.displayInventory()
Inventory.addItem("povbhaji",2)
Inventory.displayInventory()
# Inventory.addItem()
Inventory.removeAllItem()
Inventory.removeAllItem()


# red ---------------------------------------------------------------------