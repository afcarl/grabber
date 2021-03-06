import grequests
import lxml.html
import requests
import os
import datetime
import shutil
import time
import pickle
import random
from PIL import Image
from StringIO import StringIO

def grabber():
    all_links = []
    urls = [
        "http://newyork.backpage.com/FemaleEscorts/",
        "http://sfbay.backpage.com/FemaleEscorts/",
        "http://northjersey.backpage.com/FemaleEscorts/",
        "http://arizona.backpage.com/FemaleEscorts/",
        "http://pennsylvania.backpage.com/FemaleEscorts/",
        "http://massachusetts.backpage.com/FemaleEscorts/",
        "http://montana.backpage.com/FemaleEscorts/"
        ]

    rs = (grequests.get(u) for u in urls)
    responses = grequests.map(rs)
    print "initial get.."
    time.sleep(12)
    for r in responses:
        text = r.text.encode("ascii","ignore")
        html = lxml.html.fromstring(text)
        links = html.xpath('//div[@class="cat"]/a/@href')
        all_links += links
    urlz = []
    print "processing complete.."
    for i in xrange(0,len(all_links),10):
        urlz.append(all_links[i-10:i])
    all_responses = []
    total_time = len(urlz)*4/60.0
    print "will run for ",total_time,"minutes" 
    for url_list in urlz[:2]:
        print "in loop"
        all_rs = (grequests.get(u) for u in url_list)
        all_responses += grequests.map(all_rs)
        time.sleep(4)
    return all_responses


def save_files(all_responses):
    timestamp = str(datetime.datetime.now())
    timestamp = timestamp.split(".")[0]
    timestamp = timestamp.replace(":","_")
    timestamp = timestamp.replace(" ","_")
    dir_name = "bp_"+timestamp
    os.mkdir(dir_name)
    os.chdir(dir_name)
    for r in all_responses:
        text = r.text.encode("ascii","ignore")
        html = lxml.html.fromstring(text)
        html_imgs = html.xpath('//ul[@id="viewAdPhotoLayout"]/li/img/@src')
        
        img_rs = (grequests.get(u) for u in html_imgs)
        img_responses = grequests.map(img_rs)
        filename = r.url.split("/")[-1]
        allcontent = filename+"_"+timestamp
        os.mkdir(allcontent)
        os.chdir(allcontent)
        with open(filename+".html","w") as f:
            f.write(text)

        print "saving images"
        for img in img_responses:
            img_name = img.url.split("/")[-1]
            img_name = img_name.split(".")[0]+".png"
            i = Image.open(StringIO(img.content))
            i.save(img_name)
        os.chdir("../")

if __name__ == '__main__':
    while True:
        print "starting.."
        responses = grabber()
        print "saving.."
        save_files(responses)
        print "done"
        rando = random.randint(1440,2700)
        time.sleep(rando)
