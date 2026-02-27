"""
Repository Layer

Data access patterns for the application.

Team Convention: All repository methods return Optional[T] for single-item lookups.
Team Convention: All collections returned are List[T], never raw database cursors.
"""
