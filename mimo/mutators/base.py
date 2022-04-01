from typing import Any, Callable, Dict, List

from pathlib import Path
import random

from mimo.config import Configuration

from .mutations import *

class Mutator():
    mutators: List[Callable]
    cur_input: Path
    cur_data: bytearray
    state: Dict[Path, Any]

    def set_input(self, input_path: Path):
        """Read the current input, store state as needed"""
        self.cur_input = input_path
        with open(input_path, 'rb') as f:
            self.cur_data = bytearray(f.read())

    def get_next_mutation(self):
        """Mutator choice strategies to be implemented here"""
        # TODO: intelligently select non-deterministic/deterministic mutators
        mutator = random.choice(self.mutators)
        # TODO: do intelligent fixups instead of copy
        self.new_data = self.cur_data.copy()
        return mutator(self.new_data)


class AsciiMutator(Mutator):
    def __init__(self):
        self.mutators = [set_random_ascii]

class LowercaseMutator(Mutator):
    def __init__(self):
        self.mutators = [set_random_uppercase]


class BasicRandomMutator(Mutator):
    def __init__(self):
        self.mutators = [flip_random_bit, set_random_byte]

mutators = {
    'basic_random': BasicRandomMutator,
    'ascii': AsciiMutator,
    'lowercase': LowercaseMutator,
}

def get_mutator(config: Configuration):
    mutator_class = mutators[config.mutator_name]
    return mutator_class()
