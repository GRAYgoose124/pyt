from dataclasses import dataclass
from pathlib import Path
from typing import Literal


@dataclass
class Edit:
    op: Literal["insert", "delete", "substitute"]
    index: int
    old: str = ""
    new: str = ""


class EditsList(list[Edit]):
    """A data structure to store the edits and apply them to a StringIO object."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def distance(self):
        return len(self)

    def apply(self, original: str, invert: bool = False):
        """
        >>> apply_leven_edits("kitten", [Edit(operation='substitute', old='k', new='s', index=0), Edit(operation='substitute', old='e', new='i', index=4), Edit(operation='insert', old='', new='g', index=7)])
        'sitting'
        """
        transformed = list(original)

        if invert:
            el = reversed(self)
        else:
            el = self

        for edit in el:
            if edit.op == "insert" and not invert or edit.op == "delete" and invert:
                transformed.insert(edit.index, edit.new)
            elif edit.op == "delete" and not invert or edit.op == "insert" and invert:
                transformed.pop(edit.index)
            elif edit.op == "substitute":
                if not invert:
                    transformed[edit.index] = edit.new
                else:
                    transformed[edit.index] = edit.old

        return "".join(transformed)

    @staticmethod
    def calculate_edits(s1: str, s2: str) -> list[Edit]:
        """Calculate the edits needed to transform s1 into s2 using the levenshtein distance algorithm.

        Args:
            s1 (str): The original string
            s2 (str): The new string

        Returns:
            list[Edit]: A list of edits needed to transform s1 into s2

        Examples:
            ```py
            >>> leven_edits("kitten", "sitting")
            [Edit(op='substitute', old='k', new='s', index=0), Edit(op='substitute', old='e', new='i', index=4), Edit(op='insert', old='', new='g', index=7)]
            ```
        """
        m, n = len(s1), len(s2)
        dp = [[(0, None, None, 0)] * (n + 1) for _ in range(m + 1)]

        for i in range(m + 1):
            for j in range(n + 1):
                if i == 0:
                    dp[i][j] = (j, None, "insert", j)
                elif j == 0:
                    dp[i][j] = (i, None, "delete", i)
                elif s1[i - 1] == s2[j - 1]:
                    dp[i][j] = (dp[i - 1][j - 1][0], None, "no_change", i - 1)
                else:
                    insert_cost = dp[i][j - 1][0] + 1
                    delete_cost = dp[i - 1][j][0] + 1
                    substitute_cost = dp[i - 1][j - 1][0] + 1

                    min_cost = min(insert_cost, delete_cost, substitute_cost)

                    if min_cost == insert_cost:
                        dp[i][j] = (min_cost, None, "insert", j)
                    elif min_cost == delete_cost:
                        dp[i][j] = (min_cost, None, "delete", i)
                    else:
                        dp[i][j] = (min_cost, s1[i - 1], "substitute", i - 1)

        edits = []
        i, j = m, n
        while i > 0 or j > 0:
            cost, replaced_char, operation, index = dp[i][j]
            if operation == "insert":
                edits.append(Edit(op="insert", index=index, new=s2[j - 1]))
                j -= 1
            elif operation == "delete":
                edits.append(Edit(op="delete", index=index, old=s1[i - 1]))
                i -= 1
            elif operation == "substitute":
                edits.append(
                    Edit(
                        op="substitute",
                        index=index,
                        old=replaced_char,
                        new=s2[j - 1],
                    )
                )
                i -= 1
                j -= 1
            else:
                i -= 1
                j -= 1

        return list(reversed(edits))
