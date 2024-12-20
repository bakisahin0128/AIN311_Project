import os
import time
import csv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException


def start_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-notifications")
    # options.add_argument("--headless")  # Gerekirse etkinleştirilebilir
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver


def check_and_accept_popup(driver):
    try:
        wait = WebDriverWait(driver, 5)  # Popup için biraz daha uzun bekleme süresi
        iframe = wait.until(
            EC.presence_of_element_located((By.XPATH, "//iframe[contains(@src, 'privacy-mgmt.com')]"))
        )
        driver.switch_to.frame(iframe)
        accept_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[text()='Kabul et']"))
        )
        accept_button.click()
        driver.switch_to.default_content()
        print("Popup bulundu ve kabul edildi.")
    except TimeoutException:
        # Popup yok
        pass
    except NoSuchElementException:
        # Popup yok
        pass
    except Exception as e:
        print(f"Popup kontrolü sırasında hata oluştu: {e}")


def set_zoom(driver, zoom_level):
    driver.execute_script(f"document.body.style.zoom='{zoom_level}%'")
    time.sleep(1)  # Zoom işleminin tamamlanması için kısa bir bekleme


def scroll_down(driver, scroll_amount):
    driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
    time.sleep(1)  # Scroll işleminin tamamlanması için kısa bir bekleme


