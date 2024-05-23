import concurrent.futures
import os;os.system("cls")
import chompjs
import string
import json
import time
import requests as rr
import random
import tls_client
from colorama import Fore,Style;blue = Fore.BLUE;red = Fore.RED;warn = Fore.YELLOW;green = Fore.GREEN;gray = Fore.LIGHTBLACK_EX;white_red = Fore.LIGHTRED_EX;white_green = Fore.LIGHTGREEN_EX;white_warn = Fore.LIGHTYELLOW_EX;white_blue = Fore.LIGHTBLUE_EX;reset_colors = Style.RESET_ALL; pink = Fore.MAGENTA
from datetime import datetime
settings = json.loads(open("settings.json").read())
proxies = open("proxies.txt").read().splitlines()
generated = 0
failed = 0
ok = [200, 201, 202, 203, 204]
class Console:
    def __init__(self,debug=False) -> None:
        self.debug = debug
    def error(self,x):
        x = str(x)
        if self.debug:
            print(f"{red}[- ERROR -]{reset_colors} - {gray}[{datetime.now().date()} - {datetime.now().now().strftime('%H:%M:%S')}]{reset_colors} |\t {white_red}{x}{reset_colors}")
        else:
            print(f"{red}[-]{reset_colors}\t {red}{x}{reset_colors}")
    def success(self,x):
        if self.debug:
            print(f"{green}[+ Success +]{reset_colors} - {gray}[{datetime.now().date()} - {datetime.now().now().strftime('%H:%M:%S')}]{reset_colors} |\t {white_green+x}{reset_colors}")
        else:
            print(f"{green}[+]{reset_colors}\t {white_green+x}{reset_colors}")
    def warn(self,x,t=0):
        if self.debug:
            print(f"{warn}[! {'WARNING' if t == 0 else 'FAILED'} !]{reset_colors} - {gray}[{datetime.now().date()} - {datetime.now().now().strftime('%H:%M:%S')}]{reset_colors} |\t {white_warn+x}{reset_colors}")
        else:
            print(f"{warn}[!]{reset_colors}\t {white_warn+x}{reset_colors}")
    def info(self,x):
        if self.debug:
            print(f"{blue}[* INFO *]{reset_colors} - {gray}[{datetime.now().date()} - {datetime.now().now().strftime('%H:%M:%S')}]{reset_colors} |\t {white_blue+x}{reset_colors}")
        else:
            print(f"{blue}[*]{reset_colors}\t {white_blue+x}{reset_colors}")
    def input(self, x):
        if self.debug:
            x = input(f"{blue}[| INPUT |]{reset_colors} - {gray}[{datetime.now().date()} - {datetime.now().now().strftime('%H:%M:%S')}]{reset_colors} |\t {white_blue+x}{reset_colors}{white_warn}")
        else:
            x = input(f"{blue}[|]{reset_colors}\t {white_blue+x}{reset_colors}{white_warn}")
        return x
console = Console(debug=True)

