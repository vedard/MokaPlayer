import sys

if sys.platform.startswith('linux'):
    from .linux import KeyboardClient
elif sys.platform.startswith('win'):
    from .win import KeyboardClient
