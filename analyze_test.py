import re
import pytest
from analyze import condorcet_winner, net_support_for_candidate1
from testcases import parse_testcases

testcases = parse_testcases("testcases.txt")


def run_testcase(party: str):
    if party == "condorcet_winner":
        return f"{condorcet_winner()}"
    else:
        candidate1, candidate2 = party.split(",")
        return f"{net_support_for_candidate1(candidate1, candidate2)}"


def _matches(expected: str, actual: str) -> bool:
    """True if `actual` matches `expected`; supports /regex/flags style expected values."""
    m = re.fullmatch(r"/(.*)/([a-z]*)", expected) # detect "/pattern/flags" form
    if m: # expected is a regex literal
        flags = re.IGNORECASE if "i" in m.group(2) else 0 # honour the "i" flag for case-insensitive matching
        return re.fullmatch(m.group(1), actual, flags) is not None # full-string regex match
    return expected == actual # otherwise fall back to plain equality


@pytest.mark.parametrize("testcase", testcases, ids=[testcase["name"] for testcase in testcases])
def test_cases(testcase):
    actual_output = run_testcase(testcase["input"]) # run the function corresponding to the testcase input
    assert _matches(testcase["output"], actual_output), \
        f"Expected {testcase['output']}, got {actual_output}" # compare with regex-aware matcher


def test_new_cases():
    # Antisymmetry: swapping the two arguments must negate the result.
    assert net_support_for_candidate1("יאיר לפיד", "בני גנץ") == -47 # mirror of Test 1 in testcases.txt
    assert net_support_for_candidate1("יולי אדלשטיין", "בנימין נתניהו") == -11 # mirror of Test 2
    assert net_support_for_candidate1("נפתלי בנט", "ניר ברקת") == 45 # mirror of Test 3

    # Comparing a candidate with themselves yields zero net support.
    assert net_support_for_candidate1("בנימין נתניהו", "בנימין נתניהו") == 0 # no one is preferred over themselves
    assert net_support_for_candidate1("נפתלי בנט", "נפתלי בנט") == 0 # idem for the Condorcet winner

    # בנט (the Condorcet winner) should beat every other candidate.
    for opponent in ["בנימין נתניהו", "יאיר לפיד", "בני גנץ", "גדעון סער",
                     "ניר ברקת", "יולי אדלשטיין"]:
        assert net_support_for_candidate1("נפתלי בנט", opponent) > 0 # positive net support vs each opponent

    # The Condorcet winner of this poll is נפתלי בנט.
    assert condorcet_winner() == "נפתלי בנט" # exact label as stored in codes_for_questions