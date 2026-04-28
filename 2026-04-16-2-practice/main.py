# Create a class hierarchy (e.g., Animal parent class, Dog and Cat child classes)
# Implement polymorphism with a common method


from abc import ABC, abstractmethod

class Animal(ABC):

    @abstractmethod
    def sound(self):
        pass

    @abstractmethod
    def move(self):
        pass


class Dog(Animal):
    
    def sound(self):
        print("Dog is barking")

    def move(self):
        print("The dog runs.")
        
        

class Snake(Animal):
    
    def sound(self):
        print("Snake is hissing")

    def move(self):
        print("The snake crowling.")


mydog = Dog()
mydog.sound()  
mydog.move()

mysnake = Snake()
mysnake.sound()
mysnake.move()  
