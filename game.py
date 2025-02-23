import json
import random

words = {}
clongs = []


def init():
    """
    Initialises the game so that all clongs and their words can be accessed by the program
    :return:
    """
    global words, clongs
    with open('words.json', encoding='utf-8', mode='r') as f:
        unparsed_words = f.read()

    words = json.loads(unparsed_words)
    clongs = list(words.keys())

def main():
    init()
    print(clongs)

if __name__ == "__main__":
    main()