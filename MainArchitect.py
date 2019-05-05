from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup

content = []

def simple_get(url):
    """
    Attempts to get the content at `url` by making an HTTP GET request.
    If the content-type of response is some kind of HTML/XML, return the
    text content, otherwise return None.
    """
    try:
        with closing(get(url, stream=True)) as resp:
            if is_good_response(resp):
                return resp.content
            else:
                return None

    except RequestException as e:
        log_error('Error during requests to {0} : {1}'.format(url, str(e)))
        return None
    
def is_good_response(resp):
    """
    Returns True if the response seems to be HTML, False otherwise.
    """
    content_type = resp.headers['Content-Type'].lower()
#    print("resp.status_code :: ", (resp.status_code))
#    print("resp.status_code == 200 :: ", (resp.status_code == 200))
#    print("content_type is not None :: ", (content_type is not None))
#    print("content_type.find('html') > -1 :: ",(content_type.find('html') > -1))
    return (resp.status_code == 200 
            and content_type is not None 
            and content_type.find('html') > -1)

def log_error(e):
    """
    It is always a good idea to log errors. 
    This function just prints them, but you can
    make it do anything.
    """
    print(e)
    
def scrap_html(sectionTag) :
    #print(sectionTag.findAll("article"))
    for myItem in sectionTag.findAll("article"):
        info = {}
        info["name"] = myItem.find('a').string
        
        if myItem.find('div', {"class":"address"}) is not None:
            info["addr"] = myItem.find('div', {"class":"address"}).string.strip()
            addrPart = myItem.find('div', {"class":"address"}).string.strip().split(",")
            #print(addrPart[len(addrPart)-2],"\t",addrPart[len(addrPart)-1])
            info["zip"] = addrPart[len(addrPart)-1]
            info["city"] = addrPart[len(addrPart)-2]

        for pageMetaDiv in myItem.findAll('div', {"class":"pageMeta-item"}):
            if str(pageMetaDiv.string).startswith('Tel: ') and pageMetaDiv.string is not None:
                #print("CHILD[",str(i),"] :: ",str(pageMetaDiv.string).split(':')[1].strip())
                info["phone"] = str(pageMetaDiv.string).split(':')[1].strip()
            elif pageMetaDiv.find("a", {"class":"tagList","class":"faaemail"}):
                #print("pageMetaDiv :: ", pageMetaDiv.find("a", {"class":"tagList","class":"faaemail"}).string)
                info["email"] = pageMetaDiv.find("a", {"class":"tagList","class":"faaemail"}).string
            elif pageMetaDiv.find("a", {"class":"tagList","class":"exLink"}):
                #print("pageMetaDiv :: ", pageMetaDiv.find("a", {"class":"tagList","class":"exLink"}).string)
                info["website"] = pageMetaDiv.find("a", {"class":"tagList","class":"exLink"}).string        
        content.append(info)

    #print("Content :: ", content)
    #print("--------------------------------------------------------------------------\n")
    return content

content = []
for pageNo in range(0,77):
    print("Reached Page ::", pageNo)
    raw_html = simple_get('https://find-an-architect.architecture.com/FAAPractices.aspx?page=%s'%(pageNo))
    html = BeautifulSoup(raw_html, 'html.parser')

    #print(html.find(class="listColumn-withSearch"))# select().prettify())
    #print(html.select("section")[0].prettify())
    sectionTag = html.findAll("section",{"class":"listingColumn-withSearch","class":"listingColumn", "aria-labelledby":"sectionHeading"})[0]
    # print(sectionTag.prettify())
    scrap_html(sectionTag)
print(content)
