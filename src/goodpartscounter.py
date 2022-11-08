####################################
##### Connection to SQL Server #####
####################################

import pyodbc
import datetime


def getCounter(machine, server, database, username, password):
    # Date yesterday
    dt = datetime.date.today()
    dt = datetime.datetime(dt.year, dt.month, dt.day) + datetime.timedelta(days=-1)

    cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)
    cursor = cnxn.cursor()

    #QTYGOOD= Menge Gutteile, TRANSREFID= Auftragsnummer, TRANSTYPE= Einheit der Buchung [MENGE], DATEWIP= DATUM

    cursor.execute("SELECT QTYGOOD, TRANSREFID FROM TCMProdRouteTransStaging WHERE TRANSTYPE=1 AND WRKCTRID=? AND DATEWIP=? AND QTYGOOD!=0", machine, dt)
    data = cursor.fetchall()

    good_parts_counter = []

    for rows in data:
        good_parts_counter.append(int(rows[0]))

    total_counter = sum(good_parts_counter)

    return total_counter




