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
