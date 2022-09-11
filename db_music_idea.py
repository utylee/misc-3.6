import sqlalchemy as sa

meta = sa.MetaData()


tbl_idea = sa.Table('ideas', meta, 
            sa.Column('id', sa.Integer, primary_key=True), 
            sa.Column('type', sa.Integer),
            sa.Column('content_number', sa.Integer),
            sa.Column('content', sa.String(255)),
            sa.Column('description', sa.String(1024)))
