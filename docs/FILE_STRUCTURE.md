# Project File Structure
├── .pytest_cache/
│   ├── v/
│   │   └── cache/
│   │       ├── lastfailed
│   │       ├── nodeids
│   │       └── stepwise
│   ├── .gitignore
│   ├── CACHEDIR.TAG
│   └── README.md
├── assets/
│   └── icons/
│       └── HungerRush_Icon.ico
├── deployment/
│   ├── build/
│   │   └── LogoCraft/
│   │       ├── localpycs/
│   │       │   ├── pyimod01_archive.pyc
│   │       │   ├── pyimod02_importers.pyc
│   │       │   ├── pyimod03_ctypes.pyc
│   │       │   ├── pyimod04_pywin32.pyc
│   │       │   └── struct.pyc
│   │       ├── Analysis-00.toc
│   │       ├── base_library.zip
│   │       ├── EXE-00.toc
│   │       ├── Mobile_LogoCraft.pkg
│   │       ├── PKG-00.toc
│   │       ├── PYZ-00.pyz
│   │       ├── PYZ-00.toc
│   │       ├── warn-LogoCraft.txt
│   │       └── xref-LogoCraft.html
│   ├── dist/
│   │   └── Mobile_LogoCraft.exe
│   ├── logs/
│   │   └── app.log
│   ├── build.py
│   ├── build_app.ps1
│   ├── BUILD_NOTES.md
│   ├── disable_logging_hook.py
│   ├── file_version_info.txt
│   ├── LogoCraft.spec
│   └── setup.py
├── docs/
│   ├── FILE_STRUCTURE.md
│   ├── README_background_removal.md
│   └── TECHNICAL_REFERENCE.md
├── resources/
├── src/
│   ├── config/
│   │   ├── formats.py
│   │   └── __init__.py
│   ├── controllers/
│   ├── core/
│   │   ├── error_handler.py
│   │   └── __init__.py
│   ├── models/
│   │   ├── background_remover.py
│   │   ├── base.py
│   │   ├── image_processor.py
│   │   ├── push_processor.py
│   │   └── __init__.py
│   ├── services/
│   │   ├── image_processing_service.py
│   │   └── __init__.py
│   ├── ui/
│   │   ├── components/
│   │   │   ├── background_removal_option.py
│   │   │   ├── drop_zone.py
│   │   │   ├── file_section.py
│   │   │   ├── format_selector.py
│   │   │   ├── image_preview.py
│   │   │   ├── message_dialogs.py
│   │   │   ├── progress_indicator.py
│   │   │   └── __init__.py
│   │   ├── theme/
│   │   │   ├── colors.py
│   │   │   └── __init__.py
│   │   ├── main_window.py
│   │   └── __init__.py
│   ├── utils/
│   │   ├── logging.py
│   │   ├── worker.py
│   │   └── __init__.py
│   ├── main.py
│   └── __init__.py
├── tests/
│   ├── assets/
│   │   ├── output/
│   │   │   └── background_removal_analysis_summary.txt
│   │   ├── test_images/
│   │   │   ├── HHLogo.png
│   │   │   ├── kitchen.jpg
│   │   │   ├── ProcessedLOGO.PNG
│   │   │   ├── redrooster.jpg
│   │   │   ├── redrooster.png
│   │   │   ├── snaps.png
│   │   │   └── Starbucks.jpg
│   │   └── test_results/
│   │       ├── HHLogo_nobg.png
│   │       ├── kitchen_nobg.jpg
│   │       ├── ProcessedLOGO_nobg.PNG
│   │       ├── redrooster_nobg.jpg
│   │       ├── redrooster_nobg.png
│   │       ├── snaps_nobg.png
│   │       └── Starbucks_nobg.jpg
│   ├── conftest.py
│   ├── logo_background_test.py
│   ├── test_background_removal.py
│   ├── test_gui.py
│   ├── test_image_processor.py
│   ├── test_integration.py
│   ├── test_push_icon.py
│   ├── verify_output.py
│   └── __init__.py
├── .gitignore
├── build.bat
├── build_direct.bat
├── build_simple.bat
├── cleanup_logs.ps1
├── README.md
├── requirements.txt
└── run.py
