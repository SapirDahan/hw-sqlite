import sqlite3

_DB_PATH = "poll.db"                                                          # poll.db sits next to this script


def _column_for(candidate: str) -> str:
    """Return the Q6_N column name that represents the given candidate label."""
    with sqlite3.connect(_DB_PATH) as con: # open a connection to poll.db
        row = con.execute( # look up the Q6_N variable whose Label matches the candidate's name
            "SELECT Variable FROM codes_for_questions "
            "WHERE Label = ? AND Variable LIKE 'Q6%'",
            (candidate,),
        ).fetchone() # take the single matching row
    return row[0] # return the column name (e.g. "Q6_3")


def net_support_for_candidate1(candidate1: str, candidate2: str) -> int:
    """Net pairwise support for candidate1 over candidate2 (from Q6 rankings).

    In Q6 each respondent ranked the candidates, a lower value means more preferred.
    The function returns: #(respondents who ranked candidate1 above candidate2)
                        - #(respondents who ranked candidate2 above candidate1).
    It can be negative when candidate2 is more popular.

    >>> net_support_for_candidate1("בני גנץ", "יאיר לפיד")
    47
    >>> net_support_for_candidate1("בנימין נתניהו", "יולי אדלשטיין")
    11
    >>> net_support_for_candidate1("ניר ברקת", "נפתלי בנט")
    -45
    """
    c1 = _column_for(candidate1) # resolve candidate1 to its Q6_N column
    c2 = _column_for(candidate2) # resolve candidate2 to its Q6_N column
    with sqlite3.connect(_DB_PATH) as con: # open a connection to poll.db
        net = con.execute( # +1 when c1 is preferred, -1 when c2 is preferred, 0 on ties/NULLs
            f"SELECT SUM(CASE WHEN {c1} < {c2} THEN 1 "
            f"              WHEN {c2} < {c1} THEN -1 ELSE 0 END) "
            f"FROM list_of_answers"
        ).fetchone()[0] # take the single aggregate value
    return net # return the net support (positive => candidate1 leads)


def condorcet_winner() -> str:
    """Return the Condorcet winner's name, or 'אין' if there is none.

    A Condorcet winner is a candidate who beats every other candidate in a head-to-head
    contest based on Q6 rankings. We delegate the pairwise comparison to
    net_support_for_candidate1 and require it to be strictly positive against everyone else.

    >>> condorcet_winner()
    'נפתלי בנט'
    """
    with sqlite3.connect(_DB_PATH) as con: # open a connection to poll.db
        names = [r[0] for r in con.execute( # fetch the labels of all 8 Q6 candidates
            "SELECT Label FROM codes_for_questions WHERE Variable LIKE 'Q6%'"
        )]
    for name in names: # try each candidate as a potential winner
        if all(net_support_for_candidate1(name, other) > 0 # reuse the previous function for the pairwise check
               for other in names if other != name): # against every one of the 7 opponents
            return name # found a candidate that beats everyone -> Condorcet winner
    return "אין" # nobody beat all 7 others -> no Condorcet winner


if __name__ == '__main__':
    import doctest
    print(doctest.testmod())

    # Use this code for testing via console input-output:
    # party = input()
    # if party == "condorcet_winner":
    #     print(condorcet_winner())
    # else:
    #     candidate1,candidate2 = party.split(",")
    #     print(net_support_for_candidate1(candidate1,candidate2))