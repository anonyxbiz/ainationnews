import asyncio as a, json as j
from bottle import Bottle, route, run, request, static_file, response as r, post, get, put, delete, template, redirect, HTTPResponse, abort, hook
from threading import Thread
from yappaccino import Main as news_gen
from requests import get as r_get

p = print

class Backend_apps:
    def __init__(self):
        self.news = news_gen()

    async def get_json(self, request):    
        return j.loads(request.body.getvalue().decode('utf-8'))          
        
    async def get_header(self, request, value):    
        return request.get_header(value)
                        
    async def incoming(self, request):
        try:
            if request.method == "GET":
                return [request.query, "get"]
                    
            elif request.method == "POST": 
                data = await self.get_json(request)
                return [data, "post"]
        except Exception as e:
            abort(403, str(e))
    
    async def dealer(self, request, response):
        try:
            data = await self.incoming(request)   
            if data:
                query = data[0].get("query") or None
                ip = request.remote_addr
                
                detail = await self.news.latest_news()
                if data[1] == "get":
                    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{detail[0]["title"]}</title>
    <style>
        /* Add your CSS styles here */
    </style>
</head>
<body>
    <div class="article">
        <img src={detail[0]["article_img"]} alt={detail[0]["image_caption"]}>
        <p>{detail[0]["image_copyright"]}</p>
        <p>{detail[0]["summary"]}</p>
        <p>{detail[0]["date"]}</p>
        <p>{detail[0]["article_paragraph"]}</p>
    </div>
</body>
</html>'''
                    return data[1], HTTPResponse(html)
                else:  
                    return data[1], detail
                    
            else:
                abort(403, "Something went wrong processing your request")
                
        except Exception as e:
            p(e)
            abort(403, f"Something went wrong on our end: {e}")
            
    async def alive(self, url):
        p('Keepalive is running')
        while True:
            try:
                r_get(url)
            except Exception as e:
                p(f"Error in keepalive: {e}")
            await a.sleep(30)
 
    def run(self, url):        
        a.run(self.alive(url))
     
                       
              
if __name__ == '__main__':
    pass