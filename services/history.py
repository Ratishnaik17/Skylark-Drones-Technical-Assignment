from __future__ import annotations

from datetime import datetime
from typing import Dict, List
from uuid import uuid4


class ConversationHistory:
    """
    In-memory conversation history.

    Stores conversations using a session ID.
    """

    def __init__(self):
        self._history: Dict[str, List[dict]] = {}

    # --------------------------------------------------
    # Session Management
    # --------------------------------------------------

    def create_session(self) -> str:
        """
        Create a new chat session.

        Returns:
            session_id
        """

        session_id = str(uuid4())

        self._history[session_id] = []

        return session_id

    def session_exists(self, session_id: str) -> bool:
        return session_id in self._history

    # --------------------------------------------------
    # Messages
    # --------------------------------------------------

    def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
    ) -> None:
        """
        Add a user or assistant message.
        """

        if session_id not in self._history:
            self._history[session_id] = []

        self._history[session_id].append(
            {
                "role": role,
                "content": content,
                "timestamp": datetime.utcnow().isoformat(),
            }
        )

    def get_history(
        self,
        session_id: str,
    ) -> List[dict]:
        """
        Return conversation history.
        """

        return self._history.get(session_id, [])

    def clear_history(
        self,
        session_id: str,
    ) -> None:
        """
        Remove all messages from a session.
        """

        self._history.pop(session_id, None)

    def delete_session(
        self,
        session_id: str,
    ) -> None:
        """
        Delete the session completely.
        """

        self._history.pop(session_id, None)

    # --------------------------------------------------
    # Utilities
    # --------------------------------------------------

    def last_message(
        self,
        session_id: str,
    ) -> dict | None:
        """
        Return last message in conversation.
        """

        history = self.get_history(session_id)

        if history:
            return history[-1]

        return None

    def message_count(
        self,
        session_id: str,
    ) -> int:
        return len(self.get_history(session_id))

    def list_sessions(self) -> List[str]:
        """
        Return all active session IDs.
        """

        return list(self._history.keys())


history_service = ConversationHistory()