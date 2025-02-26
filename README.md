# Clongule

# Useful commands when hosting instance

`SELECT setval('word_new_id_seq', COALESCE((SELECT MAX(id) FROM word), 1), TRUE);`

resets the id in the word table
