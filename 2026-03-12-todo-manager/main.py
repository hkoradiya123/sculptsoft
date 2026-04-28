'''
Task 11: Simple To-Do List Manager
Create a command-line to-do list application that:
Allows users to add tasks with a description and priority (Low, Medium, High).
Displays all tasks sorted by priority.
Marks tasks as completed or deletes them.
Saves tasks to a file and loads them when the program starts.
Uses a list of dictionaries to store tasks (e.g., [{"description": "Buy groceries", "priority": "High", "completed": False}, ...]).
Handle all possible errors (e.g., invalid priority, file not found).
'''

import json

data = [
    {"id":1,"description": "Buy groceries", "priority": "High", "completed": False},
    {"id":2,"description": "sell jewellery", "priority": "High", "completed": False},
    {"id":3,"description": "Complete project report", "priority": "High", "completed": False},
    {"id":4,"description": "Call dentist", "priority": "Medium", "completed": False},
    {"id":5,"description": "Reply to emails", "priority": "Medium", "completed": True},
    {"id":6,"description": "Water plants", "priority": "Low", "completed": False},
    {"id":7,"description": "Organize desk", "priority": "Low", "completed": False},
    {"id":8,"description": "Book flight tickets", "priority": "High", "completed": False},
]

def file_data() -> list :
    with open("data.txt",'r') as f:
        data = json.load(f)
        # print(data)
    return data

def write_data(data) -> None:
    with open("data.txt",'w') as f:
        json.dump(data, f)

def print_to_do_list():
    to_do_list = file_data()
    for to_do in to_do_list:
        print(f"Description : {to_do['description']}")
        print(f"  id : {to_do['id']}")
        print(f"  priority : {to_do['priority']}")
        print(f"  completed : {to_do['completed']}\n")

def new_to_do(description,priority,complited):
    to_do_list = file_data()
    to_do = {
        "id": 8,
        "description": "Book flight tickets",
        "priority": "High",
        "completed": False
    }
    to_do_list.append(to_do)
    write_data(to_do_list)

def print_menu():
    print("1. view all to-do ")
    print("2. add to-do")
    print("3. modify-do")
    print("4. delete-do")
    print("5. delete-all-do")
    print("6. exit..")

choice = {
    "1": lambda:print_to_do_list(),
    "2": lambda:print_to_do_list(),
    "3": lambda:print_to_do_list(),
    "4": lambda:print_to_do_list(),
    "5": lambda:print_to_do_list(),
    "6": lambda:print_to_do_list()
}

def main():

    while True:
        print_menu()
        inp = input("\nenter your choice : ")
        if inp in choice:
            choice[inp]()
        elif inp == list(choice.keys()).count() + 1:
            print("exiting program....")
        else:
            print('invalid choice...')

if __name__ == "__main__":
    main()
