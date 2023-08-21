import pytest
import doctest
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


def test_from_strings():
    edits_list = EditsList.from_strings("kitten", "sitting")
    assert edits_list == EditsList(
        [
            Edit(op="substitute", old="k", new="s", index=0),
            Edit(op="substitute", old="e", new="i", index=4),
            Edit(op="insert", new="g", index=6),
        ]
    )


def test_from_strings_no_changes():
    edits_list = EditsList.from_strings("kitten", "kitten")
    assert edits_list == EditsList([])


def test_from_strings_insert_at_beginning():
    edits_list = EditsList.from_strings("kitten", "skitten")
    assert edits_list == EditsList(
        [
            Edit(op="insert", new="s", index=0),
        ]
    )


def test_from_strings_no_second_string():
    edits_list = EditsList.from_strings("kitten")
    assert edits_list == EditsList(
        [
            Edit(op="insert", new="k", index=0),
            Edit(op="insert", new="i", index=1),
            Edit(op="insert", new="t", index=2),
            Edit(op="insert", new="t", index=3),
            Edit(op="insert", new="e", index=4),
            Edit(op="insert", new="n", index=5),
        ]
    )


def test_from_strings_delete_at_end():
    edits_list = EditsList.from_strings("kitten", "kitte")
    assert edits_list == EditsList(
        [
            Edit(op="delete", old="n", index=5),
        ]
    )


def test_from_strings_substitute_entire_string():
    edits_list = EditsList.from_strings("kitten", "puppy")
    assert edits_list == EditsList(
        [
            Edit(op="substitute", old="k", new="p", index=0),
            Edit(op="substitute", old="i", new="u", index=1),
            Edit(op="substitute", old="t", new="p", index=2),
            Edit(op="substitute", old="t", new="p", index=3),
            Edit(op="substitute", old="e", new="y", index=4),
            Edit(op="delete", old="n", index=5),
        ]
    )


def test_from_strings_substitute_multiple_times():
    edits_list = EditsList.from_strings("kitten", "kippen")
    assert edits_list == EditsList(
        [
            Edit(op="substitute", old="t", new="p", index=2),
            Edit(op="substitute", old="t", new="p", index=3),
        ]
    )


def test_from_strings_delete_multiple_times():
    edits_list = EditsList.from_strings("kitten", "kien")
    assert edits_list == EditsList(
        [
            Edit(op="delete", old="t", index=2),
            Edit(
                op="delete", old="t", index=3
            ),  # BUG: should this be 2? Depends if the edit list expects "realtime" edits.
        ]
    )


def test_from_strings_insert_multiple_times():
    edits_list = EditsList.from_strings("kitten", "skitteng")
    assert edits_list == EditsList(
        [
            Edit(op="insert", new="s", index=0),
            Edit(op="insert", new="g", index=7),
        ]
    )


def test_from_strings_substitute_and_delete():
    edits_list = EditsList.from_strings("kitten", "kipte")
    assert edits_list == EditsList(
        [
            Edit(op="substitute", old="t", new="p", index=2),
            Edit(op="delete", old="n", index=5),
        ]
    )


def test_from_strings_delete_and_insert():
    edits_list = EditsList.from_strings("kitten", "kipten")
    assert edits_list == EditsList(
        [
            Edit(op="substitute", old="t", new="p", index=2),
        ]
    )
