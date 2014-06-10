import unittest
from collections import OrderedDict
import draw
import copy

class TestPowerPairedDraw(unittest.TestCase):
    """Basic unit test for core functionality of power-paired draws.
    Nowhere near comprehensive."""

    brackets = OrderedDict([
        (4, [1, 2, 3, 4, 5]),
        (3, [6, 7, 8, 9]),
        (2, [10, 11, 12, 13, 14]),
        (1, [15, 16])
    ])

    def setUp(self):
        self.b2 = copy.deepcopy(self.brackets)
        self.ppd = draw.PowerPairedDraw(None)

    def tearDown(self):
        self.b2 = None
        self.ppd = None

    def bracket(self, name, expected):
        self.ppd.options["odd_bracket"] = name
        self.ppd.resolve_odd_brackets(self.b2)
        self.assertEqual(self.b2, expected)

    def test_pullup_top(self):
        self.bracket("pullup_top", OrderedDict([
            (4, [1, 2, 3, 4, 5, 6]),
            (3, [7, 8, 9, 10]),
            (2, [11, 12, 13, 14]),
            (1, [15, 16])
        ]))

    def test_pullup_bottom(self):
        self.bracket("pullup_bottom", OrderedDict([
            (4, [1, 2, 3, 4, 5, 9]),
            (3, [6, 7, 8, 14]),
            (2, [10, 11, 12, 13]),
            (1, [15, 16])
        ]))

    def test_pullup_intermediate(self):
        self.bracket("intermediate", OrderedDict([
            (4, [1, 2, 3, 4]),
            (3.5, [5, 6]),
            (3, [7, 8]),
            (2.5, [9, 10]),
            (2, [11, 12, 13, 14]),
            (1, [15, 16])
        ]))

    def test_pullup_random(self):
        for j in range(5):
            b2 = self.b2
            self.ppd.options["odd_bracket"] = "pullup_random"
            self.ppd.resolve_odd_brackets(b2)
            self.assertTrue(all(i in b2[4] for i in [1, 2, 3, 4, 5]))
            self.assertEqual([i in b2[4] for i in [6, 7, 8, 9]].count(True), 1)
            self.assertEqual([i in b2[3] for i in [6, 7, 8, 9]].count(True), 3)
            self.assertEqual([i in b2[3] for i in [10, 11, 12, 13, 14]].count(True), 1)
            self.assertEqual([i in b2[2] for i in [10, 11, 12, 13, 14]].count(True), 4)
            self.assertEqual([15, 16], b2[1])

    def pairings(self, name, expected):
        ppd = self.ppd
        ppd.options["odd_bracket"] = "pullup_top"
        ppd.options["pairing_method"] = name
        ppd.resolve_odd_brackets(self.b2)
        pairings = ppd.generate_pairings(self.b2)
        result = tuple(p.teams for p in pairings)
        self.assertEqual(result, expected)

    def test_pairings_fold(self):
        self.pairings("fold", (
            (1, 6), (2, 5), (3, 4), (7, 10), (8, 9), (11, 14), (12, 13), (15, 16)
        ))

    def test_pairings_slide(self):
        self.pairings("slide", (
            (1, 4), (2, 5), (3, 6), (7, 9), (8, 10), (11, 13), (12, 14), (15, 16)
        ))


    def one_up_one_down(self, data, expected, **options):
        from one_up_one_down import Team
        for option, value in options.iteritems():
            self.ppd.options[option] = value
        pairings = []
        for ((p1, in1, hist1), (p2, in2, hist2)) in data:
            team1 = Team(p1, in1, hist1)
            team2 = Team(p2, in2, hist2)
            pairing = draw.Pairing([team1, team2], None, None)
            pairings.append(pairing)
        self.ppd.avoid_conflicts(pairings)
        self.assertEqual(len(expected), len(pairings))
        for (exp_teams, exp_flags), pair in zip(expected, pairings):
            self.assertEqual(tuple(t.id for t in pair.teams), exp_teams)
            self.assertEqual(pair.flags, exp_flags)

    @staticmethod
    def _1u1d_no_change(data):
        return [((id1, id2), []) for ((id1, inst1, hist1), (id2, inst2, hist2))
                in data]

    def test_no_swap(self):
        data = (((1, 'A', ()), (5, 'B', ())),
                ((2, 'C', ()), (6, 'A', ())),
                ((3, 'B', ()), (7, 'D', ())),
                ((4, 'C', ()), (8, 'A', ())))
        expected = self._1u1d_no_change(data)
        self.one_up_one_down(data, expected)

    def test_swap_institution(self):
        data = (((1, 'A', ()), (5, 'A', ())),
                ((2, 'C', ()), (6, 'B', ())),
                ((3, 'B', ()), (7, 'D', ())),
                ((4, 'C', ()), (8, 'A', ())))
        expected = [((1, 6), ["1u1d_institution"]),
                    ((2, 5), ["1u1d_other"]),
                    ((3, 7), []),
                    ((4, 8), [])]
        self.one_up_one_down(data, expected)

    def test_no_swap_institution(self):
        data = (((1, 'A', ()), (5, 'A', ())),
                ((2, 'C', ()), (6, 'B', ())),
                ((3, 'B', ()), (7, 'D', ())),
                ((4, 'C', ()), (8, 'A', ())))
        expected = self._1u1d_no_change(data)
        self.one_up_one_down(data, expected, avoid_institution=False)

    def test_swap_history(self):
        data = (((1, 'A', (5,)), (5, 'B', ())),
                ((2, 'C', ()), (6, 'A', ())),
                ((3, 'B', ()), (7, 'D', ())),
                ((4, 'C', ()), (8, 'A', ())))
        expected = [((1, 6), ["1u1d_history"]),
                    ((2, 5), ["1u1d_other"]),
                    ((3, 7), []),
                    ((4, 8), [])]
        self.one_up_one_down(data, expected)

    def test_no_swap_history(self):
        data = (((1, 'A', (5,)), (5, 'B', ())),
                ((2, 'C', ()), (6, 'A', ())),
                ((3, 'B', ()), (7, 'D', ())),
                ((4, 'C', ()), (8, 'A', ())))
        expected = self._1u1d_no_change(data)
        self.one_up_one_down(data, expected, avoid_history=False)

    def test_last_swap(self):
        data = (((1, 'A', ()), (5, 'B', ())),
                ((2, 'C', ()), (6, 'A', ())),
                ((3, 'B', ()), (7, 'D', ())),
                ((4, 'C', (8,)), (8, 'A', ())))
        expected = [((1, 5), []),
                    ((2, 6), []),
                    ((3, 8), ["1u1d_other"]),
                    ((4, 7), ["1u1d_history"])]
        self.one_up_one_down(data, expected)

if __name__ == '__main__':
    unittest.main()