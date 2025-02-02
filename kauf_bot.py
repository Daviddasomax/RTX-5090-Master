import os
import time
import logging
import subprocess
import requests
import tarfile
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager

# 📌 Temporäre Verzeichnisse für Firefox & glibc
firefox_dir = "/tmp/firefox"
firefox_binary = os.path.join(firefox_dir, "firefox")
glibc_dir = "/tmp/glibc"

# 📌 Falls Firefox noch nicht vorhanden ist, herunterladen und entpacken
if not os.path.exists(firefox_binary):
    print("🔽 Lade portable Firefox-Version herunter...")

    # 🔽 Lade eine GLIBC-kompatible Firefox-Version herunter (keine Standard-Version)
    firefox_url = "https://ftp.mozilla.org/pub/firefox/releases/122.0/linux-x86_64/en-US/firefox-122.0.tar.bz2"
    response = requests.get(firefox_url, allow_redirects=True)

    # 🔽 Speichere die Datei manuell
    archive_path = "/tmp/firefox.tar.bz2"
    with open(archive_path, "wb") as file:
        file.write(response.content)

    # 🔽 Stelle sicher, dass das Zielverzeichnis existiert
    os.makedirs(firefox_dir, exist_ok=True)

    # 🔽 Entpacke Firefox mit `tarfile`
    with tarfile.open(archive_path, "r:bz2") as tar:
        tar.extractall(path=firefox_dir)

    # 🔽 Suche nach der richtigen ausführbaren Firefox-Datei
    for root, dirs, files in os.walk(firefox_dir):
        if "firefox" in files:
            firefox_binary = os.path.join(root, "firefox")
            break

    # 🔽 Setze Firefox als ausführbar (WICHTIG für Railway)
    subprocess.run(["chmod", "+x", firefox_binary], check=True)

    # 🔽 Überprüfe, ob die Datei existiert & ausführbar ist
    if not os.path.exists(firefox_binary):
        raise FileNotFoundError(f"❌ Firefox-Binary nicht gefunden in {firefox_binary}")
    if not os.access(firefox_binary, os.X_OK):
        raise PermissionError(f"❌ Firefox ist nicht ausführbar! `chmod +x {firefox_binary}` fehlgeschlagen!")

# 📌 Falls GLIBC fehlt, lade sie herunter
if not os.path.exists(glibc_dir):
    print("🔽 Lade portable GLIBC-Version herunter...")

    # 🔽 Lade GLIBC 2.38 herunter
    glibc_url = "https://ftp.gnu.org/gnu/libc/glibc-2.38.tar.gz"
    response = requests.get(glibc_url, allow_redirects=True)

    # 🔽 Speichere die Datei manuell
    glibc_archive = "/tmp/glibc.tar.gz"
    with open(glibc_archive, "wb") as file:
        file.write(response.content)

    # 🔽 Stelle sicher, dass das Zielverzeichnis existiert
    os.makedirs(glibc_dir, exist_ok=True)

    # 🔽 Entpacke GLIBC mit `tarfile`
    with tarfile.open(glibc_archive, "r:gz") as tar:
        tar.extractall(path=glibc_dir)

# 🚀 Setze den `LD_LIBRARY_PATH`, um die richtige `glibc`-Version zu verwenden
os.environ["LD_LIBRARY_PATH"] = f"{glibc_dir}/lib"

# 🚀 Prüfe, ob Firefox korrekt installiert ist
firefox_version = subprocess.run([firefox_binary, "--version"], capture_output=True, text=True).stdout.strip()
logging.info(f"🔥 Installierte Firefox-Version: {firefox_version}")

# 🚀 Logging aktivieren
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# 🚀 Firefox-Setup mit Geckodriver
options = webdriver.FirefoxOptions()
options.binary_location = firefox_binary  # Setzt den Pfad zur richtigen Firefox-Binärdatei
options.add_argument("--headless")  # Kein GUI-Modus für Railway
options.add_argument("--no-sandbox")
options.add_argument("--disable-gpu")

# WebDriver initialisieren
service = Service(GeckoDriverManager().install())

try:
    driver = webdriver.Firefox(service=service, options=options)
    logging.info(f"🚀 Selenium WebDriver mit Firefox gestartet! (Pfad: {firefox_binary})")

    # 🚀 Testseite laden
    driver.get("https://www.google.com")
    print("🌍 Google erfolgreich geladen!")
except Exception as e:
    logging.error(f"❌ Fehler beim Starten von Firefox: {e}")
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
