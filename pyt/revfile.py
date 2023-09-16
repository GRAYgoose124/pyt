import hashlib
from io import StringIO
import json
from pathlib import Path
import shutil
import logging
from typing import NamedTuple, Optional

from .editslist import EditsList
from .utilities import most_matching_sha

log = logging.getLogger(__name__)


class Revision(NamedTuple):
    """A revision"""

    sha: Optional[str]
    edits: EditsList

    @property
    def asdict(self):
        return {"sha": self.sha, "edits": self.edits}
    
    def save(self, root: Path):
        """Save the revisions to a file"""
        payload = json.dumps(self.asdict, separators=(",", ":"))
        payload_sha = hashlib.sha256(payload.encode()).hexdigest()

        file = root / ".pyt" / payload_sha
        with file.open("w") as f:
            f.write(payload)

        return payload_sha
    
    @classmethod
    def load(cls, file: Path):
        """Load the revision from a file"""
        with file.open("r") as f:
            data = json.loads(f.read())

        return cls(**data)


class RevisionedFile:
    def __init__(self, path: Path):
        self._actual_file = path
        self._revisions_file = Path(".pyt") / path.name

    def update(self):
        """If the watched file has changed, create a new revision"""
        pass

    def revert(self, sha: Optional[str] = None) -> "RevisionedFile":
        """Revert the file to a particular revision"""
        pass

    def get_revision_file(self, root: Path, sha: str, create: bool = False):
        """Get the revision file for a sha"""
        file = root / ".pyt" / sha
        if not file.exists():
            if create:
                file.touch()
            else:
                return None
            
        
        return file
    
    def save_revision(self):
        """Saves the current file as a new revision"""
