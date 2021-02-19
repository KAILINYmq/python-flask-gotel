"""empty message

Revision ID: ed8fede3e8cc
Revises: 912f332fc005
Create Date: 2021-02-19 19:05:16.976787

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'ed8fede3e8cc'
down_revision = '912f332fc005'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('idea_details',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('idea_id', sa.Integer(), nullable=True),
    sa.Column('details_id', sa.Integer(), nullable=True),
    sa.Column('creat_time', sa.DateTime(), nullable=True),
    sa.Column('update_time', sa.DateTime(), nullable=True),
    sa.Column('is_delete', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['details_id'], ['details_table.id'], ),
    sa.ForeignKeyConstraint(['idea_id'], ['idea.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('learn_details',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('idea_id', sa.Integer(), nullable=True),
    sa.Column('details_id', sa.Integer(), nullable=True),
    sa.Column('creat_time', sa.DateTime(), nullable=True),
    sa.Column('update_time', sa.DateTime(), nullable=True),
    sa.Column('is_delete', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['details_id'], ['details_table.id'], ),
    sa.ForeignKeyConstraint(['idea_id'], ['learn.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_table('learn_name')
    op.drop_table('idea_name')
    op.drop_constraint('idea_type_type_id_fkey', 'idea_type', type_='foreignkey')
    op.create_foreign_key(None, 'idea_type', 'type_table', ['type_id'], ['id'])
    op.drop_constraint('learn_type_type_id_fkey', 'learn_type', type_='foreignkey')
    op.create_foreign_key(None, 'learn_type', 'type_table', ['type_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'learn_type', type_='foreignkey')
    op.create_foreign_key('learn_type_type_id_fkey', 'learn_type', 'details_table', ['type_id'], ['id'])
    op.drop_constraint(None, 'idea_type', type_='foreignkey')
    op.create_foreign_key('idea_type_type_id_fkey', 'idea_type', 'details_table', ['type_id'], ['id'])
    op.create_table('idea_name',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('idea_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('name_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('creat_time', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('update_time', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('is_delete', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['idea_id'], ['idea.id'], name='idea_name_idea_id_fkey'),
    sa.ForeignKeyConstraint(['name_id'], ['type_table.id'], name='idea_name_name_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='idea_name_pkey')
    )
    op.create_table('learn_name',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('idea_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('name_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('creat_time', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('update_time', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('is_delete', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['idea_id'], ['learn.id'], name='learn_name_idea_id_fkey'),
    sa.ForeignKeyConstraint(['name_id'], ['type_table.id'], name='learn_name_name_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='learn_name_pkey')
    )
    op.drop_table('learn_details')
    op.drop_table('idea_details')
    # ### end Alembic commands ###
