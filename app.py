# -*- coding: utf-8 -*-
import argparse

from paypark import app


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='PayPark Web Application'
    )
    parser.add_argument(
        '--config',
        type=str,
        default='paypark.ini',
        help='Configuration file',
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Debugging mode'
    )
    parser.add_argument(
        '--host',
        type=str,
        default='0.0.0.0',
        help='Host address'
    )
    parser.add_argument(
        '--port',
        type=int,
        default=8085,
        help='Port'
    )

    args = parser.parse_args()
    app.run(
        debug=args.debug,
        host=args.host,
        port=args.port
    )
