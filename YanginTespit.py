
# Gerekli kutuphaneler

from email.mime.text import MIMEText # e-posta yazilarini gondermek/duzenlemek icin
from email.mime.image import MIMEImage # e-posta ile fotograf gondermek/duzenlemek icin
from email.mime.multipart import MIMEMultipart # e-posta icerigini duzenlemek icin
import cv2 # goruntu isleme ile ilgili fonksiyonlari kullanabilmek icin gereklidir
import smtplib # alan tespit edildiginde ilgili ksisye mail gondermek icin gerekli
import time # cihazin daha kesin tespit yapabilmesi icin videoyu ya da canli goruntuyu bir miktar yavaslatir
import requests # internetten ip kullanarak veri cekmek icin kullanilir
import pyodbc # bulunan konumu veritabanina kaydetmek icin kullanilir


class Konum_Tespit:
    def __init__(self):
        pass  # İleride kullanılabilir diye boş bir __init__ metodu ekledik.

    def konum(self):
        try:
            res = requests.get('https://ipinfo.io/')
            data = res.json()
            print(data)
            return data
        except Exception as e:
            print(f"Konum bilgisi alınırken hata oluştu: {e}")
            return None

class Mail_Gonder:
    def __init__(self, email_address, password, to_email_address):
        self.email_address = email_address
        self.password = password
        self.to_email_address = to_email_address

    def konumuGetir(self):
        location_getter = Konum_Tespit()
        return location_getter.konum()

    def Bilgileri_Gonder(self):
        msg = MIMEMultipart()
        msg['From'] = self.email_address
        msg['To'] = self.to_email_address
        msg['Subject'] = "Konu: Alan tespit edilmistir."

        body = f"fotoğraf ektedir : Konum : {self.konumuGetir()}"
        msg.attach(MIMEText(body, 'plain'))

        attachment = open('tespit_edilen_goruntu.jpg', 'rb')
        image = MIMEImage(attachment.read())
        attachment.close()
        msg.attach(image)

        try:
            server = smtplib.SMTP("smtp-mail.outlook.com", 587)
            server.starttls()
            server.login(self.email_address, self.password)
            text = msg.as_string()
            server.sendmail(self.email_address, self.to_email_address, text)
            print("E-posta gönderildi!")
            server.quit()
        except Exception as e:
            print(f"Hata oluştu: {e}")

# Örnek Kullanım

class Tespit:
    def __init__(self):
        self.path = 'cascade.xml'
        self.cameraNo = 0
        self.objectName = 'Yangin'
        self.frameWidth = 1280
        self.frameHeight = 720
        self.color = (255, 0, 255)
        self.tespit_count = 0

        self.cap = cv2.VideoCapture(self.cameraNo)
        self.cap.set(3, self.frameWidth)
        self.cap.set(4, self.frameHeight)

        cv2.namedWindow("Result")
        cv2.resizeWindow("Result", self.frameWidth, self.frameHeight + 100)
        cv2.createTrackbar("Scale", "Result", 993, 1000, self.empty)
        cv2.createTrackbar("Neig", "Result", 37, 50, self.empty)
        cv2.createTrackbar("Min Area", "Result", 40000, 100000, self.empty)
        cv2.createTrackbar("Brightness", "Result", 102, 255, self.empty)

        self.cascade = cv2.CascadeClassifier(self.path)

    def empty(self, a):
        pass
    def Durum_Tespit(self):
        while True:
            cameraBrightness = cv2.getTrackbarPos("Brightness", "Result")
            self.cap.set(10, cameraBrightness)
            success, img = self.cap.read()
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            scaleVal = 1 + (cv2.getTrackbarPos("Scale", "Result") / 1000)
            neig = cv2.getTrackbarPos("Neig", "Result")
            objects = self.cascade.detectMultiScale(gray, scaleVal, neig)

            for (x, y, w, h) in objects:
                area = w * h
                minArea = cv2.getTrackbarPos("Min Area", "Result")
                if area > minArea:
                    cv2.rectangle(img, (x, y), (x + w, y + h), self.color, 3)
                    cv2.putText(img, self.objectName, (x, y - 5), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, self.color, 2)
                    roi_color = img[y:y + h, x:x + w]
                    self.tespit_count += 1
                    print(" ALAN TESPIT EDILDI !!", self.tespit_count)

            if self.tespit_count >= 100:
                cv2.imwrite("tespit_edilen_goruntu.jpg", img)
                gonder = Mail_Gonder("gonderen mail", "sifre", "alici mail")
                gonder.Bilgileri_Gonder()
                loc = Konum_Tespit()
                result_string = ", ".join(loc.konum().values())
                break

            cv2.imshow("Result", img)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

if __name__ == "__main__":
    Baslat = Tespit()
    Baslat.Durum_Tespit()
cv2.destroyAllWindows() 