import tab


def take(lst, n):
    return lst[0:n]

def bits(n):
    r"""
    return 0, 1 sequence which extend bytes of data
    >>> bits(0b00001000)
    [0, 0, 0, 0, 1, 0, 0, 0]
    >>> bits(8)
    """
    b = []
    while n:
        b = [n & 1] + b
        n >>= 1
    # add heading 0
    head = len(b) % 8
    if head != 0:
        b = [0] * (8 - head) + b
    return b


def insertTrie(trie, bs, v):
    if len(bs) == 0:
        return trie
    b = bs[0]
    if len(bs) == 1:
        if b in trie:
            print("force update")
        trie[b] = v
    else:
        d = trie[b] if b in trie else {}
        trie[b] = insertTrie(d, bs[1:], v)
    return trie


# for reverse parse VLC table, build Trie tree, then we could fast match bit
# stream to it.
def buildTrie(tbl):
    r"""
    input: dict {(len, binvalue): value}
    output: trie
    >>> buildTrie({(1, 0x80): 1, (8, 0x08): 13, (10, 0x05C0): 16})
    """
    trie = {}
    print(tbl)
    for (l, k), v in tbl.items():
        bs = take(bits(k), l)
        insertTrie(trie, bs, v)
    return trie

    
if __name__ == "__main__":
    import doctest
    doctest.testmod()
    print("test pass")

