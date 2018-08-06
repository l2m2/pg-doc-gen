import argparse
import psycopg2
import sys

class PgDocGen():
  def __init__(self, cfg):
    self.__conn = psycopg2.connect(
      host=cfg['host'], 
      port=cfg['port'], 
      dbname=cfg['name'], 
      user=cfg['user'], 
      password=cfg['password']
    )
  def fini(self):
    self.__conn.close()
  def get_all_tables(self):
    with self.__conn.cursor() as cur:
      sql = """
        SELECT table_name FROM information_schema.tables 
        WHERE table_schema = 'public'
        ORDER BY table_name
      """
      cur.execute(sql)
      rs = cur.fetchall()
      return [r[0] for r in rs]
      
if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='PostgreSQL Document Generator.')
  parser.add_argument('--host', type=str, required=True, help='database host', metavar='127.0.0.1')
  parser.add_argument('--port', type=str, required=False, default='5432', help='database port', metavar='5432')
  parser.add_argument('--name', type=str, required=True, help='database name', metavar='DB_NAME')
  parser.add_argument('--user', type=str, required=True, metavar='USER')
  parser.add_argument('--password', type=str, required=True,  metavar='PASSWORD')
  args = parser.parse_args()
  try:
    print(vars(args))
    gen = PgDocGen(vars(args))
    print(gen.get_all_tables())
    # todo
    # export each table structure to markdown
    gen.fini()
  except Exception as e:
    print(e)