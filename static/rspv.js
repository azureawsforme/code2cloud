async function sendRsvp(eventRsvp) {
    but = document.getElementById("rspv-button")
    but.disabled = true;

    rspvheader = document.getElementById("see you there")
    rspvheader.hidden = false;

    data = JSON.stringify({"event-rsvp" : eventRsvp})

    const response = await fetch ("/rsvp", {
        method : 'POST',
        credentials : 'same-origin',
        headers : {
            'Content-Type' : 'application/json'
        },
        body : data

    })
};