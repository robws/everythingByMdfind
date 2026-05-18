"""Do something on the CLI and allow for F5 Debugging in VS Code

Typical usage example:

(From VSCode)
    change the value of default_this_arg
    Press F5 to run
    
(From the CLI in this UV project)
    uv run scripts/_example_script.py --this_arg "Foo"
"""
import sys
import os
import argparse

def real_function(this_arg):
    print(f"This arg: {this_arg}")


def main():
    
    default_this_arg = "Hello"
   
    if 'debugpy' in sys.modules:
        sys.argv = [
            sys.argv[0],
            "--this_arg",default_this_arg
        ]

    parser = argparse.ArgumentParser(
        description='Some description'
    )
    parser.add_argument(
        '--this_arg',
        default=default_this_arg,
        help=f"Some contrived arg"
    )
    args = parser.parse_args()
    
    real_function(args.this_arg)

if __name__ == '__main__':
    main()