class MailTm:
    def __init__(self, password=None, username=None) -> None:
        self.headers={
            "accept":"application/ld+json",
            "Origin":"https://mail.tm",
            "Referer":"https://mail.tm/",
            "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
        self.password = password
        self.username = username
    def get_domain(self) -> str:
        domains = rr.get("https://api.mail.tm/domains",headers=self.headers)
        return random.choice(domains.json()["hydra:member"])["domain"]
    def create_email(self) -> dict:
        while True:
            domain = self.get_domain()
            if not self.username:
                username = self.generateUsername2()
            else:
                username = self.username
            if not self.password:
                password = self.generatePassword(username)
            else:
                password = self.password
            account = rr.post("https://api.mail.tm/accounts",headers=self.headers,json={"address":username+f"@{domain}","password": password})
            if "Internal Server Error" in account.text:
                password = ''.join([random.choice(string.ascii_letters + string.digits + "!.") for i in range(10)])
                account = rr.post("https://api.mail.tm/accounts",headers=self.headers,json={"address":username+f"@{domain}","password": password})
                break
            if "This value is already used." in account.text:
                username = f'{self.generateUsername()}'+''.join([random.choice(string.digits+string.ascii_lowercase) for i in range(10)])
                account = rr.post("https://api.mail.tm/accounts",headers=self.headers,json={"address":username+f"@{domain}","password": password})
                break
            if account.status_code in [201,200,203,202]:
                account = account.json()
                return account["address"], password, 
            else:
                return self.create_email()
    def generateUsername2(self):
        return f'{self.generateUsername()}'+''.join([random.choice(string.digits+string.ascii_lowercase) for i in range(3)])
    def generatePassword(self, username):
        return username+''.join([random.choice(string.ascii_letters + string.digits + "!$.") for i in range(10)])
    def get_token(self) -> str:
        try:
            headers = self.headers
            email, password  = self.create_email()
            token = rr.post("https://api.mail.tm/token",headers=self.headers,json={"address":email,"password":password}).json()["token"]
            headers.update({"authorization":f"Bearer {token}"})
            return (token, (email, password))
        except:
            return self.get_token()
    def get_messages(self, token) -> dict:
        headers = self.headers
        headers.update({"authorization":"Bearer "+token})
        messages = rr.get("https://api.mail.tm/messages",headers=headers)
        return (messages.json(), headers)
    def get_messages_items(self, token):
        messages, headers = self.get_messages(token)
        if "hydra:totalItems" in str(messages):
            items = messages["hydra:totalItems"]
            if items >= 1:
                return (True,messages, headers)
        if "hydra:totalItems" not in str(messages):
            return (True,messages, headers)
        else:
            return (False,messages, headers)
    def getMessages(self, token, interval=None) -> dict:
        if not interval:
            while True:
                try:
                    result, messages, headers = self.get_messages_items(token)
                    if result:
                        message =  messages["hydra:member"]
                        return message
                    time.sleep(1)
                except:
                    pass
        else:
            for i in range(interval):
                time.sleep(1)
                try:
                    result, messages, headers = self.get_messages_items(token)
                    if result:
                        message =  messages["hydra:member"]
                        return message
                except:
                    pass
    def getMessage(self, token, interval=None):
        emails = self.getMessages(token, interval)
        for inbox in emails:
            if "instagram" in inbox["subject"].lower():
                code = inbox["subject"].lower().split(" is your instagram code")[0]
                return code
    def get_message(self, messageId, headers=None, emailToken=None):
        if not headers:
            if emailToken:
                headers = self.headers
                headers.update({"authorization": f"Bearer {emailToken}"})
        message = rr.get(f"https://api.mail.tm/messages/{messageId}", headers=headers).json()["text"]
        return message
    def generateUsername(self):
        request = rr.get("https://randomuser.me/api/?inc=login")
        if request.status_code in [200,201,203,205,202,204]:
            js = request.json()
            username = js["results"][0]["login"]["username"]
            return username
        else:
            return ''.join([random.choice(string.ascii_lowercase) for x in range(10)])
    def createEmail(self):
        for i in range(3):
            try:
                token, account = self.get_token()
                email, password = account
                if token and account:
                    break
            except:
                pass
        account =  f"{email}:{password}"
        #console.success(f"Created email {account}")
        return (email, token)
class Kopeechka:
    def __init__(self) -> None:
        self.apikey = settings["email_key"]
        self.mails = self.getAvailableEmails()
        self.balance = int(self.getBalance())
        self.hotmailPrice, self.hotmailStock = self.getPrice("hotmail.com")
        self.outlookPrice, self.outlookStock = self.getPrice("outlook.com")
    def getBalance(self):
        request = rr.get(f"https://api.kopeechka.store/user-balance?token={self.apikey}&type=$TYPE&api=2.0").json()
        if request.get("status").lower() == "ok":
            return request.get("balance")
        return 0
    def getAvailableEmails(self):
        mails = rr.get("https://api.kopeechka.store/mailbox-zones?popular=1&site=$SITE").json().get("popular")
        return mails
    def getPrice(self, email):
        for mail in self.mails:
            if mail["name"] == email:
                return int(mail["cost"]), int(mail["count"])
        return 0, 0
    def createEmail(self):
        if self.balance < self.outlookPrice or self.balance < self.hotmailPrice:
            console.warn(f"Failed to buy email, insufficient balance {reset_colors}[{gray}Balance: {blue}{self.balance}{reset_colors}]")
            return None, None
        if self.hotmailStock > self.outlookStock or self.hotmailPrice < self.outlookPrice:
            mail = "hotmail.com"
        if self.outlookStock > self.hotmailStock or self.outlookPrice < self.hotmailPrice:
            mail = "outlook.com"
        self.balance -= self.hotmailPrice if mail == "hotmail.com" else self.outlookPrice
        if mail == "outlook.com":
            self.outlookStock -= 1
        else:
            self.hotmailStock -= 1
        request = rr.get(f"https://api.kopeechka.store/mailbox-get-email?api=2.0&spa=1&site=instagram.com&sender=instagram&regex=&mail_type=&token={self.apikey}&mail_type={mail}").json()
        return request.get("mail"), request.get("id")
    def getMessage(self, id):
        while True:
            time.sleep(5)
            request = rr.get(f"https://api.kopeechka.store/mailbox-get-message?full=1&spa=1&id={id}&token={self.apikey}").json()
            if request.get("status").lower() == "ok":
                self.deleteEmail(id)
                return request.get("value")
    def deleteEmail(self, id):
        return rr.get(f"https://api.kopeechka.store/mailbox-cancel?id={id}&token={self.apikey}").json().get("status")
    
    
         
    
class Email:
    def __init__(self, service) -> None:
        self.MailTM = MailTm()
        self.Kopeechka = Kopeechka()
        self.services = [("mailtm, ", 0), ("kopeechka", 1)]
        self.email = self.MailTM if service == "mailtm" else self.Kopeechka if service == "kopeechka" else exit(console.warn(f"These are the available email {reset_colors}[{''.join([f'''{gray}({'Premium' if i == 1 else 'Free'}) {blue}{x}{reset_colors}''' for x, i in self.services])}]", t=1))

email = Email(settings["email_service"]).email#Kopeechka
class Gen:
    def __init__(self) -> None:
        self.mail = email
        self.headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'en-US,en;q=0.9',
            'sec-ch-ua': '"Google Chrome";v="123", "Not:A-Brand";v="8", "Chromium";v="123"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'none',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
        }
        
    def getPage(self, requests: tls_client.Session):
        request = requests.get("https://www.instagram.com/", headers=self.headers)
        return request.cookies.get("csrftoken"), request
    def getCode(self, emailToken):
        return self.mail.getMessage(emailToken)
    def generateUsername(self):
        return "".join([random.choice(string.ascii_lowercase+string.digits+"_"*10) for x in range(10)])
    def create(self):
        global generated
        global failed
        proxy = random.choice(proxies)
        requests = tls_client.Session(random_tls_extension_order=True, client_identifier="chrome_123")
        requests.timeout_seconds = 100000
        requests.proxies = {
            "http": f"http://{proxy}",
            "https": f"https://{proxy}"
        }
        csrfToken, PageRequest = self.getPage(requests)
        js = PageRequest.text.split('"deferredCookies":')[1].split('"blLoggingCavalryFields": {')[0]+'}'
        config = chompjs.parse_js_object(js)
        for obj in config.keys():
            if "mid" in obj:
                mid = obj
        igAjax = PageRequest.text.split('"rev":')[1].split("\n")[0].split("}")[0].replace(" ", "")
        deviceId, webDeviceId = config[mid]["value"], config["_js_ig_did"]["value"]
        appID = PageRequest.text.split('"appId":')[1].split(",")[0].replace(" ", "")
        headers = {
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.9",
            "Content-Type": "application/x-www-form-urlencoded",
            "Dpr": "1",
            "Origin": "https://www.instagram.com",
            "Referer": "https://www.instagram.com/accounts/emailsignup/",
            "Sec-Ch-Prefers-Color-Scheme": "dark",
            "Sec-Ch-Ua": '"Google Chrome";v="123", "Not:A-Brand";v="8", "Chromium";v="123"',
            "Sec-Ch-Ua-Full-Version-List": '"Google Chrome";v="123.0.6312.86", "Not:A-Brand";v="8.0.0.0", "Chromium";v="123.0.6312.86"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Model": '""',
            "Sec-Ch-Ua-Platform": '"Windows"',
            "Sec-Ch-Ua-Platform-Version": '"10.0.0"',
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
            "X-Asbd-Id": "129477",
            "X-Csrftoken": csrfToken,
            "X-Ig-App-Id": appID,
            "X-Ig-Www-Claim": "0",
            "X-Instagram-Ajax": str(igAjax),
            "X-Requested-With": "XMLHttpRequest",
            "X-Web-Device-Id": webDeviceId
        }
        username = self.generateUsername()
        email, emailToken = self.mail.createEmail()
        payload = {
            "email": email,
            "device_id": deviceId
        }
        request = requests.post("https://www.instagram.com/api/v1/accounts/send_verify_email/", headers=headers, data=payload)
        if request.json().get("email_sent"):
            console.info("Waiting for registration code ...")
        else:
            console.warn(f"Failed to send code {reset_colors}[{gray}Status code: {warn}{request.status_code}{reset_colors}]", t=1)
            return False
        code = self.getCode(emailToken)
        console.success(f"Got registration code |   {code}")
        payload["code"] = code
        request = requests.post("https://www.instagram.com/api/v1/accounts/check_confirmation_code/", headers=headers, data=payload)
        js = request.json()
        if js.get("status") == "ok":
            signup_code = js.get("signup_code")
        else:
            console.warn(f"Failed to confirm code {reset_colors}[{gray}Status code: {warn}{request.status_code}{reset_colors}]", t=1)
            return False
        encpassword = f"#PWD_INSTAGRAM_BROWSER:0:{int(time.time())}:VirusNoirONTOP!FORREAL"
        payload = {
            "enc_password": encpassword,
            "day": "16",
            "email": email,
            "first_name": "TopG VirusNoir",
            "month": "6",
            "username": username,
            "year": "2005",
            "client_id": deviceId,
            "seamless_login_enabled": "1",
            "tos_version": "row",
            "force_sign_up_code": signup_code
        }

        request = requests.post("https://www.instagram.com/api/v1/web/accounts/web_create_ajax/", headers=headers, data=payload)
        if request.status_code in ok or request.status_code == 572:
            js = request.json() if request.status_code in ok else {"account_created": True, "user_id": "Not provided"}
            if js.get("account_created") == True:
                generated += 1
                console.success(f"Account created {reset_colors}[{gray}User ID: {blue}{js.get('user_id')}{reset_colors}, {gray}Username: {blue}{username}{reset_colors}, {gray}Email: {blue}{email}{reset_colors}, {gray}Password: {blue}Opera_browser!!11{reset_colors}, {gray}Account Status: {f'{red}LOCKED' if request.status_code not in ok else f'{white_green}UNLOCKED'}{reset_colors}]")
                sessionId = request.cookies.get("sessionid")
                with open("accounts.txt", "a") as f:
                    f.write(f"{username}:VirusNoirONTOP!FORREAL:{email}:{sessionId}\n")
                return True
        failed += 1
        console.warn("Failed to create account", t=1)
gen = Gen()
def main():
    accsToGen = int(console.input("Num of accs to gen > "))
    with concurrent.futures.ThreadPoolExecutor(accsToGen) as executor:
        threads = [executor.submit(gen.create) for i in range(accsToGen)]
        for thread in concurrent.futures.as_completed(threads):
            try:
                thread.result()
            except Exception as e:
                console.error(e)
main()
console.info(f"Generated {generated} account and {failed} of them failed to be generated")    
