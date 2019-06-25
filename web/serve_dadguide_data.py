import argparse
import json
import pymysql


def parse_args():
    parser = argparse.ArgumentParser(description="Echos DadGuide database data", add_help=False)

    inputGroup = parser.add_argument_group("Input")
    inputGroup.add_argument("--db_config", help="JSON database info")
    inputGroup.add_argument("--table", help="Table name")
    inputGroup.add_argument("--tstamp", help="DadGuide tstamp field limit")
    inputGroup.add_argument("--plain", action='store_true', help="Print a more readable output")

    return parser.parse_args()


def dump_table(table_name, cursor):
    result_json = {'items': []}
    for row in cursor:
        result_json['items'].append(row)

    return result_json


def load_from_db(db_config, table, tstamp):
    connection = pymysql.connect(host=db_config['host'],
                                 user=db_config['user'],
                                 password=db_config['password'],
                                 db=db_config['db'],
                                 charset=db_config['charset'],
                                 cursorclass=pymysql.cursors.DictCursor)

    table = table.lower()
    sql = 'SELECT * FROM `{}`'.format(table)

    if table == 'timestamps':
        pass
    else:
        sql += ' WHERE tstamp > {}'.format(int(tstamp))

        if table == 'schedule':
            sql += ' AND close_timestamp > UNIX_TIMESTAMP()'

    with connection.cursor() as cursor:
        cursor.execute(sql)
        data = dump_table(table, cursor)

    connection.close()
    return data


def main(args):
    with open(args.db_config) as f:
        db_config = json.load(f)
    data = load_from_db(db_config, args.table, args.tstamp)

    if args.plain:
        print(json.dumps(data, indent=4, sort_keys=True))
    else:
        print(json.dumps(data))


if __name__ == "__main__":
    args = parse_args()
    main(args)