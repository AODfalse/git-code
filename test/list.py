mylist = []
mylist.append(1)
mylist.append(2)
mylist.append(3)
print(mylist[0]) # prints 1
print(mylist[1]) # prints 2
print(mylist[2]) # prints 3

# prints out 1,2,3
for x in mylist:
    print(x)

squared = 7 ** 2
cubed = 2 ** 3
print(squared)
print(cubed)

# 两个列表相加可以使用 + 操作符
list1 = [1, 2, 3]
list2 = [4, 5, 6]
combined_list = [a + b for a, b in zip(list1, list2)]
print(combined_list)  # 输出: [1, 2, 3, 4, 5, 6]

phonebook = {  
    "John" : 938477566,
    "Jack" : 938377264,
    "Jill" : 947662781
}  
# your code goes here
phonebook["Jake"] = 938273443
phonebook.pop("Jill")
# testing code
if "Jake" in phonebook:  
    print("Jake is listed in the phonebook.")
    
if "Jill" not in phonebook:      
    print("Jill is not listed in the phonebook.")
