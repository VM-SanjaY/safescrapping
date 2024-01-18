from django.shortcuts import render, redirect
from selenium import webdriver
from django.db.models import Q
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import os
from django.http import HttpResponse
from .models import *
from bs4 import BeautifulSoup
import urllib.request
from urllib.request import urlopen
import time
import re

options = webdriver.ChromeOptions()
options.add_argument('headless')
service_obj = Service()
driver = webdriver.Chrome(service=service_obj,options=options)
driver.maximize_window()
driver.implicitly_wait(5)
driver.get("https://www.safeway.com/")


def accesssafeway(request):
    if request.method == "POST":
        return redirect ('runsafeway')
    return render(request,'ohhoinana.html')

def runsafeway(request):
    driver.find_element(By.XPATH,"//*[text()='Necessary Only']").click()
    time.sleep(2)
    for i in range(3):
        time.sleep(.5)
        driver.find_element(By.XPATH,"//input[@type='search']").send_keys(Keys.PAGE_DOWN);
    time.sleep(3)

    finding_cookies = driver.find_elements(By.XPATH,'//*[@class="categories-item__item-text"]/h3')

    for cookie in finding_cookies:
        if cookie.text == "Cookies, Snacks & Candy":
            parent_dir = 'media\\'
            path = os.path.join(parent_dir, cookie.text)
            try:
                os.mkdir(path)
                maindir = path
                subdir = cookie.text
                cookie.click()
                break
            except:
                maindir = path
                subdir = cookie.text
                cookie.click()
                break

    time.sleep(3)
    driver.find_element(By.XPATH,"//*[text()='View all']").click()
    time.sleep(3)
    data_inside_viewall = driver.find_elements(By.XPATH,'//div[@class="aisle-category"]')
    sublist = set()

    def replace_special_characters(text):
        cleaned_text = text.replace(',', ' ').replace('&', ' ').replace('-',' ')
        cleaned_text = ' '.join(cleaned_text.split())
        return cleaned_text

    for data in data_inside_viewall:
        cleaned_text = replace_special_characters(data.text)
        sublist.add(cleaned_text)

    new_sublist = []
    for sub in sublist:
        if sub == '':
            continue
        else:
            new_sublist.append(sub)
            if not Subcategory.objects.filter(subcategory_name=sub).exists():
                subcat = Subcategory(subcategory_name=sub)
                subcat.save()
            path = os.path.join(maindir, sub)
            try:
                os.mkdir(path)
            except:
                continue

    subcategories = driver.find_elements(By.XPATH,'//a[@class="sbc-link"]')

    subcategorieslist = []
    listinchip = []
    dicofchipset = {}
    for category in subcategories:
        categoryahref = category.get_attribute('href')
        subcategorieslist.append(categoryahref)

    for linkinsubligt in subcategorieslist:
        html = urlopen(linkinsubligt)
        bs4obj = BeautifulSoup(html.read(),'lxml')
        subcategory_urls = set()
        url_count = 0
        for link in bs4obj.find_all('a'):
            href = link.get('href')
            if href is not None and '/shop/product-details' in href:
                fullurl = 'https://www.safeway.com'+href
                subcategory_urls.add(fullurl)
                url_count +=1
                if url_count >= 3:
                    break
        dicofchipset[linkinsubligt] = list(subcategory_urls)
        listinchip.extend(list(subcategory_urls))
        
    for key, value in dicofchipset.items():
        value = list(value)
        before_html = re.search(r'\/([^/]+)\.html', key)
        print('')
        driver.get(key)
        time.sleep(5)
        amtlist = driver.find_elements(By.XPATH, "//span[@data-qa='prd-itm-prc']/span[1]")
        time.sleep(5)
        amtcount = 0
        amut = []
        for amt in amtlist:
            print("segsgg -", amt.text)
            amut.append(amt.text)
            amtcount += 1
            if amtcount >= 3:
                break
        if before_html:
            folderna = before_html.group(1)
            folderna = folderna.replace('-', ' ')
            foldername = folderna.capitalize()
        for i in range(len(value)):
            print("values -", value[i])
            try:
                print("amount =", amut[i])
            except:
                print("it is empty here")
            html = urlopen(value[i])
            try:
                amount = amut[i]
            except:
                amount = '$4.19'
            bs4obj = BeautifulSoup(html.read(), 'lxml')

            try:
                paratag = bs4obj.find('div',class_="tab-pane fade body-text show active").text
                if paratag:
                    paratag = paratag.strip().replace('  ', ' ')
                    paratag = paratag.lstrip()
                else:
                    paratag = paratag.lstrip()
            except:
                paratag = "None available"          
            imgname = bs4obj.h1.text
            sourceimg = bs4obj.find('source', class_='product-image__breakpoint')
            fulllink = 'https:' + sourceimg.get('srcset')
            file_path = os.path.join(maindir, foldername, imgname + '.jpeg')
            try:
                im_path = os.path.join(subdir, foldername, imgname + '.jpeg')
            except:
                im_path = ""
            text_path = os.path.join(maindir, foldername, imgname + '.txt')
            if not os.path.exists(file_path):
                img_file = open(file_path, 'wb')
                img_file.write(urlopen(fulllink).read())
                img_file.close()
                print("image is writing")
            else:
                print("image is already present")
            if not os.path.exists(text_path):
                file_text = open(text_path, 'w')
                file_text.write(f"Name: {imgname}\nAmount: {amount}\nDescription: {paratag}")
                file_text.close()
                folde = Subcategory.objects.get(subcategory_name=foldername)
                print("file is writing")
            else:
                print("file is already present")
            if not Datastore.objects.filter(Q(name=imgname)&Q(thumb=im_path)).exists():
                dtta = Datastore(
                        subcategory=folde,
                        name=imgname,
                        thumb=im_path,
                        desc=paratag,
                        price=amount,
                    )
                dtta.save()                    
    return HttpResponse("Data runned completely. Check your folder.  in the url add = display/ after running/")


def imagedisplay(request):
    allsubcate = Subcategory.objects.all()
    gigidi=""
    if request.method == "POST":
        category = request.POST.get('category')
        allsub = Subcategory.objects.get(subcategory_name=category)
        gigidi = Datastore.objects.filter(subcategory=allsub)
    context ={"allsubcate":allsubcate,"gigidi":gigidi}
    return render(request,'datashow.html',context)








