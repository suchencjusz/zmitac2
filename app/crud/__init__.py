def commit_or_flush(db, obj, commit=True):
    """
    Helper function to commit or flush database session.
    
    Args:
        db: SQLAlchemy session
        obj: Database object to refresh (optional)
        commit: If True, commits; if False, flushes
    """
    if commit:
        db.commit()
        if obj and hasattr(obj, '__tablename__'):
            db.refresh(obj)
    else:
        db.flush()