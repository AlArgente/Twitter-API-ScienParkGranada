"""Functions to create the database, to create the tables and other possible functions on the database.
"""

from db_tables import TablesEnum

def check_table_exists_or_create_it(mydb, table_name='Twitter'):
    """Function that check if a table exists on the database, and create
    it if it doesn't exists.

    Args:
        mydb (MySQL connector): Connection to the database.
        table_name (str, optional): Name of the table to check. Defaults to 'Twitter'.
    """
    mycursor = mydb.cursor()
    mycursor.execute("""
                        SELECT COUNT(*)
                        FROM information_schema.tables
                        WHERE table_name = '{0}'
                        """.format(table_name)
    )
    if mycursor.fetchone()[0] != 1:
        if table_name.upper() in TablesEnum.__members__.keys():
            table_attributes = TablesEnum[table_name.upper()].value
        else:
            raise ValueError(f"The table {table_name} can't be created. Try with: " + ', '.join([t.name for t in TablesEnum]))
        mycursor.execute("""CREATE TABLE {} ({})
                            """.format(table_name, table_attributes))
        mydb.commit()
        print("Table created.")
    mycursor.close()