def extract_table_data(driver):
    wait = WebDriverWait(driver, 20)
    all_data = []  # Tüm sayfalardan toplanan veriler

    while True:
        try:
            # Tabloyu bekleyin ki yüklenmiş olsun
            tbody = wait.until(
                EC.presence_of_element_located(
                    (By.XPATH, '/html/body/div[1]/main/div[1]/div/div/div[3]/div/table/tbody'))
            )
            print("Tablo bulundu.")

            # Tablonun tüm satırlarını al
            rows = tbody.find_elements(By.XPATH, ".//tr")
            total_rows = len(rows)
            print(f"Toplam {total_rows} satır bulundu.")

            data = []

            for index in range(total_rows):
                try:
                    row = rows[index]

                    # Oyuncu İsmi
                    player_name_xpath = "./td[1]/table/tbody/tr[1]/td[2]/a"
                    player_name_element = row.find_element(By.XPATH, player_name_xpath)
                    player_name = player_name_element.text.strip()

                    # Oyuncu Takımı
                    player_team_xpath = "./td[2]/a/img"
                    try:
                        team_img = row.find_element(By.XPATH, player_team_xpath)
                        # 'alt' özniteliğinden takım ismini alıyoruz
                        team_name = team_img.get_attribute("alt")
                        if team_name:
                            team_name = team_name.strip()
                        else:
                            team_name = "Bilinmiyor"
                    except NoSuchElementException:
                        team_name = "Bilinmiyor"

                    # Piyasa Değeri
                    player_market_value_xpath = "./td[3]"
                    player_market_value_element = row.find_element(By.XPATH, player_market_value_xpath)
                    player_market_value = player_market_value_element.text.strip()

                    # Oyuncu Yaşı
                    player_age_xpath = "./td[7]"
                    player_age_element = row.find_element(By.XPATH, player_age_xpath)
                    player_age = player_age_element.text.strip()

                    data.append({
                        "Oyuncu İsmi": player_name,
                        "Yaşı": player_age,
                        "Takımı": team_name,
                        "Piyasa Değeri": player_market_value
                    })

                    print(
                        f"{index + 1}. Oyuncu: {player_name}, Yaşı: {player_age}, Takımı: {team_name}, Piyasa Değeri: {player_market_value}"
                    )

                except NoSuchElementException as e:
                    continue
                except Exception as e:
                    print(f"Satır işlenirken bir hata oluştu:")
                    continue

            all_data.extend(data)  # Sayfadaki verileri genel listeye ekle

            # Şimdi, sonraki sayfaya geçip geçemeyeceğimizi kontrol edelim
            try:
                # "Sonraki" butonunu title özniteliğine göre buluyoruz
                next_page_xpath = '//*[@id="yw1"]/div[2]/ul//a[@title="Sonraki sayfaya git"]'
                next_button = wait.until(
                    EC.presence_of_element_located((By.XPATH, next_page_xpath))
                )

                # "Sonraki" butonunun etkin olup olmadığını kontrol edin
                if "disabled" in next_button.get_attribute("class"):
                    print("Sonraki sayfa butonu devre dışı, veri çekme işlemi tamamlandı.")
                    break  # Döngüyü sonlandır
                else:
                    # Butonun tıklanabilir olmasını bekleyin
                    wait.until(EC.element_to_be_clickable((By.XPATH, next_page_xpath)))

                    # Butonu görünür alana kaydırın
                    driver.execute_script("arguments[0].scrollIntoView({ behavior: 'smooth', block: 'nearest' });",
                                          next_button)
                    time.sleep(1)  # Kaydırma için bekleme
                    next_button.click()
                    print("Sonraki sayfa butonuna tıklandı.")
                    time.sleep(2)  # Yeni sayfanın yüklenmesi için bekleme
            except TimeoutException:
                print("Sonraki sayfa butonu bulunamadı veya yüklenmedi, veri çekme işlemi tamamlandı.")
                break  # Döngüyü sonlandır
            except ElementClickInterceptedException:
                print("Sonraki sayfa butonuna tıklanamadı, veri çekme işlemi tamamlandı.")
                break  # Döngüyü sonlandır
            except Exception as e:
                print(f"Sonraki sayfaya geçişte bir hata oluştu: {e}")
                break  # Döngüyü sonlandır

        except TimeoutException:
            print("Tablo bulunamadı veya yüklenmedi.")
            break  # Döngüyü sonlandır
        except Exception as e:
            print(f"Veri çekilirken bir hata oluştu: {e}")
            break  # Döngüyü sonlandır

    # Verileri CSV dosyasına kaydedin
    try:
        # Belirtilen dosya yolunu tanımlayın
        output_dir = r'C:\Users\mbaki\Desktop\Proje\data\raw\23_24'
        # Klasörün var olup olmadığını kontrol edin ve yoksa oluşturun
        os.makedirs(output_dir, exist_ok=True)
        # Tam dosya yolunu oluşturun
        output_file = os.path.join(output_dir, 'oyuncu_verileri.csv')

        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ["Oyuncu İsmi", "Yaşı", "Takımı", "Piyasa Değeri"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for row_data in all_data:
                writer.writerow(row_data)

        print(f"Veriler '{output_file}' dosyasına kaydedildi.")
    except Exception as e:
        print(f"Verileri CSV dosyasına kaydederken bir hata oluştu: {e}")


def transfermarkt_scraper():
    driver = start_driver()

    # Hedef URL'yi burada belirtin
    # Örneğin, Ligler sayfası: "https://www.transfermarkt.com.tr/liga/liga-name/lig-id"
    # Oyuncular sayfası: "https://www.transfermarkt.com.tr/liga/liga-name/lig-id/spieler"

    # Örnek hedef URL (kendi ihtiyacınıza göre değiştirin)
    target_url = "https://www.transfermarkt.com.tr/super-lig/marktwertaenderungen/wettbewerb/TR1/pos//detailpos/0/verein_id/0/land_id/0/plus/1"  # Bu sadece bir örnektir

    driver.get(target_url)
    print(f"{target_url} adresine erişildi.")

    try:
        time.sleep(3)  # Sayfanın tamamen yüklenmesi için bekleme süresini artırabilirsiniz
        check_and_accept_popup(driver)
        print("'Kabul et' butonu kontrol edildi ve gerekiyorsa tıklandı.")

        set_zoom(driver, 40)
        print("Sayfa %40 oranında küçültüldü.")

        scroll_down(driver, 350)  # İstediğiniz miktarda aşağı kaydırın
        print("Sayfa 350 piksel aşağı kaydırıldı.")

        extract_table_data(driver)  # Maksimum satır sınırı kaldırıldı
        print("Tablo verileri başarıyla alındı.")

    except TimeoutException as e:
        print(f"Zaman aşımı hatası: {e}")
    except NoSuchElementException as e:
        print(f"Element bulunamadı: {e}")
    except Exception as e:
        print(f"Hata oluştu: {e}")
    finally:
        input("İşlem tamamlandı. Tarayıcıyı kapatmak için Enter'a basın...")
        driver.quit()


if __name__ == "__main__":
    transfermarkt_scraper()
