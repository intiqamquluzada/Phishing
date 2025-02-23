"""Add company_id to user table

Revision ID: ee43560fd013
Revises: db77465bda32
Create Date: 2024-11-19 15:06:20.037671

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ee43560fd013'
down_revision: Union[str, None] = 'db77465bda32'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('ix_Training_id', table_name='Training')
    op.drop_table('Training')
    op.drop_index('ix_campaign_id', table_name='campaign')
    op.drop_table('campaign')
    op.drop_index('ix_administration_id', table_name='administration')
    op.drop_table('administration')
    op.drop_index('ix_role_id', table_name='role')
    op.drop_table('role')
    op.drop_index('ix_user_email', table_name='user')
    op.drop_index('ix_user_id', table_name='user')
    op.drop_table('user')
    op.drop_index('ix_Question_id', table_name='Question')
    op.drop_table('Question')
    op.drop_index('ix_target_user_email', table_name='target_user')
    op.drop_index('ix_target_user_id', table_name='target_user')
    op.drop_table('target_user')
    op.drop_index('ix_invite_id', table_name='invite')
    op.drop_table('invite')
    op.drop_index('ix_company_id', table_name='company')
    op.drop_table('company')
    op.drop_index('ix_target_id', table_name='target')
    op.drop_table('target')
    op.drop_index('ix_email_read_event_id', table_name='email_read_event')
    op.drop_index('ix_email_read_event_uuid', table_name='email_read_event')
    op.drop_table('email_read_event')
    op.drop_index('ix_email_template_id', table_name='email_template')
    op.drop_table('email_template')
    op.drop_index('ix_TrainingInformation_id', table_name='TrainingInformation')
    op.drop_table('TrainingInformation')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('TrainingInformation',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('question_count', sa.INTEGER(), nullable=True),
    sa.Column('pages_count', sa.INTEGER(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_TrainingInformation_id', 'TrainingInformation', ['id'], unique=False)
    op.create_table('email_template',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('name', sa.VARCHAR(), nullable=False),
    sa.Column('description', sa.VARCHAR(), nullable=True),
    sa.Column('difficulty', sa.VARCHAR(), nullable=False),
    sa.Column('subject', sa.VARCHAR(), nullable=True),
    sa.Column('body', sa.VARCHAR(), nullable=True),
    sa.Column('file_path', sa.VARCHAR(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_email_template_id', 'email_template', ['id'], unique=False)
    op.create_table('email_read_event',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('template_id', sa.INTEGER(), nullable=True),
    sa.Column('uuid', sa.VARCHAR(), nullable=True),
    sa.ForeignKeyConstraint(['template_id'], ['email_template.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_email_read_event_uuid', 'email_read_event', ['uuid'], unique=1)
    op.create_index('ix_email_read_event_id', 'email_read_event', ['id'], unique=False)
    op.create_table('target',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('name', sa.VARCHAR(), nullable=True),
    sa.Column('target_user_id', sa.INTEGER(), nullable=True),
    sa.ForeignKeyConstraint(['target_user_id'], ['target_user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_target_id', 'target', ['id'], unique=False)
    op.create_table('company',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('name', sa.VARCHAR(), nullable=False),
    sa.Column('address', sa.VARCHAR(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_company_id', 'company', ['id'], unique=False)
    op.create_table('invite',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('user_id', sa.INTEGER(), nullable=True),
    sa.Column('verification_code', sa.VARCHAR(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_invite_id', 'invite', ['id'], unique=False)
    op.create_table('target_user',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('first_name', sa.VARCHAR(), nullable=False),
    sa.Column('last_name', sa.VARCHAR(), nullable=False),
    sa.Column('email', sa.VARCHAR(), nullable=False),
    sa.Column('job_title', sa.VARCHAR(), nullable=True),
    sa.Column('company_id', sa.INTEGER(), nullable=True),
    sa.ForeignKeyConstraint(['company_id'], ['company.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_target_user_id', 'target_user', ['id'], unique=False)
    op.create_index('ix_target_user_email', 'target_user', ['email'], unique=1)
    op.create_table('Question',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('question', sa.VARCHAR(), nullable=True),
    sa.Column('training_information_id', sa.INTEGER(), nullable=True),
    sa.ForeignKeyConstraint(['training_information_id'], ['TrainingInformation.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_Question_id', 'Question', ['id'], unique=False)
    op.create_table('user',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('email', sa.VARCHAR(), nullable=True),
    sa.Column('hashed_password', sa.VARCHAR(), nullable=True),
    sa.Column('verification_code', sa.VARCHAR(), nullable=True),
    sa.Column('mfa_enabled', sa.BOOLEAN(), nullable=True),
    sa.Column('mfa_secret', sa.VARCHAR(), nullable=True),
    sa.Column('mfa_backup_codes', sa.VARCHAR(), nullable=True),
    sa.Column('role_id', sa.INTEGER(), nullable=True),
    sa.ForeignKeyConstraint(['role_id'], ['role.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_user_id', 'user', ['id'], unique=False)
    op.create_index('ix_user_email', 'user', ['email'], unique=1)
    op.create_table('role',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('name', sa.VARCHAR(), nullable=True),
    sa.Column('description', sa.VARCHAR(), nullable=True),
    sa.Column('permission', sa.VARCHAR(), nullable=True),
    sa.Column('created_at', sa.DATETIME(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_role_id', 'role', ['id'], unique=False)
    op.create_table('administration',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('name', sa.VARCHAR(), nullable=True),
    sa.Column('status', sa.VARCHAR(), nullable=True),
    sa.Column('is_active', sa.BOOLEAN(), nullable=True),
    sa.Column('user_id', sa.INTEGER(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_administration_id', 'administration', ['id'], unique=False)
    op.create_table('campaign',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('name', sa.VARCHAR(), nullable=False),
    sa.Column('delivery_status', sa.VARCHAR(length=6), nullable=True),
    sa.Column('scheduled_date', sa.DATE(), nullable=False),
    sa.Column('scheduled_time', sa.TIME(), nullable=False),
    sa.Column('company_id', sa.INTEGER(), nullable=False),
    sa.ForeignKeyConstraint(['company_id'], ['company.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_campaign_id', 'campaign', ['id'], unique=False)
    op.create_table('Training',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('module_name', sa.VARCHAR(), nullable=True),
    sa.Column('passing_score', sa.INTEGER(), nullable=True),
    sa.Column('training_information', sa.INTEGER(), nullable=True),
    sa.Column('presentation', sa.VARCHAR(), nullable=True),
    sa.Column('preview', sa.VARCHAR(), nullable=True),
    sa.ForeignKeyConstraint(['training_information'], ['TrainingInformation.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_Training_id', 'Training', ['id'], unique=False)
    # ### end Alembic commands ###
