@echo off
color 0a
title AI friend - python requirements
chcp 65001 > nul
pip install ollama requests beautifulsoup4 wikipedia search-web websearch-python rich
echo --------------------------------------------
echo  Всё установлено! Если не вылезла ошибка...
echo --------------------------------------------
pause