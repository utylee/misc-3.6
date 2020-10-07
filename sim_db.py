import sqlalchemy as sa

metadata = sa.MetaData()

tbl_spells = sa.Table('spells', metadata,
                sa.Column('spell_name', sa.String(255)),
                sa.Column('spell_id', sa.String(255), primary_key = True),
                sa.Column('kor', sa.String(255)))


