import os
from time import sleep
import discord
from discord.ext import commands
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import requests

bot = commands.Bot(command_prefix="!")

TOKEN = os.environ['TOKEN']
id = os.environ['id']
password = os.environ['password']

lecture = ""
url = "https://ex-oj.sejong.ac.kr/index.php/auth/login/"
option = Options()
option.add_argument("--headless")
resultSet = {
    '1':"Loading",
    '2':"Accept",
    '3':"Wrong Answer",
    '4':"Time Limit",
    '5':"Memory Limit",
    '6':"Compile Error",
    '8':"Output Limit",
    '9':"Run-Time Error",
    '10':"Presentation Error",
    '11':"Empty Test-data",
    '12':"Invalid Case",
    '13':"System Call Error"
}

@bot.command()
async def submit(ctx,week,num,path):
    path = path.replace("/","")
    if path.find(".py") != -1 or path.find("..") != -1:
        await ctx.send("no Hack o0o")
        return
    code = ""
    if os.path.exists(f"./code/{path}"):
        f = open(f'./code/{path}',"r",encoding='utf8')
        code = f.readlines()
        f.close()
    else:
        await ctx.send(f"can not find {path}")
        return
    try:
        #driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),options=option)
        driver = webdriver.Chrome(executable_path=os.environ['GOOGLE_CHROME_BIN'],options=option)
        driver.get(url)
        driver.find_element(By.ID,"id").send_keys(id)
        driver.find_element(By.ID,"password").send_keys(password,Keys.ENTER)
        driver.get("https://ex-oj.sejong.ac.kr/index.php/judge/studentmain/1241")#url of algorithm class
        driver.find_element(By.PARTIAL_LINK_TEXT,f"{week}주차").click()
        driver.find_element(By.PARTIAL_LINK_TEXT,f"문제{num}").click()
        driver.find_element(By.LINK_TEXT,"Coding").click()
        textarea = driver.find_element(By.CLASS_NAME,"ace_text-input")
        textarea.send_keys(Keys.CONTROL+'a')
        textarea.send_keys(Keys.DELETE)
        for i in code:
            textarea.send_keys(i+'\n')
            textarea.send_keys(Keys.LEFT_SHIFT+Keys.HOME)
            textarea.send_keys(Keys.DELETE)
        textarea.send_keys(Keys.LEFT_SHIFT+Keys.PAGE_DOWN)
        textarea.send_keys(Keys.DELETE)
        driver.find_elements(By.TAG_NAME,"input")[0].submit()
        subID = driver.find_elements(By.TAG_NAME,"td")[0].get_attribute("innerHTML")
        subID = subID.replace(" ","")
        apiURL = f"https://ex-oj.sejong.ac.kr/index.php/judge/refresh/{subID}"
        data = requests.get(apiURL).json()
        while data['result'] == '1':
            sleep(1)
            data = requests.get(apiURL).json()
        score = float(data['pass_rate']) * 100.0
        result = resultSet[data['result']]
        await ctx.send(f"{result} {score} resultUrl:{apiURL}")
        driver.close()
    except Exception as e:
        if driver:
            driver.close()

        print(e)
        await ctx.send("ERR")

@bot.command()
async def load(ctx,name):
    if ctx.message.attachments:
        attachment = ctx.message.attachments[0]
        try:
            await attachment.save(f"./code/{name}")
        except Exception as e:
            await ctx.send("ERR")

@bot.command()
async def unload(ctx,path:str):
    path = path.replace("/","")
    if path.find(".py") != -1 or path.find(".exe") != -1 or path.find("..") != -1:
        await ctx.send("no Hack o0o")
        return
    if os.path.exists("./code/"+path):
        os.remove("./code/"+path)
        await ctx.send("file removed")
    else:
        await ctx.send(f"can not find {path}")

bot.run(TOKEN)
