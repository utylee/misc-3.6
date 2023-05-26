import sqlalchemy as sa

meta = sa.MetaData()

#filename, title, playlist, status, timestamp

tbl_youtube_files = sa.Table('files', meta,
                        sa.Column('filename', sa.String(255)),
                        sa.Column('title', sa.String(255)),
                        sa.Column('playlist', sa.String(255)),
                        sa.Column('status', sa.String(255)),
                        sa.Column('timestamp', sa.String(255)))

tbl_youtube_uploading = sa.Table('uploading', meta, 
                        sa.Column('filename', sa.String(255)))
