from framework.singletones import SingletonByName
import time
import itertools


# Заметка, можно применить стратегию если добавить стратегию логирования
class Logger(metaclass=SingletonByName):

    def __init__(self, name):
        self.name = name

    def log(self, text):
        print('log--->', text)


# декоратор
def debug(func):
    def inner(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f'DEBUG--------> вызвана функция "{func.__qualname__}", время выполнения'
              f' {round((end - start), 3)} секунд')
        return result

    return inner