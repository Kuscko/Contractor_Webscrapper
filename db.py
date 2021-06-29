from datetime import datetime, timedelta
import sqlite3
from contextlib import closing

# Local imports
from objects import Contract

conn = None


def connect():
    global conn
    if not conn:
        conn = sqlite3.connect('_db\contracts.sqlite')
        conn.row_factory = sqlite3.Row


def close():
    if conn:
        conn.close()


def make_contract(row):
    return Contract(row["contractID"], row["name"], row["email"], row["phone"], row["sent"], row["lastDateSent"],
                    make_contract(row))


def make_contracts(row):
    return Contract(row["contractID"], row["name"], row["email"], row["phone"], row["sent"], row["lastDateSent"])


def get_contracts():
    query = '''SELECT contractID, name, email, phone, sent, lastDateSent
               FROM ContractInformation'''
    with closing(conn.cursor()) as c:
        c.execute(query)
        results = c.fetchall()
    categories = []
    for row in results:
        categories.append(make_contracts(row))
    return categories


def get_contract(contract_id):
    query = '''SELECT name, email, phone, sent, lastDateSent
               FROM ContractInformation
               WHERE Contract.ID = ?'''
    with closing(conn.cursor()) as c:
        c.execute(query, (contract_id,))
        row = c.fetchone()
    contract = make_contract(row)
    return contract


def get_contract_by_email(email):
    query = '''SELECT contractID, name, email, phone, sent, lastDateSent
                   FROM ContractInformation
                   WHERE email = ?'''
    with closing(conn.cursor()) as c:
        c.execute(query, (email,))
        row = c.fetchall()
    return len(row)


def add_contract(contract):
    sql = '''INSERT INTO ContractInformation(name, email, phone, sent)
             VALUES(?, ?, ?, ?)'''
    with closing(conn.cursor()) as c:
        c.execute(sql, (contract.name, contract.email, contract.phone, contract.sent))
        conn.commit()


def delete_contract(contract_id):
    sql = '''DELETE FROM ContractInformation WHERE ID = ?'''
    with closing(conn.cursor()) as c:
        c.execute(sql, (contract_id,))
        conn.commit()


def update_contract(row):
    sql = '''UPDATE ContractInformation
             SET name = ?, email = ?, phone = ?, sent = ?, lastDateSent=?
             WHERE contractID = ?'''
    date_1 = datetime.today()
    date = date_1 + timedelta(days=30)
    with closing(conn.cursor()) as c:
        c.execute(sql, (row.name, row.email, row.phone, 1, date.strftime("%Y-%m-%d"), row.contractID))
        conn.commit()
