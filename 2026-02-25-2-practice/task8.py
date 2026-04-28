
# *  task 8

#! Task 8: Text File Processor
#! Write a program that:
#! Creates a text file and writes 5 user-provided sentences to it.
#! Reads the file and counts the total number of words and lines.
#! Creates a new file containing the same content but in reverse order (line by line).
#! Ensure proper file closing using with statements.

filepath = './Day-5/myFile.txt'

def write_sentences(count:int):
    with open(filepath, "w") as file:
        for line_number in range(1, count + 1):
            sentence = input(f"enter line {line_number} : ")
            file.write(sentence+'\n')
def read_lines():
    with open(filepath, "r") as file:
        print()

        data = file.readlines()
        print(f"total lines in file : {len(data)}")
        word_count = len(str(data).split())
        print(word_count,'\n')
        for line in data:
            print(line, end="")
        print()


def rev_file():
    with open(filepath,'r') as file:
        data = file.readlines()
    with open("./Day-5/newFile.txt",'w+') as file2:
        for line in data:
            file2.write(line[::-1].replace('\n','')+'\n')
        print("\nfile write success")

write_sentences(2)
read_lines()
rev_file()
