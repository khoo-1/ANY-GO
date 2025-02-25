"""初始化数据库表

Revision ID: initial_migration
Revises: 
Create Date: 2023-11-20

"""
from alembic import op
import sqlalchemy as sa
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 检查数据库类型
database_url = os.getenv("DATABASE_URL", "sqlite:///./app.db")
is_sqlite = database_url.startswith("sqlite")

# revision identifiers, used by Alembic.
revision = 'initial_migration'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 创建用户表
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('full_name', sa.String(), nullable=True),
        sa.Column('role', sa.String(), nullable=True),
        sa.Column('permissions', sa.JSON().with_variant(sa.String(), "sqlite"), nullable=True),
        sa.Column('disabled', sa.Boolean(), default=False),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), default=sa.func.now(), onupdate=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('username'),
        sa.UniqueConstraint('email')
    )
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=False)
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=False)

    # 创建产品表
    op.create_table(
        'products',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('sku', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('price', sa.Float(), nullable=False),
        sa.Column('cost', sa.Float(), nullable=False),
        sa.Column('weight', sa.Float(), nullable=True),
        sa.Column('stock', sa.Integer(), default=0),
        sa.Column('category', sa.String(), nullable=True),
        sa.Column('supplier', sa.String(), nullable=True),
        sa.Column('tags', sa.JSON().with_variant(sa.String(), "sqlite"), default=list),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), default=sa.func.now(), onupdate=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('sku')
    )
    op.create_index(op.f('ix_products_id'), 'products', ['id'], unique=False)
    op.create_index(op.f('ix_products_name'), 'products', ['name'], unique=False)
    op.create_index(op.f('ix_products_sku'), 'products', ['sku'], unique=False)

    # 创建装箱单表
    op.create_table(
        'packing_lists',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', sa.String(), default='draft'),
        sa.Column('created_by', sa.Integer(), sa.ForeignKey('users.id')),
        sa.Column('assigned_to', sa.Integer(), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), default=sa.func.now(), onupdate=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id']),
        sa.ForeignKeyConstraint(['assigned_to'], ['users.id'])
    )
    op.create_index(op.f('ix_packing_lists_id'), 'packing_lists', ['id'], unique=False)
    op.create_index(op.f('ix_packing_lists_name'), 'packing_lists', ['name'], unique=False)

    # 创建装箱单明细表
    op.create_table(
        'packing_list_items',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('packing_list_id', sa.Integer(), sa.ForeignKey('packing_lists.id')),
        sa.Column('product_id', sa.Integer(), sa.ForeignKey('products.id')),
        sa.Column('quantity', sa.Integer(), default=1),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('is_packed', sa.Boolean(), default=False),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), default=sa.func.now(), onupdate=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['packing_list_id'], ['packing_lists.id']),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'])
    )
    op.create_index(op.f('ix_packing_list_items_id'), 'packing_list_items', ['id'], unique=False)


def downgrade() -> None:
    # 删除表
    op.drop_table('packing_list_items')
    op.drop_table('packing_lists')
    op.drop_table('products')
    op.drop_table('users') 