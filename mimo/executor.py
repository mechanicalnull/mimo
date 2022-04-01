from asyncio.subprocess import DEVNULL
from typing import Any
import subprocess

from .config import Configuration
from .coverage import CoverageBitmap, BaseCoverage


class Executor():
    def run_input(self, in_bytes: bytearray) -> BaseCoverage:
        """Run the input, return an instrumentation-specific result.
        Raise exception on error.
        """
        raise NotImplementedError()


class ReturnCodeExecutor(Executor):
    """Toy Executor that uses return code to fake a coverage bitmap"""
    def __init__(self, config: Configuration):
        # For this Executor, config dictates how to deliver input to target
        invocation = config.invocation
        if '@@' in invocation:
            self.delivery = 'file'
            self.run_input = self.run_with_file
            self.filename = '.cur_input'
            self.invocation = invocation.replace('@@', self.filename).split()
        else:
            self.delivery = 'stdin'
            self.run_input = self.run_with_stdin
            self.invocation = invocation.split()
        self.return_codes_seen = set()

    def run_with_file(self, in_bytes: bytearray) -> CoverageBitmap:
        with open(self.filename, 'wb') as f:
            f.write(in_bytes)
        child_proc = subprocess.run(self.invocation)
        return self.get_coverage(child_proc.returncode)

    def run_with_stdin(self, in_bytes: bytearray) -> CoverageBitmap:
        child_proc = subprocess.run(self.invocation, input=in_bytes, stdout=subprocess.DEVNULL)
        return self.get_coverage(child_proc.returncode)

    def get_coverage(self, return_code: int) -> CoverageBitmap:
        coverage_bitmap = CoverageBitmap()
        coverage_bitmap.is_crash =  self.result_is_crash(return_code)
        coverage_bitmap.bitmap[return_code] = 1
        return coverage_bitmap

    def result_is_crash(self, return_code: int) -> bool:
        if return_code < 0 or return_code == 255:
            return True
        else:
            return False


def get_executor(config) -> Executor:
    # Once multiple executors, get executor name from config
    return ReturnCodeExecutor(config)
