import pyodbc

# "Arbeitsplan" D365


def get_ideal_cycle_time(machine, server, database, username, password, article):

    article = article + "B"

    cnxn = pyodbc.connect(
        'DRIVER={ODBC Driver 17 for SQL Server};SERVER=' + server + ';DATABASE=' + database + ';UID=' + username + ';PWD=' + password)
    cursor = cnxn.cursor()

    # QTYGOOD= Menge Gutteile, TRANSREFID= Auftragsnummer, TRANSTYPE= Einheit der Buchung [MENGE], DATEWIP= DATUM

    if article.startswith("2"):
        ideal_cycle_time = "500"

    else:
        cursor.execute("SELECT PROCESSPERQTY FROM TCMRouteOprStaging WHERE OPRID=? AND ITEMRELATION=?", machine, article)
        data = cursor.fetchall()

        if not data:
            cursor.execute("SELECT PROCESSPERQTY FROM TCMRouteOprStaging WHERE OPRID=? AND ITEMRELATION=?", "1065",
                           article)
            data = cursor.fetchall()

        ideal_cycle_time = (60 / int(data[-1][0])) * 60

    #print(ideal_cycle_time)

    return ideal_cycle_time

