import unittest
from analyze import generate_tickets, summarize


class TicketTests(unittest.TestCase):
    def test_boundary_pending_and_response_after_cutoff(self):
        rows = [
            (1, '2024-01-01 09:00:00', 'high', 60, '2024-01-01 10:00:00'),
            (2, '2024-01-01 09:00:00', 'high', 60, '2024-01-01 10:01:00'),
            (3, '2024-01-01 11:30:00', 'high', 60, '2024-01-01 12:30:00'),
            (4, '2024-01-01 10:00:00', 'high', 60, None),
            (5, '2024-01-01 13:00:00', 'high', 60, None),
        ]
        columns, result = summarize(rows, '2024-01-01 12:00:00')
        self.assertEqual(dict(zip(columns, result[0])), {'priority': 'high', 'tickets': 4, 'met': 1, 'breached': 2, 'pending': 1, 'sla_met_pct_decided': 33.33})

    def test_no_decided_tickets_has_null_rate(self):
        _, result = summarize([(1, '2024-01-01 11:30:00', 'normal', 240, None)], '2024-01-01 12:00:00')
        self.assertIsNone(result[0][-1])

    def test_generation_is_reproducible(self):
        self.assertEqual(generate_tickets(), generate_tickets())
        self.assertEqual(len(generate_tickets()), 600)

    def test_invalid_timestamps_and_targets_are_rejected(self):
        invalid = [
            (1, '2024-01-01 09:00:00', 'high', 60, '2024-01-01 08:59:59'),
            (1, '2024-02-30 09:00:00', 'high', 60, None),
            (1, '2024-01-01 09:00:00', 'high', 0, None),
            (1, '2024-01-01 09:00:00', 'high', 1.5, None),
            (1, '2024-01-01 09:00:00', 'urgent', 60, None),
        ]
        for row in invalid:
            with self.subTest(row=row), self.assertRaises(ValueError):
                summarize([row])
        with self.assertRaises(ValueError):
            summarize([], 'invalid')


if __name__ == '__main__':
    unittest.main()
