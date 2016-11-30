# -*- coding: utf-8 -*-
import argparse

from paypark import create_app 


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='PayPark Web Application'
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug mode'
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
    parser.add_argument(
        '--config',
        choices=['production','development','testing','default'],
        default='default',
        help='Configuration'
    )
    args = parser.parse_args()
    app = create_app(args.config)
    app.run(
        debug=args.debug,
        host=args.host,
        port=args.port
    )
