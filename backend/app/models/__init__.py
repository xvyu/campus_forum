"""Models package - re-exports all SQLAlchemy models for IDE-friendly imports.

Why this exists:
- 让 `from app.models import Post, Comment, Board, PostDeleteSnapshot` 这种写法可用
- 同时保留 `from app.models.post import Post` 的细粒度写法
- 解决 Pylance / Pyright 等 IDE 在空 __init__.py 下误报"未导入"的问题
"""
from app.models.user import User
from app.models.post import Board, Post, Comment, PostDeleteSnapshot

__all__ = ["User", "Board", "Post", "Comment", "PostDeleteSnapshot"]