@echo off
title MySQL Password Reset - Run as Administrator

:: Check for admin rights
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ============================================
    echo  ERROR: Please right-click this file and
    echo  select "Run as administrator"
    echo ============================================
    pause
    exit /b 1
)

set MYSQL_BIN=C:\Program Files\MySQL\MySQL Server 9.7\bin
set DATADIR=C:\ProgramData\MySQL\MySQL Server 9.7\Data
set MYINI=C:\ProgramData\MySQL\MySQL Server 9.7\my.ini
set INIT_FILE=C:\ProgramData\MySQL\reset_pw.sql
set NEW_PASS=SatyAi

echo ============================================
echo  MySQL Root Password Reset Tool
echo ============================================
echo.

:: Write the SQL reset file
echo ALTER USER 'root'@'localhost' IDENTIFIED BY '%NEW_PASS%'; > "%INIT_FILE%"
echo FLUSH PRIVILEGES; >> "%INIT_FILE%"
echo. >> "%INIT_FILE%"
echo SQL reset file created.

:: Stop MySQL service
echo.
echo [1/3] Stopping MySQL97 service...
net stop MySQL97 >nul 2>&1
timeout /t 3 /nobreak >nul
echo Done.

:: Start MySQL with init file to reset password
echo.
echo [2/3] Resetting password (this takes ~10 seconds)...
"%MYSQL_BIN%\mysqld.exe" --defaults-file="%MYINI%" --init-file="%INIT_FILE%" --console --daemonize=OFF &
timeout /t 10 /nobreak >nul
taskkill /F /IM mysqld.exe >nul 2>&1
timeout /t 3 /nobreak >nul
echo Done.

:: Start MySQL normally
echo.
echo [3/3] Starting MySQL97 service normally...
net start MySQL97
timeout /t 3 /nobreak >nul

:: Test connection
echo.
echo Testing connection with new password...
"%MYSQL_BIN%\mysql.exe" -u root -p%NEW_PASS% -e "SELECT 'SUCCESS: Connected with new password!' AS Result;" 2>&1

echo.
echo ============================================
echo  Password has been reset to: SatyAi
echo  You can now run your application!
echo ============================================
echo.
pause
