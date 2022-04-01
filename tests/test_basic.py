from typing import Optional

import shutil
import time
from pathlib import Path

from mimo.fuzzer import Fuzzer
from mimo.config import Configuration


test_dir = Path(__file__).absolute().parent
config_dir = test_dir.joinpath('configs')

def run_config(config_file, seed: Optional[int]=None):
    start = time.time()

    config = Configuration(config_file)
    fuzzer = Fuzzer(config, seed)
    fuzzer.initialize()
    fuzzer.run(30)

    duration = time.time() - start
    print(f'Duration: {duration:.02f}')

    assert(fuzzer.crash_count > 0)

    shutil.rmtree(config.output_dir)


def test_file_target():
    config_file = config_dir.joinpath('file_target.json')
    run_config(config_file, 27)


def test_stdin_target():
    config_file = config_dir.joinpath('stdin_target.json')
    run_config(config_file, 27)


def test_wordle():
    config_file = config_dir.joinpath('wordle.json')
    run_config(config_file, 0)
