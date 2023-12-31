import json
import logging
import math
import time
import unittest
from time import sleep, time

from src.crypto.paillier_abb import PaillierABB
from src.election.election_authority import ElectionAuthority
from src.election.single_vote.single_vote_election_system import \
    SingleVoteElection
from src.election.trustee.trustee import init_trustees
from src.protocols.sublinear import SubLinearProtocolSuite
from src.util.point_vote import PointVote
from src.util.logging import setup_logging

log = logging.getLogger(__name__)


class BasicElectionEncTest(unittest.TestCase):

    def setUp(self):
        setup_logging()
        abbs = PaillierABB.gen_trustee_abbs(256, 5, 3, SubLinearProtocolSuite)
        self.trustee_gen = lambda bulletin_board: init_trustees(bulletin_board, abbs, [i for i, _ in enumerate(abbs)])
        self.startTime = time()

    def tearDown(self):
        t = time() - self.startTime
        log.info("%s: %.3f" % (self.id(), t))

    def test_winner_election(self):
        e = self._init_election(4)
        e.add_generic_vote(PointVote([1, 0, 0, 0]), count=0)
        e.add_generic_vote(PointVote([0, 1, 0, 0]), count=1)
        e.add_generic_vote(PointVote([0, 0, 1, 0]), count=2)
        e.add_generic_vote(PointVote([0, 0, 0, 1]), count=3)
        result = e.trigger_evaluation()
        self.assertEqual(3, result[0])

    def test_winner_election_tie(self):
        e = self._init_election(4)
        e.add_generic_vote(PointVote([1, 0, 0, 0]), count=0)
        e.add_generic_vote(PointVote([0, 1, 0, 0]), count=3)
        e.add_generic_vote(PointVote([0, 0, 1, 0]), count=2)
        e.add_generic_vote(PointVote([0, 0, 0, 1]), count=3)
        result = e.trigger_evaluation()
        self.assertEqual(2, len(result))
        self.assertTrue(1 in result)
        self.assertTrue(3 in result)

    def _init_election(self, n_cand):
        return ElectionAuthority(self.trustee_gen, SingleVoteElection(n_cand), local_bulletin_board=True)
