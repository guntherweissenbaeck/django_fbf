# establish connection to database
import os
import psycopg2
import psycopg2.extras
import psycopg2.extensions

host = os.environ['DB_HOST']
database = os.environ['DB_NAME']
user = os.environ['DB_USER']
password = os.environ['DB_PASSWORD']
port = os.environ['DB_PORT']


conn = psycopg2.connect(
    host=host,
    database=database,
    user=user,
    password=password,
    port=port)
conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

# check if column finder exists in table bird_fallenbird
cur.execute("SELECT column_name FROM information_schema.columns WHERE
            table_name = 'bird_fallenbird' AND column_name = 'finder'")

# if column finder does not exist in table bird_fallenbird, add column
# finder to table bird_fallenbird
if not cur.fetchone():
    cur.execute("alter table bird_fallenbird add column finder text")

# query the table rescuer_rescuer and write the results to a variable
cur.execute("SELECT * FROM rescuer_rescuer")
rescuer_rescuer = cur.fetchall()

# query the table bird_fallenbird with its columns id and rescuer_id and
# write the results to a variable
cur.execute("SELECT id, rescuer_id FROM bird_fallenbird")
bird_fallenbird = cur.fetchall()

# iterate over the results of the query bird_fallenbird
# for each row, iterate over the results of the query rescuer_rescuer
# if the rescuer_id of the bird_fallenbird row matches the id of the
# rescuer_rescuer row, update the bird_fallenbird row finder with
# all the data of the rescuer_rescuer
# all rows of rescuer_rescuer should be inserted into the column finder of
# bird_fallenbird with the same rescuer_id
for row in bird_fallenbird:
    for rescuer in rescuer_rescuer:
        if row['rescuer_id'] == rescuer['id']:
            # the data should be in the format column_name: column_value
            finder = ''
            for key, value in rescuer.items():
                # exclude the id column
                if key != 'id':
                    if key != 'user_id':
                        if value != '-':
                            if key == 'first_name':
                                key = 'Vorname'
                            elif key == 'last_name':
                                key = 'Nachname'
                            elif key == 'phone':
                                key = 'Telefonnummer'
                            elif key == 'street':
                                key = 'Straße'
                            elif key == 'street_number':
                                key = 'Hausnummer'
                            elif key == 'city':
                                key = 'Stadt'
                            elif key == 'zip_code':
                                key = 'PLZ'
                            finder += key + ': ' + str(value) + '\n'
            finder = finder[:-2]
            cur.execute(
                "UPDATE bird_fallenbird SET finder = %s WHERE id = %s",
                (finder, row['id']))
