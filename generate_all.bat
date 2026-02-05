@echo off
REM COPD教材 リップシンク動画一括生成スクリプト (Windows版)
REM 使用方法: SadTalkerフォルダで実行

setlocal enabledelayedexpansion

REM パス設定（必要に応じて変更）
set SADTALKER_DIR=%~dp0..\SadTalker
set DATA_DIR=%~dp0
set OUTPUT_DIR=%DATA_DIR%videos

echo ============================================================
echo COPD教材 リップシンク動画一括生成
echo ============================================================
echo SadTalker: %SADTALKER_DIR%
echo データ: %DATA_DIR%
echo 出力先: %OUTPUT_DIR%
echo ============================================================

REM 出力ディレクトリ作成
if not exist "%OUTPUT_DIR%" mkdir "%OUTPUT_DIR%"

REM カウンター
set /a SUCCESS=0
set /a FAIL=0
set /a TOTAL=66

REM 仮想環境有効化
cd /d "%SADTALKER_DIR%"
call venv\Scripts\activate.bat

echo.
echo 処理を開始します...
echo.

REM シーン3
call :generate s03_01 kazuo kazuo_expressions\kazuo_general_05_neutral.png
call :generate s03_02 ichiko ichiko_expressions\ichiko_05_neutral.png
call :generate s03_03 kazuo kazuo_expressions\kazuo_general_05_neutral.png
call :generate s03_04 ichiko ichiko_expressions\ichiko_05_neutral.png
call :generate s03_05 kazuo kazuo_expressions\kazuo_general_05_neutral.png
call :generate s03_06 ichiko ichiko_expressions\ichiko_05_neutral.png

REM シーン4
call :generate s04_01 yamada yamada_expressions\yamada_05_neutral.png
call :generate s04_02 kazuo kazuo_expressions\kazuo_general_05_neutral.png
call :generate s04_03 yamada yamada_expressions\yamada_05_neutral.png
call :generate s04_04 yamada yamada_expressions\yamada_05_neutral.png
call :generate s04_05 yamada yamada_expressions\yamada_05_neutral.png
call :generate s04_06 kazuo kazuo_expressions\kazuo_general_05_neutral.png
call :generate s04_07 yamada yamada_expressions\yamada_05_neutral.png

REM シーン5
call :generate s05_01 yamada yamada_expressions\yamada_05_neutral.png
call :generate s05_02 ichiko ichiko_expressions\ichiko_05_neutral.png
call :generate s05_03 yamada yamada_expressions\yamada_05_neutral.png
call :generate s05_04 kazuo kazuo_expressions\kazuo_general_05_neutral.png
call :generate s05_05 yamada yamada_expressions\yamada_05_neutral.png
call :generate s05_06 kazuo kazuo_expressions\kazuo_general_05_neutral.png
call :generate s05_07 yamada yamada_expressions\yamada_05_neutral.png

REM シーン6
call :generate s06_01 yamada yamada_expressions\yamada_05_neutral.png
call :generate s06_02 kazuo kazuo_expressions\kazuo_general_05_neutral.png
call :generate s06_03 yamada yamada_expressions\yamada_05_neutral.png
call :generate s06_04 yamada yamada_expressions\yamada_05_neutral.png
call :generate s06_05 kazuo kazuo_expressions\kazuo_general_05_neutral.png
call :generate s06_06 yamada yamada_expressions\yamada_05_neutral.png
call :generate s06_07 kazuo kazuo_expressions\kazuo_general_05_neutral.png
call :generate s06_08 yamada yamada_expressions\yamada_05_neutral.png

REM シーン7
call :generate s07_01 kazuo kazuo_expressions\kazuo_general_05_neutral.png
call :generate s07_02 pharmacist pharmacist_expressions\pharmacist_05_neutral.png
call :generate s07_03 kazuo kazuo_expressions\kazuo_general_05_neutral.png
call :generate s07_04 pharmacist pharmacist_expressions\pharmacist_05_neutral.png
call :generate s07_05 pharmacist pharmacist_expressions\pharmacist_05_neutral.png
call :generate s07_06 kazuo kazuo_expressions\kazuo_general_05_neutral.png

