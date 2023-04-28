#!/usr/bin/env python3

import sys
import random
from wonderwords import RandomWord

DEFAULT_NUMBER_OF_REQUESTS = 4
STATIONS = ['A', 'B', 'C', 'D']


if __name__ == '__main__':
    num_of_requests = DEFAULT_NUMBER_OF_REQUESTS
    time = -1
    pos_gen = RandomWord(station=STATIONS)
    word_gen = RandomWord()
    
    if len(sys.argv) > 1:
        num_of_requests = int(sys.argv[1])
    
    for _ in range(num_of_requests):
        time += random.randint(1, 25)
        src = pos_gen.word()
        dst = pos_gen.word()
        weight = random.randint(1, 150)
        content = word_gen.word(include_categories=['noun'])
        # No established multi-word expressions
        #content = word_gen.word(include_categories=['noun'], regex=[^ ]*)
        
        print(f'{time},{src},{dst},{weight},{content}')       
    