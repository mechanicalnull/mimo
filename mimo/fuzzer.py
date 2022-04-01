from socket import timeout
from typing import Optional, List, Tuple
from threading import Thread
from pathlib import Path

import os
import random
import shutil
import time

from .mutators.base import Mutator, get_mutator
from .executor import Executor, get_executor
from .scheduler import Scheduler, get_scheduler
from .config import Configuration

class Fuzzer():
    def __init__(self, config: Configuration, random_seed: Optional[int]=None):
        if random_seed is not None:
            print(f'[*] Using constant random seed for testing: {random_seed}')
            random.seed(random_seed)
        self.config = config
        self.executor: Executor = get_executor(config)
        self.mutator: Mutator = get_mutator(config)
        self.scheduler: Scheduler = get_scheduler(config)
        self.input_count = 0
        self.crash_count = 0

        #self.update_interval: float = 0.1
        self.update_interval: float = 1.0
        self.update_thread: Optional[Thread] = None
        self.should_stop = False

        self.execs: int = 0
        self.start_time: float = time.time()
        # For calculating execs/sec
        self.last_print_time: float = self.start_time
        self.last_execs = 0

    def initialize(self):
        print(f'[MIMO] Initializing...')

        # "Dry run" of getting coverage for initial inputs
        original_inputs = list(self.config.input_dir.glob('*'))
        for cur_input_path in original_inputs:
            new_id = f'id-{self.input_count}'
            new_path = self.config.queue_dir.joinpath(new_id)

            with open(cur_input_path, 'rb') as f:
                cur_input_data = f.read()
            # For demonstration on toy targets
            cur_input_str = cur_input_data.decode(errors="backslashreplace")

            result = self.executor.run_input(cur_input_data)
            result.is_new = self.scheduler.check_and_update_coverage(result)
            self.scheduler.add_new_input(new_path, result, None)
            print(f'[{self.input_count}] Starting input: "{cur_input_str}" (new_coverage: {result.is_new})')

            shutil.copy(cur_input_path.as_posix(), new_path)
            self.input_count += 1

        self.scheduler.set_initial_inputs()

    def run(self, time_limit=0):
        """The fuzzing loop happens here"""
        print('[MIMO] ...Monkeys, at your stations!')
        # Run display in separate thread
        self.update_thread = Thread(target=self.update_thread_main, args=())
        self.update_thread.start()

        try:
            while self.should_stop is False:
                # Pick the next most promising input and how much to fuzz it
                self.cur_input, num_mutations = self.scheduler.pick_next_input()

                self.fuzz_one_input(self.cur_input, num_mutations)

                if time_limit and time.time() - self.start_time > time_limit:
                    self.should_stop = True

        except KeyboardInterrupt:
            print('[!] Caught CTRL+C in main thread, bailing...')
        finally:
            self.should_stop = True

        self.update_thread.join()
        print('[MIMO] ...All typewriters are silent.')


    def fuzz_one_input(self, cur_input: Path, fuzz_iterations: int):
        """Mutate and run an input a variable number of times"""

        self.mutator.set_input(cur_input)
        while fuzz_iterations > 0:
            mutated_bytes = self.mutator.get_next_mutation()

            result = self.executor.run_input(mutated_bytes)

            if result.is_crash:
                self.save_crash(mutated_bytes)
                if self.config.stop_on_first_crash:
                    self.should_stop = True
                    duration = time.time() - self.start_time
                    print(f'[*] Stopping on first crash after {duration:.02f} seconds')
                    return

            result.is_new = self.scheduler.check_and_update_coverage(result)
            if result.is_new:
                new_input_bytes = mutated_bytes.decode(errors='backslashreplace').strip()
                print(f'[{self.input_count}] New input: "{new_input_bytes}"')
                new_input_path = self.save_new_input(mutated_bytes, cur_input)
                self.scheduler.add_new_input(new_input_path, result, cur_input)

            self.execs += 1
            fuzz_iterations -= 1

    @staticmethod
    def get_id_from_name(name: str) -> str:
        return name.split('-')[1]

    def save_new_input(self, in_bytes: bytearray, parent_input: Path) -> Path:
        parent_id = self.get_id_from_name(parent_input.name)
        new_input_name = f'id-{self.input_count}-from-{parent_id}'
        self.input_count += 1

        new_input_path = self.config.queue_dir.joinpath(new_input_name)
        with open(new_input_path.as_posix(), 'wb') as f:
            f.write(in_bytes)

        return new_input_path

    def save_crash(self, in_bytes: bytearray) -> Path:
        source_id = self.get_id_from_name(self.cur_input.name)
        crash_name = f'crash-{self.crash_count}-from-{source_id}'
        self.crash_count += 1

        crash_path = self.config.crashes_dir.joinpath(crash_name)
        with open(crash_path.as_posix(), 'wb') as f:
            f.write(in_bytes)

        print(f'[+] Crash saved to: {crash_path}')
        # For demonstration on toy targets
        crashing_input = in_bytes.decode(errors="backslashreplace")
        print(f'[C] Crashing input: "{crashing_input}"')

        return crash_path

    def update_thread_main(self):
        try:
            time.sleep(self.update_interval)
            while True:
                self.print_stats()
                if self.should_stop:
                    break
                time.sleep(self.update_interval)
        finally:
            self.should_stop = True

    def print_stats(self):
        time_now = time.time()
        time_delta = time_now - self.last_print_time

        new_execs = self.execs - self.last_execs
        execs_per_sec = new_execs / time_delta
        time_elapsed = time_now - self.start_time

        print(f'[*] Execs: {self.execs}; '
                f'Corpus: {self.input_count}; Crashes: {self.crash_count}; '
                f'Time elapsed: {time_elapsed:.3f}; Execs/sec: {execs_per_sec:.2f}')

        self.last_print_time = time_now
        self.last_execs = self.execs

