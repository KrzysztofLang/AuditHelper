# Audit Helper

Program mający ułatwić proces audytu lokalnego. Sposób działania:

1. Wykrycie instalacji AnyDesk i agenta nVision
2. Instalacja AnyDesk i nVision jeśli nie zostały wykryte, dodanie zadania harmonogramu OpenAudit
3. Utworzenie konta administracyjnego BITAdmin wraz z losowym hasłem
4. Wyświetlenie okna do wpisania danych nt komputera:
   1. Nadanej nazwy
   2. Użytkownika odpowiedzialnego
   3. Dodatkowe uwagi
5. Automatyczne zebranie dodatkowych informacji:
   1. Hostname
   2. Podmapowane udziały sieciowe
   3. AnyDesk ID
6. Zapisanie informacji do 2 plików:
   1. dane_XXX.csv - informacje nt komputera
   2. pwd_XXX.csv - plik z hasłem użytkownika BITAdmin do zaimportowania do Bitwarden
