from backend import a, p, Bottle, route, run, request, static_file, r, post, get, put, delete, template, redirect, HTTPResponse, abort, hook, Thread, Backend_apps

app = Bottle()
apps = Backend_apps()

@app.route('/api/v1/models', method=['GET','POST'])
def models():
    try:
        method, data = a.run(apps.dealer(request, r))
        return data
    except Exception as e:
        abort(403, str(e))

def ping():
    stay = True
    if stay:
        url = "https://ainationnews.onrender.com"
        t = Thread(target=apps.run, args=(url,))
        t.start()

if __name__=="__main__":
    ping()
    run(app=app, host="0.0.0.0", port="8004", debug=True, reloader=True)