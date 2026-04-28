from main import Animal

class elephant(Animal):
    def sound(self):
        print("Elephant is trumpetsing")
    def move(self):
        print("The elephant is walking.")   

myelephant = elephant()
myelephant.sound()
myelephant.move()