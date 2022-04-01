# MILLION MONKEYS (aka mimo)

mimo is a modular fuzzer written to be easy to extend and experiment. It's meant
to be simple to modify so you can examine and tinker with any part of the
fuzzer.

Support is limited to Linux usermode programs for now.

It's still a work in progress, so everything is subject to change.

## Quick Start

mimo puts all of the options in the config file, and comes with some builtin
test targets and configs as examples. Run the following to try one out.

```bash
cd tests
make
cd ..
python3 mimo.py tests/configs/wordle.json
```
