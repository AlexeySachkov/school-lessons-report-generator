import argparse

VERSION = '0.1'

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Reports generator')

    parser.add_argument('-v', '--version', action='version', version=VERSION)

    args = parser.parse_args()
