import time
import json
import os

from pathlib import Path
import shutil


class Configuration():
    config_file: Path
    input_dir: Path
    output_dir: Path
    queue_dir: Path
    crashes_dir: Path
    invocation: str
    stop_on_first_crash: bool
    mutator_name: str

    def __init__(self, config_file: str):
        if not os.path.exists(config_file):
            raise Exception(f'Configuration file "{config_file}" not found')
        self.config_file = Path(config_file)
        with open(config_file) as f:
            self.config_dict = json.load(f)

        self.check_and_set_defaults()


    def check_and_set_defaults(self):
        input_dir = Path(self.config_dict['input_dir'])
        if not input_dir.exists():
            raise Exception(f'Input directory ({input_dir.as_posix()}) not found!')
        elif not input_dir.is_dir():
            raise Exception(f'Input directory ({input_dir.as_posix()}) not a directory!')
        self.input_dir = input_dir

        output_dir = Path(self.config_dict['output_dir'])
        if not output_dir.exists():
            os.makedirs(output_dir.as_posix())
        if not output_dir.is_dir():
            raise Exception(f'Output directory ({output_dir.as_posix()}) not a directory!')
        else:
            if os.listdir(output_dir):
                old_time = os.path.getctime(output_dir)
                old_date = time.strftime('%Y%m%d-%H%M', time.localtime(old_time))
                archive_name = f'{output_dir.name}-{old_date}'
                archive_path = output_dir.parent.joinpath(archive_name)
                output_dir.rename(archive_path)
                print(f'[*] Old output directory found at {output_dir}, moved to {archive_path}')
                os.makedirs(output_dir.as_posix())
        self.output_dir = output_dir 

        self.crashes_dir = output_dir.joinpath('crashes')
        self.crashes_dir.mkdir(exist_ok=False)
        self.queue_dir = output_dir.joinpath('queue')
        self.queue_dir.mkdir(exist_ok=False)

        if 'invocation' not in self.config_dict:
            raise Exception(f'Mandatory field "invocation" not in configuration')
        else:
            invocation = self.config_dict['invocation']
            self.canonicalize_invocation(invocation)

        if 'stop_on_first_crash' not in self.config_dict:
            self.stop_on_first_crash = False
        else:
            self.stop_on_first_crash = self.config_dict['stop_on_first_crash']

        if 'mutator' not in self.config_dict:
            self.mutator_name = 'basic_random'
        else:
            self.mutator_name = self.config_dict['mutator']


    def canonicalize_invocation(self, invocation: str):
        binary_path = invocation.split(' ')[0]

        if binary_path.startswith('/'):
            pass  # absolute paths don't require changes

        elif binary_path.startswith('~/'):
            expanded_path = os.path.expanduser(binary_path)
            if not os.path.exists(expanded_path):
                raise FileNotFoundError(f'Target binary not found ("{binary_path}" -> "{expanded_path}")')
            invocation = invocation.replace(binary_path, expanded_path, 1)

        elif binary_path.startswith('.'):
            config_dir = self.config_file.absolute().parent
            absolute_path = config_dir.joinpath(binary_path)
            if not absolute_path.exists():
                raise FileNotFoundError(f'Target binary not found ("{binary_path}" -> "{absolute_path}")')
            invocation = invocation.replace(binary_path, absolute_path.as_posix(), 1)

        else:
            raise Exception('Invocation must be absolute or relative path')

        self.invocation = invocation
