#import sqlalchemy as sa
from sqlalchemy import *

def get_jesus():
    return Table('jesus', metadata,
        Column('id', sa.Integer, primary_key = True),
        Column('num', sa.CHAR(8)),
        Column('title', sa.String(255)),
        Column('last_pos', sa.String(255), default="00:00:00"),
        Column('completed', sa.Boolean, default=False))
