from __future__ import generators
from sympy import false, true
from easygui import *
import win32net as wn
import numpy as np
import socket as so
import subprocess as su
import os
import csv
import secrets


# Klasa odpowiadająca za instalację oprogramowania
class InstallTools:
    def __init__(self) -> None:
        # Wywołanie funkcji sprawdzającej czy zainstalowano nVision i AnyDesk
        self.check_installs()
        print("Czy wykryto AnyDesk: ", self.anydesk)
        print("Czy wykryto nVision: ", self.nvision)
        self.install()
        self.create_user()

    def check_installs(self):
        # Sprawdzenie czy zainstalowano AnyDesk
        self.anydesk = os.path.exists(
            "C:\Program Files (x86)\AnyDesk-c035baa3"
        )

        # Sprawdzenie czy zainstalowano nVision
        self.nvision = os.path.exists("C:\Program Files (x86)\Axence")

    def install(self):
        # Instalowanie AnyDesk
        if not self.anydesk:
            # Utworzenie pliku ze skryptem instalującym AnyDesk
            print("Tworzę plik ze skryptem - instalacja AnyDesk")
            lines = [
                "@echo off",
                'xcopy "%~dp0\\anydesk" "C:\BIT\\" /y',
                'msiexec/i "C:\BIT\AnyDesk_BetterIT_ACL.msi" /quiet',
            ]
            with open("InstallAnyDesk.bat", "w") as f:
                for line in lines:
                    f.write(line)
                    f.write("\n")

            print("Uruchamiam skrypt")
            # Uruchomienie skryptu
            su.run("InstallAnyDesk.bat")
            os.remove("InstallAnyDesk.bat")

        # Instalowanie nVision
        if not self.nvision:
            # Utworzenie pliku ze skryptem instalujacym nVision
            print("Tworzę plik ze skryptem - instalacja nVision")
            lines = [
                "@echo off",
                'xcopy "%~dp0\\nVision" "C:\BIT\\" /y',
                'msiexec/i "C:\BIT\\nVAgentInstall.msi" /quiet',
            ]
            with open("InstallNvision.bat", "w") as f:
                for line in lines:
                    f.write(line)
                    f.write("\n")

            print("Uruchamiam skrypt")
            # Uruchomienie skryptu
            su.run("InstallNvision.bat")
            os.remove("InstallNvision.bat")

        # Dodanie zadania harmonogramu OpenAudIT
        print("Tworzę plik ze skryptem - instalacja OpenAudIT")
        lines = [
            "@echo off",
            'xcopy "%~dp0\\openaudit" "C:\BIT\\" /y',
        ]
        with open("InstallOpenaudit.bat", "w") as f:
            for line in lines:
                f.write(line)
                f.write("\n")

        print("Uruchamiam skrypt")
        # Uruchomienie skryptu
        su.run("InstallOpenaudit.bat")
        su.run("C:\BIT\INSTALL.bat")
        os.remove("InstallOpenaudit.bat")


    def create_user(self):
        # Generowanie hasła
        self.pwd = secrets.token_urlsafe(8)

        # Tworzenie użytkownika, dodanie do grupy Administratorów
        command = (
            """net user BITAdmin_test """
            + '"{}"'.format(self.pwd)
            + """ /add
        net localgroup Administratorzy BITAdmin_test /add
        net localgroup Administrators BITAdmin_test /add"""
        )
        print(command)
        exec = su.Popen(["powershell", "& {" + command + "}"])
        exec.wait()


# Klasa odpowiadająca za zebranie danych
class GetInfo:
    def __init__(self, install) -> None:
        # Wywołanie głównej funkcji
        self.get_user_info()
        self.get_network_shares()
        self.hostname = so.gethostname()
        self.get_anydesk_id()
        self.pwd = install.pwd
        print("Wywołuję główną funkcję")
        self.save_data()

    # Okno programu do wpisania informacji o komputerze
    def get_user_info(self):
        # Przygotowanie właściwości okna
        msg = "Wprowadź potrzebne dane"
        title = "AuditHelper"
        fieldNames = ["Nazwa BetterIT", "Użytkownik odpowiedzialny", "Uwagi"]

        # Wyświetlenie okna, zwrócenie wpisanych informacji
        print("Wyświetlam okno do wpisania informacji")
        self.info = multenterbox(msg, title, fieldNames)

    # Zebranie informacji o podpiętych udziałąch sieciowych,
    # zwracane jako lista
    def get_network_shares(self):
        print("Odczytuję mapowane dyski")
        resume = 0
        self.shares = 0
        (self.shares, total, resume) = wn.NetUseEnum(None, 0, resume)

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
            self.anyDeskID = f.read().rstrip()

        print(self.anyDeskID)
        print("Czy poprawnie odczytano ID:", self.anyDeskID.isnumeric())

        # Weryfikacja czy udało się odczytać numer
        if not self.anyDeskID.isnumeric():
            self.anyDeskID = ""

        # Usunięcie plików tymczasowych
        print("Usuwam pliki tymczasowe")
        os.remove("GetAnyDeskID.bat")
        os.remove("AnyDeskID.txt")

    # Główna funkcaj programu zbierająca dane i zapisująca do pliku
    def save_data(self):
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
                        "Użytkownik odpowiedzialny",
                        "Hostname",
                        "AnyDesk ID",
                        "Udział sieciowy lokalny",
                        "Udział sieciowy zdalny",
                        "Hasło BITAdmin",
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
            print(self.shares)
            if self.shares:
                for share in self.shares:
                    dane_writer.writerow(
                        [
                            self.info[0],
                            self.info[1],
                            self.hostname,
                            self.anyDeskID,
                            share["local"],
                            share["remote"],
                            self.pwd,
                            self.info[2],
                        ]
                    )
                    print("Zapisano linię danych - znaleziono dyski sieciowe")
            else:
                dane_writer.writerow(
                    [
                        self.info[0],
                        self.info[1],
                        self.hostname,
                        self.anyDeskID,
                        "",
                        "",
                        self.pwd,
                        self.info[2],
                    ]
                )
                print("Zapisano linię danych - brak dysków sieciowych")

        # Okno potwierdzające zakończenie działania
        print("Zakończono zapisywanie")
        msgbox("Zakończono zapisywanie!", "AuditHelper")


info = GetInfo(InstallTools())
print("Zakończono program")
os.system("pause")
