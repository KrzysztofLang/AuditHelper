"""Program ułatwiający wdrażanie SOI na komputerach, tj:
Instalacja narzędzi - AnyDesk, nVision, OpenAudit
Utworzenie konta administratora BITAdmin
Zebranie niezbędnych informacji i zapisanie do plików
"""

__author__ = "Krzysztof Lang"
__version__ = "2.2"
__status__ = "Dev"

from sympy import false, true
from easygui import *
import win32net as wn
import numpy as np
import socket as so
import subprocess as su
import os
import csv
import secrets
import shutil


# Klasa odpowiadająca za instalację oprogramowania
class InstallTools:
    """Instalacja narzędzi i utworzenie konta BITAdmin"""

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
            if os.path.exists("anydesk"):
                # Przygotowanie plików do instalacji
                shutil.copytree("anydesk", "C:\BIT", dirs_exist_ok=True)
                # Uruchomienie instalatora
                exec = su.Popen(
                    [
                        "powershell",
                        '& {msiexec /i "C:\BIT\AnyDesk_BetterIT_ACL.msi" /quiet}',
                    ]
                )
                exec.wait()
            else:
                msgbox("Nie znaleziono instalatora Anydesk!", "AuditHelper")

        # Instalowanie nVision
        if not self.nvision:
            if os.path.exists("nVision"):
                # Przygotowanie plików do instralacji
                shutil.copytree("nVision", "C:\BIT", dirs_exist_ok=True)
                # Uruchomienie instalatora
                exec = su.Popen(
                    [
                        "powershell",
                        '& {msiexec /i "C:\BIT\nVAgentInstall.msi" /quiet}',
                    ]
                )
                exec.wait()
            else:
                msgbox("Nie znaleziono instalatora nVision!", "AuditHelper")

        # Dodanie zadania harmonogramu OpenAudIT
        if os.path.exists("openaudit"):
            # Przygotowanie plików do instralacji
            shutil.copytree("openaudit", "C:\BIT", dirs_exist_ok=True)
            # Uruchomienie instalatora
            su.run("C:\BIT\INSTALL.bat")
        else:
            msgbox("Nie znaleziono instalatora OpenAudIT!", "AuditHelper")

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
    """Zebranie informacji i zapisanie do pliku"""

    def __init__(self, install) -> None:
        # Wywołanie głównej funkcji
        print("Zbieram informacje")
        self.get_user_info()
        self.get_network_shares()
        self.hostname = so.gethostname()
        self.get_anydesk_id()
        self.pwd = install.pwd
        print("Zapisuję informacje o kumputerze")
        self.save_info()
        self.save_pass()
        msgbox("Zakończono zapisywanie!", "AuditHelper")

    # Okno programu do wpisania informacji o komputerze
    def get_user_info(self):
        # Przygotowanie właściwości okna
        msg = "Wprowadź potrzebne dane"
        title = "AuditHelper"
        fieldNames = ["Nazwa BetterIT", "Użytkownik odpowiedzialny", "Uwagi"]

        # Wyświetlenie okna, zwrócenie wpisanych informacji
        print("Wyświetlam okno do wpisania informacji")
        self.name, self.user, self.notes = multenterbox(msg, title, fieldNames)

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
    def save_info(self):
        # Jeśli plik nie istnieje, tworzy go i dodaje linię z nagłówkami
        filename = "dane_" + self.name[:3] + ".csv"
        print("Sprawdzam istnienie pliku")
        if os.path.isfile(filename) == 0:
            print("Plik nie istnieje, tworzę")
            with open(filename, "w") as dane:
                dane_writer = csv.writer(
                    dane,
                    delimiter=",",
                    quotechar='"',
                    quoting=csv.QUOTE_MINIMAL,
                    lineterminator="\n",
                )
                dane_writer.writerow(
                    [
                        "Hostname",
                        "Nazwa BetterIT",
                        "User",
                        "Uwagi",
                        "AnyDesk ID",
                        "Lokalny",
                        "Zdalny",
                    ]
                )
            print("Utworzono plik")

        # Zapisuje zebrane dane do pliku
        print("Zapisuję dane do pliku")
        with open(filename, "a") as dane:
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
                            self.hostname,
                            self.name,
                            self.user,
                            self.notes,
                            self.anyDeskID,
                            share["local"],
                            share["remote"],
                        ]
                    )
                    print("Zapisano linię danych - znaleziono dyski sieciowe")
            else:
                dane_writer.writerow(
                    [
                        self.hostname,
                        self.name,
                        self.user,
                        self.notes,
                        self.anyDeskID,
                        "",
                        "",
                    ]
                )
                print("Zapisano linię danych - brak dysków sieciowych")

        # Okno potwierdzające zakończenie działania
        print("Zakończono zapisywanie")

    def save_pass(self):
        # Jeśli plik nie istnieje, tworzy go i dodaje linię z nagłówkami
        filename = "pwd_" + self.name[:3] + ".csv"
        print("Sprawdzam istnienie pliku")
        if os.path.isfile(filename) == 0:
            print("Plik nie istnieje, tworzę")
            with open(filename, "w") as dane:
                dane_writer = csv.writer(
                    dane,
                    delimiter=",",
                    quotechar='"',
                    quoting=csv.QUOTE_MINIMAL,
                    lineterminator="\n",
                )
                dane_writer.writerow(
                    [
                        "collections",
                        "type",
                        "name",
                        "notes",
                        "fields",
                        "reprompt",
                        "login_uri",
                        "login_username",
                        "login_password",
                        "login_totp",
                    ]
                )
            print("Utworzono plik")

        # Zapisuje zebrane dane do pliku
        print("Zapisuję dane do pliku")
        with open(filename, "a") as dane:
            dane_writer = csv.writer(
                dane,
                delimiter=",",
                quotechar='"',
                quoting=csv.QUOTE_MINIMAL,
                lineterminator="\n",
            )
            dane_writer.writerow(
                [
                    self.name[:3],
                    "login",
                    self.name,
                    "",
                    "",
                    "",
                    "",
                    "BITAdmin",
                    self.pwd,
                    "",
                ]
            )
            print("Zapisano linię danych")


GetInfo(InstallTools())
print("Zakończono program")
# os.system("pause")
