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
        if self._actual_file.exists():
            if self.last_revision is None:
                rev = Revision(None, EditsList.from_file(self._actual_file))
            elif self.current_sha != self.last_revision.sha:
                rev = Revision(
                    self.current_sha,
                    EditsList.after(self._actual_file, self.last_revision.edits),
                )

            log.debug("Appending revision, %s", self.revisions)
            self._revisions.append(rev)

    def revert(self, sha: Optional[str] = None) -> "DeltaFile":
        """Revert to a revision"""
        # TODO: This and build_from_final_revision_file are very similar, maybe abstract out the common code.
        if sha is None:
            sha = self.last_revision.sha

        if sha is None:
            raise ValueError("No revisions to revert to")

        closest_sha = most_matching_sha(self.get_all_revision_shas(), sha)
        if closest_sha is None:
            raise ValueError("No revisions to revert to")
        sha = closest_sha

        # To load a revision, we need to load the prior revision file by getting the sha from the current revision file
        # then undo the edits from the prior revision file
        current = self.current_revision_file
        current = json.load(current.open("r"))
        if current is None:
            raise ValueError("No revisions to revert to")

        prior = self.get_revision_file(current["last_sha"])
        if prior is None:
            raise ValueError("No revisions to revert to")

        last_prior = None
        last_sha = current["last_sha"]
        while (
            prior is not None
            and prior.exists()
            and self.get_sha_from_revision_filename(prior) != sha
        ):
            last_prior = prior
            prior = json.load(prior.open("r"))
            last_sha = prior["last_sha"] if prior["last_sha"] is not None else last_sha
            prior = self.get_revision_file(last_sha)

        self = self.build_from_final_revision_file(self.get_revision_file(last_sha))

        with self._actual_file.open("w") as f:
            f.write(self.last_revision.edits.apply())

        return self

    def get_revision_file(self, sha: str, create: bool = False) -> Optional[Path]:
        """Get the revision file"""
        file = self._actual_file.parent.resolve() / ".pyt" / f"{sha}.json"
        if file.exists():
            return file
        elif create:
            file.touch()
            return file
        else:
            return None

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

    def save(self):
        """Update and dump the revisions"""
        self.update()
        self.dump_revision()

    @staticmethod
    def build_from_final_revision_file(rev_file: Path):
        """Load the revisions from a file"""
        obj = DeltaFile()
        rdict = json.load(rev_file.open("r"))
        obj._actual_file = Path(rdict["path"])

        rev_file = obj.get_revision_file(rdict["last_sha"])
        while rev_file is not None and rev_file.exists():
            rev_file = obj.get_revision_file(rdict["last_sha"])
            rev = Revision(
                rdict["revision"][0],
                EditsList(rdict["revision"][1]),
            )
            obj._revisions.append(rev)

            if rev_file is not None:
                rdict = json.load(rev_file.open("r"))
            else:
                break

        obj._original = rdict["current"]
        return obj

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
