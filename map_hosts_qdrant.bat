@echo off
:: HBOS: Lanzador elevado para mapeo hosts
powershell -Command "Start-Process powershell -ArgumentList '-NoProfile -ExecutionPolicy Bypass -File \"%~dp0map_hosts_qdrant.ps1\"' -Verb RunAs"
