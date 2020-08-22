from caspy.helpers.helpers import group_list_into_all_poss_pairs


def test_groupings():
    tot = []
    for z in group_list_into_all_poss_pairs([1,2,3]):
        tot.append(z)

    assert tot == 0
