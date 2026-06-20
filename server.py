from flask import Flask, request, render_template

invite_app = Flask('app')

@invite_app.route("/view")

def view_invite():
    to = "Sarah"
    event = "Chirag's Birthday Party"
    date = "Feb 17th"
    time = " 6 PM "
    sender = "Raghu"

    #http://localhost:8080/view?=kids
    style = request.args.get('style')

    template = "invite-" + style + ".html"
    
    
    return render_template(template, to=to, event_name=event,date=date,time=time,sender=sender)

if __name__ == '__main__' :
    invite_app.run(debug=True, use_reloader=True, host='0.0.0.0',port=8080)