import psqltest

connection = psqltest.SQLConn() #open connection to database

def get_word():
    lang = get_lang()
    query = f"""
        SELECT word
        FROM clongule
        WHERE lang = '{lang}'
        ORDER BY random()
        LIMIT 1;"""
    cur = connection.conn.cursor()
    cur.execute(query)
    word = cur.fetchone()[0]

    query = """
        INSERT INTO word (lang, word)
        VALUES (%s, %s);
    """
    cur.execute(query, (lang, word))
    connection.conn.commit()


def get_lang(): #this gets a random clong that hasn't been used in the last 2 days
    query = """
        SELECT lang
        FROM clongule
        ORDER BY RANDOM()
        LIMIT 1;
        """
    cur = connection.conn.cursor()
    cur.execute(query)
    lang = cur.fetchall()
    lang = lang[0][0]

    if lang not in get_previous_lang(): # if the clong hasn't been used in the last 2 days, insert into the table, and return true
        return lang
    else:
        return False



def get_previous_lang(): #this gets the previous 2 clongs
    cur = connection.conn.cursor()

    previous_lang_query = f"""
    SELECT lang FROM word
    ORDER BY id DESC
    LIMIT 2;
    """

    cur.execute(previous_lang_query)
    previous_lang = cur.fetchall()
    try:
        previous_lang_1 = previous_lang[0][0]
        previous_lang_2 = previous_lang[1][0]
    except IndexError:
        previous_lang = (None, None)
        return previous_lang
    if previous_lang_1 is not None and previous_lang_2 is not None:
        previous_lang = (previous_lang_1, previous_lang_2)
        return previous_lang
    else:
        previous_lang = (previous_lang_1, None)
        return previous_lang


get_word()