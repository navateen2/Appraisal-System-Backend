from sqlalchemy import event, inspect
from sqlalchemy.orm import Session
from middleware.context import get_current_user_id
from models.audit import Audit


def register_audit_listeners(session_factory):

    @event.listens_for(session_factory, "before_flush")
    def handle_updates_and_deletes(session: Session, flush_context, instances):
        user_id = get_current_user_id()

        # 1. Track updates and isolate exact field differentials
        for instance in session.dirty:
            if isinstance(instance, Audit):
                continue

            state = inspect(instance)
            changes = {}
            for attr in state.attrs:
                history = attr.history
                if history.has_changes():
                    # Format: {"field_name": [old_value, new_value]}
                    changes[attr.key] = [history.deleted[0] if history.deleted else None, attr.value]

            if changes:
                session.add(
                    Audit(
                        user_id=user_id,
                        action="UPDATE",
                        table_name=instance.__tablename__,
                        record_id=getattr(instance, "id"),
                        changed_fields=changes,
                    )
                )

        # 2. Track explicit hard deletions
        for instance in session.deleted:
            if isinstance(instance, Audit):
                continue
            session.add(
                Audit(
                    user_id=user_id,
                    action="DELETE",
                    table_name=instance.__tablename__,
                    record_id=getattr(instance, "id"),
                    changed_fields=None,
                )
            )

    @event.listens_for(session_factory, "after_flush")
    def handle_insertions(session: Session, flush_context):
        user_id = get_current_user_id()

        # 3. Track brand-new rows safely after the database populates row IDs
        for instance in session.new:
            if isinstance(instance, Audit):
                continue

            session.add(
                Audit(
                    user_id=user_id,
                    action="INSERT",
                    table_name=instance.__tablename__,
                    record_id=getattr(instance, "id"),
                    changed_fields=None,
                )
            )
