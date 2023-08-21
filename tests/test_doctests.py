import pytest
import doctest
import pyt.utils
import pyt.deltafile


from pyt.editslist import Edit, EditsList


def test_apply_edits():
    original = "kitten"
    edits = [
        Edit(op="substitute", old="k", new="s", index=0),
        Edit(op="substitute", old="e", new="i", index=4),
        Edit(op="insert", new="g", index=7),
    ]
    edits_list = EditsList(edits)
    transformed = edits_list.apply(original)
    assert transformed == "sitting"


def test_apply_edits_no_changes():
    original = "kitten"
    edits = []
    edits_list = EditsList(edits)
    transformed = edits_list.apply(original)
    assert transformed == "kitten"


def test_apply_edits_insert_at_beginning():
    original = "kitten"
    edits = [
        Edit(op="insert", new="s", index=0),
    ]
    edits_list = EditsList(edits)
    transformed = edits_list.apply(original)
    assert transformed == "skitten"


def test_apply_edits_delete_at_end():
    original = "kitten"
    edits = [
        Edit(op="delete", old="n", index=5),
    ]
    edits_list = EditsList(edits)
    transformed = edits_list.apply(original)
    assert transformed == "kitte"


def test_apply_edits_substitute_entire_string():
    original = "kitten"
    edits = [
        Edit(op="substitute", old="k", new="p", index=0),
        Edit(op="substitute", old="i", new="u", index=1),
        Edit(op="substitute", old="t", new="p", index=2),
        Edit(op="substitute", old="t", new="p", index=3),
        Edit(op="substitute", old="e", new="y", index=4),
        Edit(op="substitute", old="n", index=5),
    ]
    edits_list = EditsList(edits)
    transformed = edits_list.apply(original)
    assert transformed == "puppy"


def test_apply_edits_substitute_multiple_times():
    original = "kitten"
    edits = [
        Edit(op="substitute", old="t", new="p", index=2),
        Edit(op="substitute", old="t", new="p", index=3),
    ]
    edits_list = EditsList(edits)
    transformed = edits_list.apply(original)
    assert transformed == "kippen"


def test_apply_edits_delete_multiple_times():
    original = "kitten"
    edits = [
        Edit(op="delete", old="t", index=2),
        Edit(op="delete", old="t", index=2),
    ]
    edits_list = EditsList(edits)
    transformed = edits_list.apply(original)
    assert transformed == "kien"


def test_apply_edits_insert_multiple_times():
    original = "kitten"
    edits = [
        Edit(op="insert", new="s", index=0),
        Edit(op="insert", new="g", index=7),
    ]
    edits_list = EditsList(edits)
    transformed = edits_list.apply(original)
    assert transformed == "skitteng"


def test_apply_edits_substitute_and_delete():
    original = "kitten"
    edits = [
        Edit(op="substitute", old="t", new="p", index=2),
        Edit(op="delete", old="n", index=5),
    ]
    edits_list = EditsList(edits)
    transformed = edits_list.apply(original)
    assert transformed == "kipte"


def test_apply_edits_delete_and_insert():
    original = "kitten"
    edits = [
        Edit(op="delete", old="t", index=2),
        Edit(op="insert", new="p", index=2),
    ]
    edits_list = EditsList(edits)
    transformed = edits_list.apply(original)
    assert transformed == "kipten"


def test_undo_edits():
    original = "sitting"
    edits = [
        Edit(op="substitute", old="k", new="s", index=0),
        Edit(op="substitute", old="e", new="i", index=4),
        Edit(op="insert", new="g", index=6),
    ]
    edits_list = EditsList(edits)
    transformed = edits_list.apply(original, invert=True)
    assert transformed == "kitten"


def test_apply_then_undo_edits():
    original = "kitten"
    edits = [
        Edit(op="substitute", old="k", new="s", index=0),
        Edit(op="substitute", old="e", new="i", index=4),
        Edit(op="insert", new="g", index=6),
    ]
    edits_list = EditsList(edits)
    transformed = edits_list.apply(original)
    assert transformed == "sitting"
    transformed = edits_list.apply(transformed, invert=True)
    assert transformed == "kitten"
