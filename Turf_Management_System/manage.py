import argparse
from app import app


def main():
    parser = argparse.ArgumentParser(description='Manage the Turf Management app')
    parser.add_argument('command', nargs='?', default='runserver', help='command to run (runserver)')
    parser.add_argument('--host', default='127.0.0.1')
    parser.add_argument('--port', type=int, default=5000)
    args = parser.parse_args()

    if args.command in ('runserver', 'run'):
        app.run(host=args.host, port=args.port, debug=True)
    else:
        print('Unknown command:', args.command)


if __name__ == '__main__':
    main()
