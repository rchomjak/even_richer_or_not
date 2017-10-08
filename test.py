#!/usr/bin/env python3.5

import asyncio

TEXT="Nieco python pekne atd"


def couroutine(func):
    def start(*args, **kwargs):
        couroutine_func = func(*args, **kwargs)
        next(couroutine_func)
        return couroutine_func
    return start

def generator_text(target):    
    print("Coroutine_text")

    for i in TEXT.split():
        target.send(i) 
    target.close()

@couroutine
def generator_grep(grep_text):
    print("Generator grep")
    try:
        while True:
            line = (yield)

            if grep_text in line:
                print(line)

    except GeneratorExit:
        print("Koniec generatora")


a = generator_text(generator_grep("python"))






