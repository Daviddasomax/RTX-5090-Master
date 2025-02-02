import os
import time
import logging
import subprocess
import requests
import shutil
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# 📌 Temporäre Verzeichnisse für Chromium
chromium_dir = "/tmp/chromium"
chromium_binary = os.path.join(chromium_dir, "chrome-linux64", "chrome")

# 📌 Falls Chromium noch nicht vorhanden ist, herunterladen und entpacken
if not os.path.exists(chromium_binary):
    print("🔽 Lade portable Chromium-Version herunter (Railway-kompatibel)...")

    chromium_url = "https://storage.googleapis.com/chrome-for-testing-public/122.0.6261.94/linux64/chrome-linux.zip"
    archive_path = "/tmp/chrome-linux.zip"

    # Lade Chromium von Google herunter
    response = requests.get(chromium_url, allow_redirects=True)
    with open(archive_path, "wb") as file:
        file.write(response.content)

    os.makedirs(chromium_dir, exist_ok=True)

    # 📌 Verwende `shutil` anstelle von `unzip`
    shutil.unpack_archive(archive_path, chromium_dir)

    # 📌 Setze Chromium als ausführbar
    subprocess.run(["chmod", "+x", chromium_binary], check=True)

    if not os.path.exists(chromium_binary):
        raise FileNotFoundError(f"❌ Chromium-Binary nicht gefunden in {chromium_binary}")
    if not os.access(chromium_binary, os.X_OK):
        raise PermissionError(f"❌ Chromium ist nicht ausführbar! `chmod +x {chromium_binary}` fehlgeschlagen!")

# 🚀 Prüfe, ob Chromium korrekt installiert ist
chromium_version = subprocess.run([chromium_binary, "--version"], capture_output=True, text=True).stdout.strip()
logging.info(f"🔥 Installierte Chromium-Version: {chromium_version}")

# 🚀 Logging aktivieren
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# 🚀 Chromium-Setup mit Selenium
options = webdriver.ChromeOptions()
options.binary_location = chromium_binary  # Setzt den Pfad zur richtigen Chromium-Binärdatei
options.add_argument("--headless")  # Kein GUI-Modus für Railway
options.add_argument("--no-sandbox")
options.add_argument("--disable-gpu")

# WebDriver initialisieren
service = Service(ChromeDriverManager().install())

try:
    driver = webdriver.Chrome(service=service, options=options)
    logging.info(f"🚀 Selenium WebDriver mit Chromium gestartet! (Pfad: {chromium_binary})")

    # 🚀 Testseite laden
    driver.get("https://www.google.com")
    print("🌍 Google erfolgreich geladen!")
except Exception as e:
    logging.error(f"❌ Fehler beim Starten von Chromium: {e}")
    raise e




# 🚀 RTX 5090 Produktlinks für verschiedene Shops
SHOPS = {
    "Caseking": "https://www.caseking.de/pc-komponenten/grafikkarten/nvidia/rtx-5000/geforce-rtx-5090",
    "Proshop": "https://www.proshop.at/Grafikkarte/GIGABYTE-GeForce-RTX-5090-AORUS-Master-32GB-GDDR7-RAM-Grafikkarte/3331130",
    "Alternate": "https://www.alternate.de/GIGABYTE/GeForce-RTX-5090-AORUS-MASTER-ICE-32G-Grafikkarte/html/product/100108931",
    "Alza": "https://www.alza.at/gigabyte-aorus-geforce-rtx-5090-master-32g-d12783426.htm?o=1"
}

# 🚀 Zugangsdaten aus Render-Umgebungsvariablen
USER_EMAIL = os.getenv("USER_EMAIL")
USER_PASSWORD = os.getenv("USER_PASSWORD")
PAYPAL_EMAIL = os.getenv("PAYPAL_EMAIL")
PAYPAL_PASSWORD = os.getenv("PAYPAL_PASSWORD")

if not USER_EMAIL or not USER_PASSWORD or not PAYPAL_EMAIL or not PAYPAL_PASSWORD:
    logging.error("❌ ERROR: Login-Daten fehlen! Setze 'USER_EMAIL', 'USER_PASSWORD', 'PAYPAL_EMAIL' und 'PAYPAL_PASSWORD'.")
    exit(1)

def check_and_buy():
    """
    Prüft alle RTX 5090 Shops & kauft automatisch, falls verfügbar.
    """
    for shop, url in SHOPS.items():
        logging.info(f"🔍 Prüfe Verfügbarkeit bei {shop}...")
        driver.get(url)

        try:
            # Warten, bis der "In den Warenkorb"-Button erscheint
            add_to_cart = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'In den Warenkorb') or contains(text(), 'Add to cart')]"))
            )
            add_to_cart.click()
            logging.info(f"✅ {shop}: RTX 5090 in den Warenkorb gelegt!")

            # Weiter zur Kasse
            if shop == "Caseking":
                driver.get("https://www.caseking.de/checkout/cart")
            elif shop == "Proshop":
                driver.get("https://www.proshop.at/cart")
            elif shop == "Alternate":
                driver.get("https://www.alternate.de/cart")
            elif shop == "Alza":
                driver.get("https://www.alza.at/Order1.htm")

            # Login-Prozess
            email_field = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "email")))
            password_field = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "password")))

            email_field.send_keys(USER_EMAIL)
            password_field.send_keys(USER_PASSWORD)
            password_field.send_keys(Keys.RETURN)

            # Zahlung per PayPal durchführen
            if shop in ["Caseking", "Proshop", "Alternate", "Alza"]:
                pay_with_paypal()

            # Bestellung abschließen
            confirm_order = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Bestellung abschicken') or contains(text(), 'Place order')]"))
            )
            confirm_order.click()
            logging.info(f"🎉 RTX 5090 wurde erfolgreich bei {shop} gekauft!")
            return True

        except Exception as e:
            logging.warning(f"❌ {shop}: Noch nicht verfügbar ({e})")

    return False

def pay_with_paypal():
    """
    Wechselt in das PayPal-Fenster, loggt sich ein und bestätigt die Zahlung.
    """
    try:
        # Warten, bis das PayPal-Fenster geöffnet wird
        WebDriverWait(driver, 10).until(EC.number_of_windows_to_be(2))
        paypal_window = driver.window_handles[1]  # PayPal-Popup ist das zweite Fenster
        driver.switch_to.window(paypal_window)

        logging.info("✅ Wechsel zum PayPal-Popup erfolgreich!")

        # PayPal-Login
        email_field = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "email")))
        email_field.send_keys(PAYPAL_EMAIL)
        email_field.send_keys(Keys.RETURN)

        password_field = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "password")))
        password_field.send_keys(PAYPAL_PASSWORD)
        password_field.send_keys(Keys.RETURN)

        logging.info("✅ PayPal-Login erfolgreich!")

        # Zahlung bestätigen
        pay_now_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Jetzt bezahlen')]"))
        )
        pay_now_button.click()
        
        logging.info("🎉 PayPal-Zahlung erfolgreich!")

        # Zurück zum Hauptfenster wechseln
        driver.switch_to.window(driver.window_handles[0])

    except Exception as e:
        logging.error(f"❌ Fehler bei der PayPal-Zahlung: {e}")

# 🚀 Wiederholt den Check alle 5 Minuten, bis die RTX 5090 verfügbar ist.
while True:
    if check_and_buy():
        break
    logging.info("⏳ Warte 5 Minuten, bevor erneut geprüft wird...")
    time.sleep(300)  # Alle 5 Minuten erneut prüfen

driver.quit()
