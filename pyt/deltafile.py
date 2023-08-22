import hashlib
from io import StringIO
import json
from pathlib import Path
import shutil
import logging
from typing import NamedTuple, Optional

from .editslist import EditsList

log = logging.getLogger(__name__)


class Revision(NamedTuple):
    """A revision"""

    sha: Optional[str]
    edits: EditsList


def most_matching_sha(shas: list[str], sha: str):
    """Matches the most similar sha by number of matching leading characters.
    If less than 3 characters match for any sha, None is returned.

    Such as:
    >>> most_matching_sha(["abc123", "abc456", "abc789"], "abc456")
    "abc456"
    """
    matching = {}
    for s in shas:
        if s is None:
            continue
        matching[s] = 0
        for i in range(len(s)):
            if s[i] == sha[i]:
                matching[s] += 1
            else:
                break

    max_matching = max(matching.values())
    if max_matching < 3:
        return None

    for s, v in matching.items():
        if v == max_matching:
            return s


class DeltaFile:
    def __init__(self, path: Path = None):
        self._actual_file = path
        self._revisions: list[Revision] = []

        if path is not None:
            self.update()

    @property
    def actual_file(self):
        """Get the path"""
        return self._actual_file

    def update(self):
        """If the file has changed, create a new revision"""
        pass

    def revert(self, sha: Optional[str] = None) -> "DeltaFile":
        pass

    @staticmethod
    def get_sha_from_revision_filename(file: Path):
        """Get the sha from the revision filename"""
        return file.stem

    def get_last_revision_file(self):
        """Get the last revision file"""
        return self.get_revision_file(self.last_revision.sha)

    def get_all_revision_shas(self):
        """Get all the revision shas"""
        return [sha for sha, _ in self.revisions]

    @property
    def current_revision_file(self):
        """Get the next revision file"""
        return self.get_revision_file(self.current_sha, create=True)

    def dump_revision(self):
        """Dump the revisions to a file"""
        with self.current_revision_file.open("w") as f:
            rev = {
                "path": str(self._actual_file),
                "last_sha": self.revisions[-2].sha if len(self.revisions) > 1 else None,
                "current": self.actual_file.read_text(),
                "revision": self.revisions[-1],
            }

            log.debug("Dumping revision %s", rev)
            json.dump(
                rev,
                f,
            )

    def save(self):
        """Update and dump the revisions"""
        self.update()
        self.dump_revision()

    def revisions_to_str(self, sha: str):
        """Apply all revisions up to a certain sha"""

        built_str = self.revisions[0].edits.apply()
        for rev in self.revisions:
            if rev.sha == sha:
                break
            built_str = rev.edits.apply(built_str)

        return built_str

    def build(self):
        """Build the file"""
        return self.revisions_to_str(self.current_sha)

    @staticmethod
    def make_sha(path: Path):
        """Make a sha from a file"""
        with path.open("rb") as f:
            return hashlib.sha256(f.read()).hexdigest()

    @property
    def current_sha(self):
        """Get the current sha"""
        return self.make_sha(self._actual_file)

    @property
    def last_revision(self):
        """Get the last revision"""
        if len(self.revisions) == 0:
            log.debug("No revisions")
            return None

        return self.revisions[-1]

    @property
    def revisions(self):
        """Get the revisions"""
        return self._revisions

    def __repr__(self) -> str:
        return f"<DeltaFile {self._actual_file}>"


def main():
    try:
        import os

        logging.basicConfig(level=logging.DEBUG)

        os.makedirs("asdf/.pyt", exist_ok=True)
        os.chdir("asdf")

        with open("test.txt", "w") as f:
            f.write("Hello, World!")
        deltafile = DeltaFile(Path("test.txt"))
        deltafile.save()
        with open("test.txt", "w") as f:
            f.write("Hello, World! This is a test.")

        deltafile.save()
        print("\nBuild from final revision file:")
        print(
            DeltaFile.build_from_final_revision_file(
                deltafile.current_revision_file
            ).revisions
        )

        print("DeltaFile:", deltafile.build())

        print("\nRevert:")
        deltafile.revert(
            "46743c9057e56f3fa6fd91d1e34e1858ef95dbf962581b0f66143340de360291"
        )
    except KeyboardInterrupt:
        pass
    finally:
        os.chdir("..")
        shutil.rmtree("asdf")


if __name__ == "__main__":
    main()
