@echo off
set PYTHON=C:\Users\anaba\AppData\Local\Programs\Python\Python312\python.exe
set WORKDIR=C:\Users\anaba\OneDrive\Desktop\Python fördjupat\Kunskapskontroll 2

cd /d %WORKDIR%
echo ==== START %date% %time% ==== >> pipeline.log

%PYTHON% main.py >> pipeline.log 2>&1
%PYTHON% report.py >> pipeline.log 2>&1

echo ==== END %date% %time% ==== >> pipeline.log

