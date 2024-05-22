# yappaccino.py - Breaking news
from requests import get
from asyncio import run, sleep, create_task, gather
from bs4 import BeautifulSoup as bs4
from sys import exit
from datetime import datetime as dt
import json as j
from ai import chat

p = print

class Error(Exception):
    def __init__(self, e=None, location=None, status=None):
        self.errors = {
            'status': status,
            'error': str(e),
            'location': location
        }
        print(self.errors)
        exit(1)
    
    def __str__(self):
        return str(self.errors)

class LocalDev:
    def __init__(self): pass
    async def get_file(self, name, cp="get_news"):
        try:
            ext = ".html"
            bad_chars = [":", ",", "/", "\\", "(", ")", "?", "*", ";", "!", "&", "`", "="]
            
            for a in bad_chars:
                name = name.replace(a, '')
            if not name.endswith(ext):
                name = name + ext
                
            with open(name, "r") as f:
                return f.read()
        except Exception as e: raise Error(e, cp, 403)
                    
    async def save(self, news, title, cp="save"):
        try:
            bad_chars = [":", ",", "/", "\\", "(", ")", "?", "*", ";", "!", "&", "`", "="]
            
            for a in bad_chars:
                title = title.replace(a, '')
            with open(title + '.html', "w") as f:
                f.write(news)
                return True
        except Exception as e: raise Error(e, cp, 403)

class Choose_state:
    def __init__(self, ld):
        self.latest = True
        self.url = 'https://nation.africa/kenya'
        self.ld = ld
        
    async def get_news(self, comps):
        if self.latest:
            self.news = await comps.get_latest_data(self.url)
        else:
            self.news = await ld.get_file("news")
            
        return self.news
        
class Components:
    saved_articles = []
    def __init__(self, ld, state):
        self.ld = ld 
        self.state = state                        
                         
    async def get_latest_data(self, url, cp="get_latest_data"):
        try:
            news = await self.fetch(url)
            return news
        except Exception as e: raise Error(e, cp, 403)
            
    async def fetch(self, url, cp='fetch'):
        try:
            headers = {}
            
            r = get(url, headers)
            headers = r.headers
             
            if r.status_code < 400:
                return r.text
            else:
                raise Error(r, cp, r.status_code)
                
        except Exception as e: raise Error(e, cp, 403)

    async def get_soup(self, r, cp="get_soup"):
        try:
            soup = bs4(r, "html.parser")
            return soup
        except Exception as e: raise Error(e, cp, 403)

    async def save_article(self, article_paragraph, do, cp="save_article", file="news.json"):
        try:
            if do == "append":
                if article_paragraph == {}:
                    return False
                try:
                    self.saved_articles.append(article_paragraph)
                except:
                    pass
                return f"Current articles: {len(self.saved_articles)} articles!"
            elif do == "save":
                return f"Saved {len(self.saved_articles)} articles!", self.saved_articles
                with open(file, "w", encoding="utf=8") as f:
                    j.dump(self.saved_articles, f, indent=4)
                    return f"Fetched {len(self.saved_articles)} articles!", self.saved_articles
    
        except Exception as e: raise Error(e, cp, 403) 

class Main:
    ld = LocalDev()
    state = Choose_state(ld)
    comps = Components(ld, state)
    
    def __init__(self): pass                                                                            
    async def latest_news(self, latest=True, cp="latest_news"):
        url = self.state.url
        do = "append"
        
        try:
            news = await self.state.get_news(self.comps)
            soup = await self.comps.get_soup(news)  
            article = soup.find_all("section", class_="nested-cols headline-teasers_row")
            
            tasks = []
            for a in article:
               try:
                   snippet = a.find('p').text.strip()
               except:
                   snippet = None
               
               if not "https://" in a.find("a").attrs['href']:
                   article_url = url + a.find("a").attrs['href'].replace('/kenya', '')
               else:
                   article_url = a.find("a").attrs['href']
               
               data = {"title": a.find("h3").text.strip(), "url": article_url, "snippet": snippet, "date": a.find("span", class_="date").text.strip()}
               
               tasks.append(self.process_article(data, latest, do))
        
            await gather(*tasks)
            do = "save"
            msg, saved_articles = await self.process_article(data, latest, do)
            
            if msg and saved_articles:
                p(msg)
                return saved_articles
                
        except Exception as e: raise Error(e, cp, 403)
    
    async def process_article(self, dict, latest, do, cp="process_article"):
        data = {}
        prompt = "Paraphrase this: "
        try:
            url = dict['url']
            
            if latest:
                r = await self.comps.fetch(url)
               
            soup = await self.comps.get_soup(r)
            
            if soup:
                try:
                    article_img = 'https://nation.africa' + str(soup.find("div", class_="article-page").find("img").attrs["src"])
                    image_caption = soup.find("figcaption", class_="article-picture_caption").find("p").text.strip()
                    image_copyright = soup.find("div", class_="article-picture_copyright").text.strip()
                    summary = chat(prompt + soup.find("section").find(class_="rte--list").find('li').text.strip())
                    date = dict['date']
                    article_paragraph = []
                    
                    data = {"title": chat(prompt + dict["title"]), "article_img": article_img, "image_caption": image_caption, "image_copyright": image_copyright, "summary": summary, "date": f'Current time: {str(dt.now())}, article_publish_time: {date}', "article_paragraph": article_paragraph}
                    
                except Exception as e: pass
    
                   
            article = soup.find_all("div", class_="paragraph-wrapper")
            
            for a in article:
                text = a.find('p')
                if text:
                    text = text.text.strip()
                    if not text.startswith("Also Read:"):
                        data["article_paragraph"].append(text)
                    
            data["article_paragraph"] = chat(prompt + ' '.join(data["article_paragraph"]))
        except Exception as e: pass
        try:
            save = await self.comps.save_article(data, do)
            if save:
                return save
        except Exception as e: raise Error(e, cp, 403)

def gate():
    news = run(Main().latest_news())   
    return news
    
if __name__ =="__main__":
    pass