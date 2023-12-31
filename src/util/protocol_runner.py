import logging
from src.election.trustee.trustee_client import TrusteeClient
from src.election.trustee.trustee import Trustee
from time import sleep, time
from typing import List
import gmpy2 as gmpy

import numpy as np
from src.crypto.paillier_abb import PaillierCiphertext

log = logging.getLogger(__name__)


class ProtocolRunner():

    def __init__(self, trustees: List[Trustee], protocol_initializer):
        self.protocol_initializer = protocol_initializer
        self.trustees = trustees

    def run(self, *protocol_args):
        self.protocol_args = protocol_args
        for t in self.trustees:
            # HACK replace the trigger_evaluation() in the trustee with a properly received and deserialized
            # Protocol alongside its arguments.
            if isinstance(t, TrusteeClient):
                t.trigger_evaluation()
            else:
                p = self.protocol_initializer()
                t.run_protocol(p, *self.protocol_args)


        for t in self.trustees:
            while not t.is_protocol_finished():
                sleep(0.5)

        result = self.trustees[0].result
        for t in self.trustees:
            r = t.result
            try:
                if isinstance(result, (list, tuple, np.ndarray)):
                    if not np.array_equal(r, result):
                        log.warning('Inconsistent array result: r is ' + str(r) + " and result is " + str(result))
                        break
                elif isinstance(result, (PaillierCiphertext)):
                    if not r.val == result.val:
                        log.warning('Inconsistent result: r is ' + str(r) + " and result is " + str(result))
                        break
                else:
                    if not r == result:
                        log.warning('Inconsistent result: r is ' + str(r) + " and result is " + str(result))
                        break
            except AttributeError as identifier: # sometimes wrong compare method is used, don't know when
                log.warning("r is " + str(r) + " and result is " + str(result))
                raise
        return result, None
        # return result, self.trustees[0].get_protocol()

    def prepare_protocol(self, p):
        return
