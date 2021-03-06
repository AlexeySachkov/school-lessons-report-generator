import argparse
import lib

VERSION = '0.1'

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Reports generator')

    parser.add_argument('-v', '--version', action='version', version=VERSION)
    parser.add_argument('action', choices=['generate', 'fetch', 'render'], default='generate')
    parser.add_argument('-d', '--data', dest='data_file', required=True)

    args = parser.parse_args()

    if args.action == 'generate':
        lib.fetch_data(args.data_file)
        lib.render_personal_reports(args.data_file)
        lib.render_main_page(args.data_file)

    elif args.action == 'fetch':
        lib.fetch_data(args.data_file)

    elif args.action == 'render':
        lib.render_personal_reports(args.data_file)
        lib.render_main_page(args.data_file)
