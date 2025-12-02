#!/bin/bash
# NFC Copy & Emulate Tool для Termux (2025)
# Работает без root на Android 10+

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}╔══════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║     NFC Card Cloner + Emulator (2025)    ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════╝${NC}"

# Проверяем, включён ли NFC
if ! termux-nfc -i > /dev/null 2>&1; then
    echo -e "${RED}[✗] NFC выключен или не поддерживается${NC}"
    echo "Включи NFC в настройках и запусти снова"
    exit 1
fi

echo -e "${YELLOW}[*] Выбери действие:${NC}"
echo "1) Считать и сохранить карту (дамп)"
echo "2) Эмулировать сохранённую карту"
echo "3) Список всех сохранённых карт"
read -p "→ " choice

case $choice in
    1)
        read -p "Введи название карты (например: troika, office, gym): " cardname
        filename="$cardname-$(date +%Y%m%d-%H%M).dump"

        echo -e "${YELLOW}[*] Приложи карту к телефону и не убирай 10–15 сек...${NC}"
        echo -e "${YELLOW}[*] Идёт полное считывание (Mifare Classic 1K/4K, DESFire, Ultralight)${NC}"

        # Универсальное считывание через libnfc + nfcpy (работает с большинством карт)
        python3 - <<PYTHON
import nfc
import binascii
import os
from datetime import datetime

def on_connect(tag):
    print("[+] Карта обнаружена:", tag)
    dump = tag.dump()
    uid = binascii.hexlify(tag.identifier).decode()
    cardtype = str(tag)
    
    filename = "$filename"
    with open("/sdcard/NFC-Dumps/" + filename, "w") as f:
        f.write(f"# NFC Dump {datetime.now()}\n")
        f.write(f"# UID: {uid.upper()}\n")
        f.write(f"# Type: {cardtype}\n")
        f.write("# Data:\n")
        for line in dump:
            f.write("".join(line) + "\n")
    
    print(f"[√] Дамп сохранён: /sdcard/NFC-Dumps/{filename}")
    print(f"[√] UID: {uid.upper()}")
    return True

clf = nfc.ContactlessFrontend('android')
if clf.connect(rdwr={'on-connect': on_connect}):
    clf.close()
PYTHON

        echo -e "${GREEN}[√] Готово! Дамп лежит в /sdcard/NFC-Dumps/$filename${NC}"
        ;;

    2)
        echo -e "${YELLOW}[*] Список доступных карт для эмуляции:${NC}"
        ls -1 /sdcard/NFC-Dumps/*.dump 2>/dev/null | xargs -n1 basename
        read -p "Введи имя файла (без пути): " emulatefile

        if [[ ! -f "/sdcard/NFC-Dumps/$emulatefile" ]]; then
            echo -e "${RED}[✗] Файл не найден!${NC}"
            exit 1
        fi

        echo -e "${YELLOW}[!] ВКЛЮЧАЕТСЯ ЭМУЛЯЦИЯ КАРТЫ${NC}"
        echo -e "${YELLOW}[!] Приложи телефон к терминалу спиной (где NFC)${NC}"
        echo -e "${YELLOW}[!] Для остановки нажми Ctrl+C${NC}"
        sleep 3

        # Эмуляция через встроенный HCE (Host Card Emulation) Android
        termux-nfc -t nfc_a -d "$(cat "/sdcard/NFC-Dumps/$emulatefile" | grep -v '^#' | tr -d '\n ')"
        echo -e "${GREEN}[√] Эмуляция завершена${NC}"
        ;;

    3)
        echo -e "${YELLOW}Сохранённые карты:${NC}"
        ls -lh /sdcard/NFC-Dumps/ | grep dump
        ;;

    *)
        echo -e "${RED}Неверный выбор${NC}"
        ;;
esac

echo -e "${GREEN}Готово! Подписывайся на обновления: t.me/termuxhacking${NC}"
