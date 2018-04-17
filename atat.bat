@echo off
title Automated Toner Audit Report

set WHID=Location
set CommunityString=Secret
set printers=color-2, mfp-1, mfp-2, mfp-3, mfp-4, plotter-1, mfp-5, mfp-9
set hostname=Hostname

echo            Automated Toner Audit Report          
for /f "delims=: tokens=*" %%A in ('findstr /b ::: "%~f0"') do @echo(%%A
set /P login=Login: 
echo.
echo Connecting to Server

:confirm_values
echo Using the following values:
echo 	Warehouse ID:  "%WHID%"
echo 	Community String:  "%CommunityString%"
echo 	Printers:  "%printers%"
echo.

:choice
set verify=Y
set /P verify=Is this correct [Y/n]:
if /I "%verify%" EQU "Y" goto :move_along
if /I "%verify%" EQU "N" goto :need_input
goto :choice

:need_input
set /P WHID=Enter Warehouse ID: 
set /P CommunityString=Enter Community String: 
set /P Printers=List all printers seperated by commas: 
echo.
goto :confirm_values


:move_along
plink %hostname% -l %login% "echo Loading Data.  This may take a minute && echo; /usr/share/atat.py %WHID% %CommunityString% ""%printers%"""
pause 




:::                 ____________
:::            _,.-Y  |      |  Y-._
:::        .-~"    |  |      |  |   "-.
:::        I    == |  !      !  | []  |     _____
:::        L__  [] |..----------|    _[----I" .-{"-.
:::       I___|    |  __________|   [__L]_[I_/r(=}=-P
:::      [L________[____________]______j~  '-=c_]/=-^
:::       \_I_j    \==I  |  I==_/   L_]
:::         [_((==)[`---------"](==)j
:::            I--I"~~~"""""~~~"I--I
:::            |  |             |  |
:::            l__j             l__j
:::            |  |             |  |
:::            |  |             |  |
:::            ([])             ([])
:::            ]  [             ]  [
:::            [  ]             [  ] 
:::           /|  |\           /|  |\
:::          | }  { |         | }  { |
:::         .-^--r-^-.       .-^--r-^-.             
:::  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
