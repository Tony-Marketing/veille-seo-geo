"""Repository des invitations utilisateur."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models import UserInvitation
from backend.app.repositories.base import BaseRepository


class UserInvitationRepository(BaseRepository[UserInvitation]):
    """Acces aux invitations utilisateur."""

    search_fields = ("email",)

    def __init__(self, db: Session) -> None:
        super().__init__(db, UserInvitation)

    def get_by_token_hash(self, token_hash: str) -> UserInvitation | None:
        """Return an invitation matching a token hash."""

        return self.db.scalar(select(UserInvitation).where(UserInvitation.token_hash == token_hash))
