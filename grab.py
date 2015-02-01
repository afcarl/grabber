import grequests
import lxml.html
import requests
import os
import datetime
import shutil
import time
import pickle
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
    time.sleep(1500)
    for r in responses:
        text = r.text.encode("ascii","ignore")
        html = lxml.html.fromstring(text)
        links = html.xpath('//div[@class="cat"]/a/@href')
        all_links += links
    
    all_rs = (grequests.get(u) for u in all_links)
    #all_responses = grequests.map(all_rs)
    return grequests.map(all_rs)

def get_all_backpages():
    r = requests.get("http://www.backpage.com/")
    html = lxml.html.fromstring(r.text)
    backpages = html.xpath("//a/@href")
    links = []
    for i in backpages:
        if "backpage" in i:
            if not "www" in i: 
                i = str(i)
                links.append(i)

    with open("backpages","w") as f:
        pickle.dump(links,f)
    
def setup_all(index):
    backpages = pickle.load(open("backpages","rb"))
    female_escorts = []
    body_rubs = []
    strippers = []
    dominatrixes = []
    transsexual_escorts = []
    male_escorts = []
    websites = []
    adult_jobs = []
    for page in backpages:
        for i in xrange(1,index):
            if i == 1:
                female = page + "FemaleEscorts/"
                female_escorts.append(female)
                bodyrub = page + "BodyRubs/"
                body_rubs.append(bodyrub)
                stripper = page + "Strippers/"
                strippers.append(stripper)
                dominatrix = page + "Domination/"
                dominatrixes.append(dominatrix)
                transsexual = page + "TranssexualEscorts/"
                transsexual_escorts.append(transsexual)
                male = page + "MaleEscorts/"
                male_escorts.append(male)
                website = page + "Datelines/"
                websites.append(website)
                adult = page + "AdultJobs/"
                adult_jobs.append(adult)
            else:
                female = page + "FemaleEscorts/?page="+str(i)
                female_escorts.append(female)
                bodyrub = page + "BodyRubs/?page="+str(i)
                body_rubs.append(bodyrub)
                stripper = page + "Strippers/?page="+str(i)
                strippers.append(stripper)
                dominatrix = page + "Domination/?page="+str(i)
                dominatrixes.append(dominatrix)
                transsexual = page + "TranssexualEscorts/?page="+str(i)
                transsexual_escorts.append(transsexual)
                male = page + "MaleEscorts/?page="+str(i)
                male_escorts.append(male)
                website = page + "Datelines/?page="+str(i)
                websites.append(website)
                adult = page + "AdultJobs/?page="+str(i)
                adult_jobs.append(adult)
                
    all_pages = female_escorts + body_rubs + strippers + dominatrixes + transsexual_escorts + male_escorts + websites + adult_jobs
    return all_pages

#gets all the ads on a given backpage, page
def grab_ads(page):
    try:
        r = requests.get(page)
        html = lxml.html.fromstring(r.text)
        ads = html.xpath('//div[@class="cat"]/a/@href')
        final = []
        for ad in ads:
            ad = str(ad)
            final.append(ad)
        return final
    except requests.exceptions.ConnectionError:
        return []
    
def get_information_from_page(url_list,asynchronous=False):


    if asynchronous:
        for urls in url_list:
            rs = (grequests.get(u,stream=False) for u in urls)
            responses = grequests.map(rs)
            results = []
            for r in responses:
                result = {}
                html = lxml.html.fromstring(r.text)
                posting_body = html.xpath('//div[@class="postingBody"]')
                result["textbody"] = [i.text_content() for i in posting_body]
                result['pictures'] = html.xpath('//ul[@id="viewAdPhotoLayout"]/li/a/@href')
                result['url'] = r.url
                results.append(result)
                r.close()
        if url_list != []: 
            return results
        else:
            return []
            
    else:
        r = requests.get(url_list)
        html = lxml.html.fromstring(r.text)
        posting_body = html.xpath('//div[@class="postingBody"]')
        textbody = [i.text_content() for i in posting_body]
        pictures = html.xpath('//ul[@id="viewAdPhotoLayout"]/li/a/@href')
        return textbody,pictures
# data = []
# for link in links:
#     data.append(get_information_from_page(link))

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
        html = lxml.html.fromstring("text")
        html_imgs = html.xpath('//ul[@id="viewAdPhotoLayout"]/li/a/@src')
        img_rs = (grequests.get(u) for u in html_imgs)
        img_responses = grequests.map(img_rs)
        filename = r.url.split("/")[-1]
        allcontent = filename+"_"+timestamp
        os.mkdir(allcontent)
        os.chdir(allcontent)
        with open(filename,"w") as f:
            f.write(text)
        for img in img_responses:
            img_name = img.url.split("/")[-1]
            with open(img_name,"wb") as g:
                img.raw.decode_content = True
                shutil.copyfileobj(img.raw,g)
        os.chdir("../")

if __name__ == '__main__':
    #responses = grabber()
    #save_files(responses)
    print "start.."
    pages = setup_all(3)
    print "got all the links to start scraping.."
    links = []

    #for real
    print "scraping all the links.."
    for page in pages[:10]:
        links += grab_ads(page)

    print "grabbing page data..."

    #chunking requests because grequests can't handle that many at once
    url_list = []
    for i in xrange(0,len(links),10):
        url_list.append(links[i-10:i])

    data = get_information_from_page(url_list,asynchronous=True)
    print data
