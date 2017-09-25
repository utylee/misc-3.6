import sqlalchemy as sa

metadata = sa.MetaData()
jesus = sa.Table('jesus', metadata,
        sa.Column('id', sa.Integer, primary_key = True),
        sa.Column('num', sa.CHAR(8)),
        sa.Column('title', sa.String(255)),
        sa.Column('last_pos', sa.String(255), default="00:00:00"),
        sa.Column('completed', sa.Boolean, default=False))
