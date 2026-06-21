from flask import Flask, request, render_template
import json,os
import dotenv
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
from azure.core.exceptions import ResourceExistsError,ResourceNotFoundError

#create the flask app
app = Flask('app')

# When we need to run it locally
from dotenv import load_dotenv
load_dotenv(".env")

#Make Container
connect_str = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
blob_service_client = BlobServiceClient.from_connection_string(connect_str)

# Create local directory to hold RSVP files
local_path="./data"
os.makedirs("data",exist_ok=True)

# Create unique name for the container
container_name="inviteappstorage"

# Create the container in Azure blob storage
try:
    container_client=blob_service_client.create_container(container_name)
except ResourceExistsError:
    container_client=blob_service_client.get_container_client(container_name)

# Routes that are required for the program

# The Route where we will see the form to create an invite
@app.route("/")
def form():
    return render_template("form.html")

# Route where you see the invite
@app.route("/view")
def view_invite():
    # to = "Sarah"
    # event = "Chirag's Birthday Party"
    # date = "Feb 17th"
    # time = " 6 PM "
    # sender = "Raghu"

    to = request.args.get("to")
    event = request.args.get("event")
    date = request.args.get("date")
    time = request.args.get("time")
    sender = request.args.get("sender")
    style = request.args.get('style')
    eventId = sender + "|" + event

    #http://localhost:8080/view?=kids
    # style = request.args.get('style')

    template = "invite-" + style + ".html"
    
    
    return render_template(template, to=to, event_name=event,date=date,time=time,sender=sender, eventId=eventId)

@app.route("/events")
def events():
    Blob_list = container_client.list_blobs()

    render_template("events.html",event_list=Blob_list)

# The route that lists all the RSVPs for a specific event
@app.route("/event-rsvp/<event_file>")
def event_rsvps(event_file):
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=event_file)
    attendees = str(blob_client.download_blob().readall(), "utf-8")
    attendees = attendees.split("\n")
    print(attendees)
    return render_template("event-rsvp.html", attendees=attendees)
    print(event_file)

# The route that handles the RSVP button from the invitaiton page
@app.route("/rsvp", methods=('GET', 'POST'))
def rsvp():
    data = request.json
    event_data = data["event-rsvp"].split(",")
    attendee = event_data[0]
    event_ID = event_data[1]
    print("RSVP, conect str", connect_str)

    # Attempt to sync the blob
    try:
        sync_blob(event_ID, attendee)
        print("Blob sync succeeded")
        return json.dumps({'success':True}), 200, {'ContentType':'application/json'}
    except:
        print("Blob sync failed")
        return json.dumps({'success':True}), 400, {'ContentType':'application/json'}


# A helper function that handles updating or creating a blob in Azure blob storage
def sync_blob(event_ID,attendee):
    print("Blob Sync Succeeded")

    filename = event_ID + ".txt"
    local_file=os.path.join(local_path,filename)
    print(local_file)

    blob_client = blob_service_client.get_blob_client(container=container_name, blob=filename)

    # Try to download the blob, if it exists. Then update the file with the new attendee
    try:
        print("\nDownloading blob to \n\t" + local_file)

        # Get the data out of the file, split it into a list of people who have already RSVPed
        attendees = str(blob_client.download_blob().readall(), "utf-8")
        attendees = attendees.split("\n")

        if attendee not in attendees:
            attendees.append(attendee)
        
            # Make the local file
            with open(local_file, "w") as download_file:
                download_file.writelines("\n".join(attendees))

            # Push the local file to Azure blob
            with open(local_file, "rb") as data:
                blob_client.delete_blob()
                blob_client.upload_blob(data)
            print(f"File ({filename}) updated on blob.")

    # The blob wasn't there, oh no! Let's make a new one, this must be the first RSVP for this event
    except ResourceNotFoundError:
        # If the file doesn't exist, make a local file, conatining the single attendee from the request
        with open(local_file, "w") as f:
            f.write(attendee)

        # Write the file to Azure blob
        with open(local_file, "rb") as data:
            blob_client.upload_blob(data)
            print("New file uploaded to blob.")

if __name__ == '__main__' :
    app.run(debug=True, use_reloader=True, host='0.0.0.0',port=8080)
    #sync_blob("jim|bday party","Sahana")