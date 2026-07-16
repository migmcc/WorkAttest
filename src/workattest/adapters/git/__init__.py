"""Git adapter — observe a real repository as an authorized evidence source."""

from .adapter import GitAdapter, GitError, GitSnapshot

__all__ = ["GitAdapter", "GitError", "GitSnapshot"]