REM シーン8
call :generate s08_01 doctor doctor_expressions\doctor_05_neutral.png
call :generate s08_02 kazuo kazuo_expressions\kazuo_general_05_neutral.png
call :generate s08_03 doctor doctor_expressions\doctor_05_neutral.png
call :generate s08_04 kazuo kazuo_expressions\kazuo_general_05_neutral.png
call :generate s08_05 doctor doctor_expressions\doctor_05_neutral.png
call :generate s08_06 doctor doctor_expressions\doctor_05_neutral.png
call :generate s08_07 kazuo kazuo_expressions\kazuo_general_05_neutral.png
call :generate s08_08 doctor doctor_expressions\doctor_05_neutral.png

REM シーン9
call :generate s09_01 sato sato_expressions\sato_05_neutral.png
call :generate s09_02 ichiko ichiko_expressions\ichiko_05_neutral.png
call :generate s09_03 sato sato_expressions\sato_05_neutral.png
call :generate s09_04 kazuo kazuo_expressions\kazuo_general_05_neutral.png
call :generate s09_05 sato sato_expressions\sato_05_neutral.png
call :generate s09_06 ichiko ichiko_expressions\ichiko_05_neutral.png
call :generate s09_07 sato sato_expressions\sato_05_neutral.png

REM シーン10
call :generate s10_01 ichiko ichiko_expressions\ichiko_05_neutral.png
call :generate s10_02 kazuo kazuo_expressions\kazuo_general_05_neutral.png
call :generate s10_03 ichiko ichiko_expressions\ichiko_05_neutral.png
call :generate s10_04 kazuo kazuo_expressions\kazuo_general_05_neutral.png
call :generate s10_05 ichiko ichiko_expressions\ichiko_05_neutral.png
call :generate s10_06 kazuo kazuo_expressions\kazuo_general_05_neutral.png
call :generate s10_07 ichiko ichiko_expressions\ichiko_05_neutral.png
call :generate s10_08 kazuo kazuo_expressions\kazuo_general_05_neutral.png

REM シーン11
call :generate s11_01 yamada yamada_expressions\yamada_05_neutral.png
call :generate s11_02 kazuo kazuo_expressions\kazuo_general_05_neutral.png
call :generate s11_03 yamada yamada_expressions\yamada_05_neutral.png
call :generate s11_04 yamada yamada_expressions\yamada_05_neutral.png
call :generate s11_05 kazuo kazuo_expressions\kazuo_general_05_neutral.png
call :generate s11_06 yamada yamada_expressions\yamada_05_neutral.png
call :generate s11_07 ichiko ichiko_expressions\ichiko_05_neutral.png
call :generate s11_08 yamada yamada_expressions\yamada_05_neutral.png
call :generate s11_09 ichiko ichiko_expressions\ichiko_05_neutral.png

echo.
echo ============================================================
echo 完了
echo ============================================================
echo 成功: %SUCCESS%
echo 失敗: %FAIL%
echo 出力先: %OUTPUT_DIR%
echo ============================================================

pause
exit /b

:generate
set CUT_ID=%1
set CHARACTER=%2
set IMAGE_PATH=%3

echo [%CUT_ID%_%CHARACTER%] 処理中...

REM 既存チェック
if exist "%OUTPUT_DIR%\%CUT_ID%_%CHARACTER%.mp4" (
    echo   [SKIP] 既に存在します
    set /a SUCCESS+=1
    exit /b
)

REM 生成
python inference.py ^
  --driven_audio "%DATA_DIR%audio\%CUT_ID%.mp3" ^
  --source_image "%DATA_DIR%characters\%IMAGE_PATH%" ^
  --result_dir "%OUTPUT_DIR%" ^
  --still --preprocess full

if %errorlevel% equ 0 (
    echo   [OK] 完了
    set /a SUCCESS+=1
) else (
    echo   [FAIL] 失敗
    set /a FAIL+=1
)

exit /b
