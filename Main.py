from __future__ import generators
from sympy import false, true
from easygui import *
import win32net as wn
import numpy as np
import socket as so
import subprocess as su
import os
import csv


class InstallTools:
    def __init__(self) -> None:
        exit()


class GetInfo:
    def __init__(self) -> None:
        # Uruchamianie poszczególnych funkcji zbierających dane
        info = self.get_user_info()
        hostname = so.gethostname()
        anyDeskID = self.get_anydesk_id()
        shares = self.get_network_shares()

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
            if shares:
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
            else:
                dane_writer.writerow(
                    [
                        info[0],
                        info[1],
                        hostname,
                        anyDeskID,
                        "",
                        "",
                        info[2],
                    ]
                )

        # Okno potwierdzające zakończenie działania
        msgbox("Zakończono zapisywanie!", "AuditHelper")

    # Okno programu do wpisania informacji o komputerze
    @staticmethod
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
    @staticmethod
    def get_network_shares():
        resume = 0
        drives = 0
        (drives, total, resume) = wn.NetUseEnum(None, 0, resume)
        return drives

    # Sprawdzenie AnyDesk ID
    @staticmethod
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

        # Weryfikacja czy udało się odczytać numer
        if not id.isnumeric():
            id = ""

        # Usunięcie plików tymczasowych
        os.remove("GetAnyDeskID.bat")
        os.remove("AnyDeskID.txt")

        return id


# Wywołanie głównej funkcji
getInfo = GetInfo()
