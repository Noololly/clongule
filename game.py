import random
from psqltest import SQLConn

words = {}
clongs = []


def init():
    """
    Initialises the game so that all clongs and their words can be accessed by the program
    :return:
    """
    global clongs

    conn = SQLConn() #create the connection to the database
    cur = conn.conn.cursor()
    cur.execute("SELECT DISTINCT lang FROM clongule") #get all individual clongs
    clongs = [row[0] for row in cur.fetchall()] #format it into a usable format

def main():
    init()


if __name__ == "__main__":
    main()