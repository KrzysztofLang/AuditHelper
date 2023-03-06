from __future__ import generators
from sympy import false, true
from easygui import *
import win32net as wn
import numpy as np
import socket as so
import subprocess as su
import os
import csv


# Okno programu do wpisania informacji o komputerze
def get_user_info():
    # Przygotowanie właściwości okna
    msg = "Wprowadź potrzebne dane"
    title = "AuditHelper"
    fieldNames = ["Nazwa BetterIT", "Użytkownik odpowiedzialny", "Uwagi"]
    fieldValues = []

    # Wyświetlenie okna, zwrócenie wpisanych informacji
    return multenterbox(msg, title, fieldNames)


# Zebranie informacji o podpiętych udziałąch sieciowych,
# zwracane jako lista
def get_network_shares():
    resume = 0
    (drives, total, resume) = wn.NetUseEnum(None, 0, resume)
    return drives


# Sprawdzenie AnyDesk ID
def get_anydesk_id():
    # Utworzenie pliku ze skryptem zapisującym AnyDesk ID do pliku
    lines = [
        "@echo off",
        "path=C:\Program Files (x86)\AnyDesk-c035baa3;%path%",
        "for /f \"delims=\" %%i in ('AnyDesk-c035baa3 --get-id') do set CID=%%i",
        "echo %CID% > AnyDeskID.txt",
    ]
    with open("GetAnyDeskID.bat", "w") as f:
        for line in lines:
            f.write(line)
            f.write("\n")

    # Uruchomienie skryptu
    su.run("GetAnyDeskID.bat")

    # Odczytanie AnyDesk ID z pliku
    with open("AnyDeskID.txt", "r") as f:
        id = f.read().rstrip()

    # Usunięcie plików tymczasowych
    os.remove("GetAnyDeskID.bat")
    os.remove("AnyDeskID.txt")

    return id


# Główna funkcaj programu zbierająca dane i zapisująca do pliku
def save_data(info, hostname, anyDeskID, shares):
    # Jeśli plik nie istnieje, tworzy go i dodaje linię z nagłówkami
    if os.path.isfile("dane.csv") == 0:
        with open("dane.csv", "w") as dane:
            dane_writer = csv.writer(
                dane,
                delimiter=",",
                quotechar='"',
                quoting=csv.QUOTE_MINIMAL,
                lineterminator="\n",
            )
            dane_writer.writerow(
                [
                    "Nazwa BetterIT",
                    "Uzytkownik odpowiedzialny",
                    "Hostname",
                    "AnyDesk ID",
                    "Udzial sieciowy lokalny",
                    "Udzial sieciowy zdalny",
                    "Uwagi",
                ]
            )

    # Zapisuje zebrane dane do pliku
    with open("dane.csv", "a") as dane:
        dane_writer = csv.writer(
            dane,
            delimiter=",",
            quotechar='"',
            quoting=csv.QUOTE_MINIMAL,
            lineterminator="\n",
        )
        for share in shares:
            dane_writer.writerow(
                [
                    info[0],
                    info[1],
                    hostname,
                    anyDeskID,
                    share["local"],
                    share["remote"],
                    info[2],
                ]
            )

    # Okno potwierdzające zakończenie działanie
    msgbox("Zakonczono zapisywanie!", "AuditHelper")


# Wywołanie głównej funkcji
save_data(
    get_user_info(), so.gethostname(), get_anydesk_id(), get_network_shares()
)
