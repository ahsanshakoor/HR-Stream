from hrstream.celery import app


@app.task
def autopunchout():
    print("I am very busy....")