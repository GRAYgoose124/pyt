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

    def __post_init__(self):
        self._root = None

    @property
    def asdict(self):
        return {
            "sha": self.sha,
            "edits": self.edits.pickle(),
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
        self._root = root
        payload = json.dumps(self.asdict, separators=(",", ":"))

        with (root / self.sha).open("w") as f:
            f.write(payload)

    def new(self):
        """Create a new revision"""

        if not (self._root / self.sha).exists():
            raise FileNotFoundError(
                f"Cant find revision {self.sha:.8} to apply edits to."
            )

        return Revision.from_filename(self.path, self)

    def revert(self, reversion: Optional["Revision"] = None):
        """Revert to the previous revision"""
        original = ""
        revisions = []
        first_revision = reversion or self
        while first_revision.previous_sha:
            first_revision = Revision.load(
                first_revision._root / first_revision.previous_sha
            )
            revisions.append(first_revision)

        while revisions:
            rev = revisions.pop()
            original = rev.edits.apply(original)

        return original

    @classmethod
    def from_filename(
        cls,
        file: Path,
        previous_revision: Optional["Revision"] = None,
        root: Optional[Path] = None,
    ):
        """Create a revision from a filename"""
        if not file.exists():
            raise FileNotFoundError(f"File {file} does not exist")

        with file.open("r") as f:
            actual = f.read()

        sha = hashlib.sha256(actual.encode()).hexdigest()

        # see if the file has been modified
        if previous_revision and sha == previous_revision.sha:
            return previous_revision

        if previous_revision:
            original = previous_revision.revert()
            obj = cls(
                sha,
                previous_revision.sha,
                EditsList.from_strings(original, actual),
                file,
            )
            obj._root = root or previous_revision._root
            return obj
        else:
            obj = cls(sha, None, EditsList.from_strings("", actual), file)
            obj._root = root or Path(".")
            return obj


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
    revision2 = revision.new()
    revision2.save(root)

    print(test_file.read_text())
    # undo revision2
    revision3 = revision2.new()
    revision3.save(root)
    test_file.write_text(revision3.revert())
    print(test_file.read_text())


if __name__ == "__main__":
    main()
