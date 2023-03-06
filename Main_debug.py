from __future__ import generators
from sympy import false, true
from easygui import *
import win32net as wn
import numpy as np
import socket as so
import subprocess as su
import os
import csv

# Klasa odpowiadająca za zebranie danych
class GetInfo:
    def __init__(self) -> None:
        # Wywołanie głównej funkcji
        print("Wywołuję główną funkcję")
        self.save_data(
            self.get_user_info(), so.gethostname(), self.get_anydesk_id(), self.get_network_shares()
        )

    # Okno programu do wpisania informacji o komputerze
    def get_user_info(self):
        # Przygotowanie właściwości okna
        msg = "Wprowadź potrzebne dane"
        title = "AuditHelper"
        fieldNames = ["Nazwa BetterIT", "Użytkownik odpowiedzialny", "Uwagi"]
        fieldValues = []

        # Wyświetlenie okna, zwrócenie wpisanych informacji
        print("Wyświetlam okno do wpisania informacji")
        return multenterbox(msg, title, fieldNames)


    # Zebranie informacji o podpiętych udziałąch sieciowych,
    # zwracane jako lista
    def get_network_shares(self):
        print("Odczytuję mapowane dyski")
        resume = 0
        drives = 0
        (drives, total, resume) = wn.NetUseEnum(None, 0, resume)
        return drives


    # Sprawdzenie AnyDesk ID
    def get_anydesk_id(self):
        # Utworzenie pliku ze skryptem zapisującym AnyDesk ID do pliku
        print("Tworzę plik ze skryptem")
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

        print("Uruchamiam skrypt")
        # Uruchomienie skryptu
        su.run("GetAnyDeskID.bat")

        # Odczytanie AnyDesk ID z pliku
        print("Odczytuję ID z pliku")
        with open("AnyDeskID.txt", "r") as f:
            id = f.read().rstrip()

        print(id)
        print("Czy poprawnie odczytano ID:", id.isnumeric())

        # Weryfikacja czy udało się odczytać numer
        if not id.isnumeric():
            id = ""

        # Usunięcie plików tymczasowych
        print("Usuwam pliki tymczasowe")
        os.remove("GetAnyDeskID.bat")
        os.remove("AnyDeskID.txt")

        return id


    # Główna funkcaj programu zbierająca dane i zapisująca do pliku
    def save_data(self, info, hostname, anyDeskID, shares):
        # Jeśli plik nie istnieje, tworzy go i dodaje linię z nagłówkami

        print("Sprawdzam istnienie pliku")
        if os.path.isfile("dane.csv") == 0:
            print("Plik nie istnieje, tworzę")
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
            print("Utworzono plik")

        # Zapisuje zebrane dane do pliku
        print("Zapisuję dane do pliku")
        with open("dane.csv", "a") as dane:
            dane_writer = csv.writer(
                dane,
                delimiter=",",
                quotechar='"',
                quoting=csv.QUOTE_MINIMAL,
                lineterminator="\n",
            )
            print(shares)
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
                    print("Zapisano linię danych - znaleziono dyski sieciowe")
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
                print("Zapisano linię danych - brak dysków sieciowych")

        # Okno potwierdzające zakończenie działania
        print("Zakończono zapisywanie")
        msgbox("Zakończono zapisywanie!", "AuditHelper")



getInfo = GetInfo()
print("Zakończono program")
os.system("pause")
