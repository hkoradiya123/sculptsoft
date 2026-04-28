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
import os

def clear_wait(func):
    def inner(*args, **kwargs):
        os.system('cls' if os.name == 'nt' else 'clear')
        func(*args, **kwargs)
        input()
    return inner
    inner()


class task:
    
    tasks = []
    file = "data.json"
    id_counter = 1
 
    priority_items = {
        '1':"low",
        '2':"medium",
        '3':"high"
    }
    complete_items = {
        "1":"incomplete",
        "2":"completed"
    }
    def __init__(self, description , id=None, priority="Medium", completed=False):
        if id != None:
            self.id = id
        else:
            self.id = task.id_counter
            task.id_counter+=1
        self.description = description
        self.priority = priority
        self.completed = completed
    
    def load_json():
        with open(task.file) as f:
            data = f.read()
            data = json.loads(data)
            for i in data:
                
                id = i['id']
                description = i['description']
                priority = i['priority']
                completed = i['completed']
                
                task1 = task(id=id, description=description, priority=priority, completed=completed)
                task.tasks.append(task1)
                
        task.id_counter = id + 1
        print(f"loaded {len(task.tasks)} tasks from {task.file}")
        print(f"next task id: {task.id_counter}")

    def __repr__(self):
        return f"task({self.id}, {self.description}, {self.priority}, {self.completed})"
    
    def update_json():
        data = []
        for i in task.tasks:
            data.append({
                "id":i.id,
                "description":i.description,
                "priority":i.priority,
                "completed":i.completed
            })
        with open(task.file, "w") as f:
            json.dump(data, f, indent=4)
            
            
    @clear_wait
    def display():
        # with open(self.file) as f:
        data = task.tasks
        for i in data:
            print(i)
    
    def add():
        description = input("enter task description : ")  
        priority = ""
        completed = ""
        while priority not in task.priority_items:
            priority = input("\nenter task priority \n1. low\n2. medium\n3. high \nenter number : ")      
        priority = task.priority_items[priority]     
        print(f"\npriority : {priority}\n")      
        while completed not in task.complete_items:
            completed = input("\nenter task completed \n1. Incomplete\n2. Completed\nenter number : ")        
        completed = task.complete_items[completed]   
        print(f"\ncompleted : {completed}\n")      
        mytask = task(description=description, priority=priority, completed=completed)       
        task.tasks.append(mytask)
        print(mytask)
        task.update_json()
        
    def remove():
        data = task.tasks
        for i in data:
            print(i)
        id = input("\nenter task id to delete : ")
        for i in task.tasks:
            if str(i.id) == id:
                task.tasks.remove(i)
                print(f"task with id {id} removed.")
                task.update_json()
                return
        print(f"task with id {id} not found.")
        
    def completed():
        data = task.tasks
        for i in data:
            print(i)
        id = input("\nenter task id to mark as completed : ")
        for i in task.tasks:
            if str(i.id) == id:
                i.completed = "completed"
                print(f"task with id {id} marked as completed.")
                task.update_json()
                return
        print(f"task with id {id} not found.")
        

def menu():
    # os.system('cls' if os.name == 'nt' else 'clear')
    print("-"*30)
    for i,j  in menu_items.items():
        print(f"{i}. {j}")
    print(f'{len(menu_items.keys())+1}. exit')
    print("-"*30)
    
    inp = input("enter a number : ")
    return inp

menu_items = {
    "1":"list all tasks.",
    "2":"add new task.",
    "3":"delete task.",
    "4":"mark task as completed"
}

operations = {
    "1":task.display,
    "2":task.add,
    "3":task.remove,
    "4":task.completed
}

def main():
    try :
        global menu_items
        task.load_json()
        while True:
            os.system('cls' if os.name == 'nt' else 'clear')
            inp = menu()
            if inp in menu_items.keys():
                print(f"found : {inp}")
                print("-"*30)
                operations[inp]()
            elif inp == str(len(menu_items.keys()) + 1):
                print("\nExiting...")
                break
            else:
                print(f"number not found.")

    except KeyboardInterrupt:
        print("\nExiting...")

if __name__ == "__main__":
    main()
