from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import shutil
import logging
from typing import Optional
from pathlib import Path

from .editslist import EditsList
from .utilities import most_matching_sha

log = logging.getLogger(__name__)


@dataclass
class Revision:
    """A revision"""

    sha: int
    previous_sha: Optional[int]
    edits: EditsList
    path: Path

    @property
    def asdict(self):
        return {
            "sha": self.sha,
            "edits": str(self.edits.pickle()),
            "previous_sha": self.previous_sha,
            "path": str(self.path),
        }

    @classmethod
    def load(cls, file: Path):
        """Load the revision from a file"""
        with file.open("r") as f:
            data = json.loads(f.read())

        data["path"] = Path(data["path"])
        data["edits"] = EditsList.unpickle(data["edits"])

        return cls(**data)

    def save(self, root: Path = Path(".")):
        """Save the revisions to a file"""
        payload = json.dumps(self.asdict, separators=(",", ":"))

        with (root / self.sha).open("w") as f:
            f.write(payload)

    def new(self, root: Path = Path(".")):
        """Create a new revision"""
        this_revision = root / self.sha

        if not this_revision.exists():
            raise FileNotFoundError(
                f"Cant find revision {self.sha:.8} to apply edits to."
            )

        return Revision.from_filename(self.path, self)

    @classmethod
    def from_filename(cls, file: Path, previous_revision: Optional["Revision"] = None):
        """Create a revision from a filename"""
        if not file.exists():
            raise FileNotFoundError(f"File {file} does not exist")

        with file.open("r") as f:
            original = f.read()

        sha = hashlib.sha256(original.encode()).hexdigest()

        if previous_revision:
            return cls(
                sha,
                previous_revision.sha,
                EditsList.from_strings(
                    previous_revision.edits.apply(original, invert=True), original
                ),
                file,
            )
        else:
            return cls(sha, None, EditsList.from_strings("", original), file)


def main():
    root = Path(".") / ".pyt"
    if root.exists():
        shutil.rmtree(root)
    root.mkdir()

    test_file = Path("test.txt")
    test_file.write_text("Hello, World!")

    revision = Revision.from_filename(test_file)
    revision.save(root)

    test_file.write_text("Hello, World! This is a test")
    revision2 = revision.new(root)
    revision2.save(root)


if __name__ == "__main__":
    main()
