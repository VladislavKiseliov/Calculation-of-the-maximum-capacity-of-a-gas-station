import pickle

class A:
    def __init__(self):
        self.a =5
    def prin(self):
        print("Good")

a=A()

print(f"{a=}")
serialized_manager = pickle.dumps(a)
print(f"{serialized_manager=}")
# Восстанавливаем объект
manager = pickle.loads(serialized_manager)
print(f"{manager=}")
print(manager.prin())

dic = {"in":0,"out":2}


for i in dic:
    print(i)