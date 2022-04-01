
import random
from pathlib import Path
from typing import Dict, List, Tuple, Optional

from .coverage import BITMAP_SIZE, CoverageBitmap, get_bitmap


class Scheduler():
    def set_initial_inputs(self):
        """Call once finished importing initial inputs, which may be special"""
        raise NotImplementedError()

    def pick_next_input(self) -> Tuple[Path, int]:
        """Select next input to fuzz (intelligently)"""
        raise NotImplementedError()

    def is_result_new(self, result) -> bool:
        """Return if result is new; don't update coverage"""
        raise NotImplementedError()

    def check_and_update_coverage(self, result) -> bool:
        """Return if result is new PLUS update coverage"""
        raise NotImplementedError()

    def add_new_input(self, cur_input: Path, cur_coverage: CoverageBitmap, parent_input: Path) -> Optional[str]:
        """Add new input based with coverage"""
        raise NotImplementedError()


class RoundRobinScheduler(Scheduler):
    """A "fair" scheduler using the AFL-style coverage bitmap"""

    def __init__(self):
        self.inputs: List[Path] = []
        self.queue: List[Path] = []
        self.initialization_finished = False
        # Inverted to simplify checks for new bits
        self.overall_coverage = bytearray(b'\xFF' * BITMAP_SIZE)

    def set_initial_inputs(self):
        self.initialization_finished = True

    def pick_next_input(self) -> Tuple[Path, int]:
        """Select next input to fuzz (intelligently)"""
        num_mutations = 256
        if len(self.queue) == 0:
            self.queue = self.inputs.copy()
            random.shuffle(self.queue)
        next_input = self.queue.pop()
        #print(f'  DBG: Next input: {next_input}')
        return next_input, num_mutations

    def is_result_new(self, cur_coverage: CoverageBitmap) -> bool:
        """New coverage includes new bits, does NOT update overall coverage"""
        is_new = False
        cur_bitmap = cur_coverage.bitmap
        for i in range(BITMAP_SIZE):
            new_bits = cur_bitmap[i] & self.overall_coverage[i]
            if new_bits:
                is_new = True
                self.overall_coverage[i] &= ~new_bits
        return is_new

    def check_and_update_coverage(self, cur_coverage: CoverageBitmap) -> bool:
        """New coverage includes new bits, DOES update overall coverage"""
        is_new = False
        cur_bitmap = cur_coverage.bitmap
        for i in range(BITMAP_SIZE):
            new_bits = cur_bitmap[i] & self.overall_coverage[i]
            if new_bits:
                is_new = True
                self.overall_coverage[i] &= ~new_bits
        return is_new

    def add_new_input(self, cur_input: Path, cur_coverage: CoverageBitmap, parent_input: Optional[Path]) -> Optional[str]:
        if cur_coverage.is_new:
            self.queue.append(cur_input)
            self.inputs.append(cur_input)


def get_scheduler(config) -> Scheduler:
    return RoundRobinScheduler()
