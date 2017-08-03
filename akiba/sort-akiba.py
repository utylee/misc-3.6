from peewee import *
from playhouse.apsw_ext import *

db = APSWDatabase('akiba.db', timeout=300000)

with db.atomic():
    try:
        print('.dropping table...')
        cur = db.execute_sql('drop table sorted;')
    except:
        print('!! exception while drop table')


with db.atomic():
    try:
        print('.creating sorted table...')
        cur = db.execute_sql('create table sorted as select * from akiba order by date desc;')
    except:
        print('!! exception while creating table')
#cur = db.execute_sql('vacuum;')
    #cur = db.execute_sql('select * from akiba')

#for i in cur.fetchall():
    #print(i)
