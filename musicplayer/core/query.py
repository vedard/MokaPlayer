""" Contains all the static SQL query needed for the applications
"""

ADD_SONG = "INSERT INTO SONG VALUE(?,?,?,?,?,?)"
REMOVE_SONG = "DELETE SONG WHERE id = ?"
