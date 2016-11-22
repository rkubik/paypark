# -*- coding: utf-8 -*-
from paypark.database import init_db, db_session
from paypark.models import User, ZoneGroup, ZoneSchedule, Zone, PhoneNumber, LicensePlate
import argparse
from datetime import datetime


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Database Migration Tool')
    parser.add_argument(
        '--init',
        action='store_true',
        help='Initialize database'
    )
    parser.add_argument(
        '--demo',
        action='store_true',
        help='Preload with demo data'
    )
    args = parser.parse_args()

    if args.init:
        init_db()

    if args.demo:
        objs = [
            User('demo', 'demo', 'demo@demo.com', 'demo', balance=10000),
            ZoneGroup('Downtown'),
            ZoneSchedule(1, 375, 60, datetime.strptime('09:00', '%H:%M').time(), datetime.strptime('18:00', '%H:%M').time(), '0123456'),
            ZoneSchedule(1, 110, 30, datetime.strptime('18:00', '%H:%M').time(), datetime.strptime('23:00', '%H:%M').time(), '0123456'),
            Zone('1000', '123 Fake Street SW', 1),
        ]
        for obj in objs:
            db_session.add(obj)
        db_session.commit()
