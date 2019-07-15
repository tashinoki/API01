
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

options = Options()
options.headless = True
options.add_argument("--no-sandbox")
options.add_argument("--disable-setuid-sandbox")

my_fit = 'https://my.fit.ac.jp'
chrome_exe_path = 'C:\\Users\\User\\Driver\\chromedriver.exe'
# chrome = webdriver.Chrome(executable_path=chrome_exe_path)


# tokenの取得
def get_fit_token(user_id, user_pwd):

    chrome = launch_browser()
    chrome = fit_certification(chrome, user_id, user_pwd)
    fit_token = chrome.get_cookies()[0]['value']

    return fit_token


# ブラウザの立ち上げ
# 同じユーザは同じオブジェクトを使いまわせないか？
def launch_browser():
    return webdriver.Chrome(executable_path=chrome_exe_path, chrome_options=options)


# sso認証
def fit_certification(browser, user_id, user_pwd):
    chrome = browser
    chrome.get(my_fit)

    benefit = chrome.find_element_by_id('benefit')
    chrome.switch_to_frame(benefit)

    idp = chrome.find_element_by_id('idp')
    chrome.switch_to_frame(idp)

    tgt = chrome.find_element_by_id('tgt')
    chrome.switch_to_frame(tgt)

    # ログイン処理
    chrome.find_element_by_id('username').send_keys(user_id)
    chrome.find_element_by_id('password').send_keys(user_pwd)
    chrome.find_element_by_xpath('html/body/div/div/div/div/form/div/button').click()

    return chrome
