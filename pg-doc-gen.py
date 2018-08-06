import argparse
import psycopg2
import sys
import os

class PgDocGen():
  def __init__(self, cfg):
    self.__conn = psycopg2.connect(
      host=cfg['host'], 
      port=cfg['port'], 
      dbname=cfg['name'], 
      user=cfg['user'], 
      password=cfg['password']
    )
    self.__md_file = '%s table structure.md'%cfg['name']
  def fini(self):
    self.__conn.close()
  def __get_all_tables(self):
    with self.__conn.cursor() as cur:
      sql = """
        SELECT table_name FROM information_schema.tables 
        WHERE table_schema = 'public' AND table_name NOT IN (
          SELECT c.relname AS child
          FROM pg_inherits JOIN pg_class AS c ON (inhrelid=c.oid)
        )
        ORDER BY table_name
      """
      cur.execute(sql)
      rs = cur.fetchall()
      return [r[0] for r in rs]
  def gen_md(self):
    if os.path.exists(self.__md_file):
      os.remove(self.__md_file)
    tables = self.__get_all_tables()
    sql = """
      SELECT c.column_name, c.data_type, c.is_nullable, c.column_default, pgd.description
      FROM pg_catalog.pg_statio_all_tables AS st
        LEFT JOIN pg_catalog.pg_description pgd ON (pgd.objoid=st.relid)
        RIGHT JOIN information_schema.columns c ON (pgd.objsubid=c.ordinal_position
          AND c.table_schema=st.schemaname AND c.table_name=st.relname)
      WHERE c.table_schema='{table_schema}' AND c.table_name='{table_name}'
      ORDER BY c.ordinal_position
    """
    fd = open(self.__md_file, 'w+')
    for t in tables:
      with self.__conn.cursor() as cur:
        cur.execute(sql.format(table_schema='public', table_name=t))
        fd.writelines([
          "### %s \n" % t,
          "--- \n",
          "| Field Name | Field Type | Not Null | Default | Description | \n",
          "| ---------- | ---------- | -------- | ------- | ----------- | \n"
        ])
        rs = cur.fetchall()
        for r in rs:
          fd.writelines([
            "| %s | %s | %s | %s | %s | \n" % r
          ])
    fd.close()
      
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
    gen.gen_md()
    gen.fini()
  except Exception as e:
    print(e)