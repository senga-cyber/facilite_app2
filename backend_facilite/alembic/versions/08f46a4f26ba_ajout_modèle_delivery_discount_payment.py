"""Ajout modèle Delivery + champ discount dans Payment"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# Identifiants de migration
revision = '08f46a4f26ba'
down_revision = 'e37e6edd6554'
branch_labels = None
depends_on = None


def upgrade() -> None:
    
    # Nouvelle table deliveries
    op.create_table(
        'deliveries',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('order_id', sa.Integer(), sa.ForeignKey('orders.id', ondelete="CASCADE"), nullable=False),
        sa.Column('delivery_person_id', sa.Integer(), sa.ForeignKey('users.id', ondelete="CASCADE"), nullable=False),
        sa.Column('latitude', sa.Float(), nullable=True),
        sa.Column('longitude', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False)
    )

    # Ajout colonne discount dans payments
    op.add_column('payments', sa.Column('discount', sa.Float(), nullable=False, server_default="0.0"))


def downgrade() -> None:
    # Retirer colonne discount
    op.drop_column('payments', 'discount')

    # Supprimer table deliveries
    op.drop_table('deliveries')

    # Supprimer l'ENUM
    delivery_status_enum = postgresql.ENUM(
        'pending', 'accepted', 'in_progress', 'delivered', 'cancelled',
        name='deliverystatusenum'
    )
    delivery_status_enum.drop(op.get_bind(), checkfirst=True)
