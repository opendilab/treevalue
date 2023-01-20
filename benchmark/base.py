import os
import shutil

CMP_N = int(os.environ.get('CMP_N', None) or '5')
HAS_CUDA = bool(os.environ.get('HAS_CUDA', shutil.which('nvidia-smi')))
