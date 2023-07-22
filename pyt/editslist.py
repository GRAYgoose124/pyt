from io import FileIO, StringIO
from pathlib import Path
from typing import Iterable, NamedTuple

from .utils import leven_edits, Edit


class EditsList(list[Edit]):
    """A data structure to store the edits and apply them to a StringIO object."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._original: str = None

    @property
    def original(self):
        return self._original

    @staticmethod
    def from_file(file: FileIO):
        """Create an EditsList from a file"""
        edits = EditsList()
        edits._original = ""
        edits.update(file)

        return edits

    @staticmethod
    def after(new_file: Path, edits: "EditsList"):
        """Create an EditsList from a string"""
        obj = EditsList()
        obj._original = edits.apply()
        obj._path = new_file
        obj.update(new_file)

        return obj

    def update(self, path: Path):
        """Update the edits list"""
        with open(path, "r") as file:
            new_file = file.read()

        self.get_edits(self.original, new_file)

    def get_edits(self, s1, s2):
        self.clear()
        self.extend(leven_edits(s1, s2))

    def apply(self):
        """
        >>> apply_leven_edits("kitten", [Edit(operation='substitute', old='k', new='s', index=0), Edit(operation='substitute', old='e', new='i', index=4), Edit(operation='insert', old='', new='g', index=7)])
        'sitting'
        """
        transformed = list(self.original)
        for edit in reversed(self):
            if edit.op == "insert":
                transformed.insert(edit.index, edit.new)
            elif edit.op == "delete":
                transformed.pop(edit.index)
            elif edit.op == "substitute":
                transformed[edit.index] = edit.new
        return "".join(transformed)

    def undo(self):
        """
        >>> undo_leven_edits("sitting", [Edit(operation='substitute', old='k', new='s', index=0), Edit(operation='substitute', old='e', new='i', index=4), Edit(operation='insert', old='', new='g', index=7)])
        'kitten'
        """
        transformed = list(self.original)
        for edit in reversed(self):
            if edit.op == "insert":
                transformed.pop(edit.index - 1)
            elif edit.op == "delete":
                transformed.insert(edit.index, edit.old)
            elif edit.op == "substitute":
                transformed[edit.index] = edit.old
        return "".join(transformed)
