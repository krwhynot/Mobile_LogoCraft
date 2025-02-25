@echo off
echo Mobile LogoCraft CraveKit Background Removal Tests
echo ================================================
echo.

set PROJECT_ROOT=R:\Projects\Python\Mobile_LogoCraft

cd %PROJECT_ROOT%

echo Checking for CarveKit installation...
python -c "import carvekit" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo CarveKit is not installed. Would you like to install it now? (Y/N)
    set /p INSTALL_CARVEKIT=
    if /i "%INSTALL_CARVEKIT%"=="Y" (
        echo Installing CarveKit...
        pip install carvekit --extra-index-url https://download.pytorch.org/whl/cpu
    ) else (
        echo CarveKit is required for these tests. Exiting.
        exit /b 1
    )
)

echo Checking CUDA availability...
python -c "import torch; print('CUDA available' if torch.cuda.is_available() else 'CPU only')"

echo.
echo Select test mode:
echo 1. Run with Tracer B7 model only (fastest)
echo 2. Run with U^2-Net model only (best for hair)
echo 3. Run with all models (comprehensive)
echo.

set /p TEST_MODE=Enter selection (1-3): 

if "%TEST_MODE%"=="1" (
    echo.
    echo Running tests with Tracer B7 model...
    python tests\test_only_cravekit.py --models tracer_b7
) else if "%TEST_MODE%"=="2" (
    echo.
    echo Running tests with U^2-Net model...
    python tests\test_only_cravekit.py --models u2net
) else if "%TEST_MODE%"=="3" (
    echo.
    echo Running tests with all models (this may take a while)...
    python tests\test_only_cravekit.py --models all
) else (
    echo.
    echo Invalid selection. Running with default (Tracer B7)...
    python tests\test_only_cravekit.py --models tracer_b7
)

if %ERRORLEVEL% NEQ 0 (
    echo Error: CraveKit tests failed.
    exit /b 1
)

echo.
echo Tests completed successfully.
echo Results are available in tests\assets\output\cravekit_only\
echo Check the generated report file: tests\assets\output\cravekit_only\cravekit_results.md
echo.

pause
exit /b 0
