"""empty message

Revision ID: 62770250c28f
Revises: None
Create Date: 2016-03-02 17:30:10.410299

"""

# revision identifiers, used by Alembic.
revision = '62770250c28f'
down_revision = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('site_settings',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('site_title', sa.String(), nullable=True),
    sa.Column('footer_line', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(), nullable=True),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('pw_hash', sa.Binary(), nullable=True),
    sa.Column('pw_salt', sa.Binary(), nullable=True),
    sa.Column('active', sa.Boolean(), nullable=True),
    sa.Column('create_date', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('post',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(), nullable=True),
    sa.Column('description', sa.String(), nullable=True),
    sa.Column('permalink', sa.String(), nullable=True),
    sa.Column('body', sa.Text(), nullable=True),
    sa.Column('create_date', sa.DateTime(), nullable=True),
    sa.Column('edit_date', sa.DateTime(), nullable=True),
    sa.Column('static_page', sa.Boolean(), nullable=True),
    sa.Column('static_page_in_timeline', sa.Boolean(), nullable=True),
    sa.Column('static_page_link_title', sa.String(), nullable=True),
    sa.Column('published', sa.Boolean(), nullable=True),
    sa.Column('comments_allowed', sa.Boolean(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('permalink'),
    sa.UniqueConstraint('title')
    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('post')
    op.drop_table('user')
    op.drop_table('site_settings')
    ### end Alembic commands ###
