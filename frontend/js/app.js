//"use strict";

// The host where the API is hosted
var apiHost = "https://safeisland.hesusruiz.org";


// This variable holds at all times in memory the value of the current credential
//var passengerCredential = credentialInitialJSON;
var testJWT = "eyJhbGciOiJFUzI1NksiLCJraWQiOiJkaWQ6ZWxzaTpWQVRFUy1BODYyMTI0MjAja2V5LXZlcmlmaWNhdGlvbiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE2MDc5ODQ4NDEsImlhdCI6MTYwNzU1Mjg0MSwiaXNzIjoiZGlkOmVsc2k6VkFURVMtQTg2MjEyNDIwIiwibmJmIjoxNjA3NTUyODQxLCJzdWIiOiI0NjEwNjUwOEgiLCJ2YyI6eyJAY29udGV4dCI6WyJodHRwczovL3d3dy53My5vcmcvMjAxOC9jcmVkZW50aWFscy92MSIsImh0dHBzOi8vYWxhc3RyaWEuZ2l0aHViLmlvL2lkZW50aXR5L2NyZWRlbnRpYWxzL3YxIiwiaHR0cHM6Ly9zYWZlaXNsYW5kLm9yZy8ud2VsbC1rbm93bi93M2MtY292aWQtdGVzdC92MSJdLCJjcmVkZW50aWFsU3ViamVjdCI6eyJjb3ZpZFRlc3RSZXN1bHQiOnsiQUNRVUlSRVJfSUQiOiIiLCJDSVRJWkVOIjp7IkNJVElaRU5fQ0VMTF9QSE9ORSI6IjAwMzQ1ODQ5OTY1MzIiLCJDSVRJWkVOX0VNQUlMX0FERFIiOiJwYXNzZW5nZXJAZ21haWwuY29tIiwiSURfVFlQRSI6IklEX0NBUkQiLCJOQU1FIjoiQ09TVEEvQUxCRVJUTyIsIlZBTElEX0lEX05VTUJFUiI6IjQ2MTA2NTA4SCJ9LCJESUFHTk9TVElDX1BBU1NfREFUQSI6eyJESUFHTk9TSVMiOiJGUkVFIiwiRElBR05PU0lTX0RVRV9EQVRFIjoiMjAyMC0xMC0xNyAxMTowNTo0Ny42NTkiLCJESUFHTk9TSVNfUVIiOiIiLCJESUFHTk9TVElDX05VTUJFUiI6IkxFNFJEUyIsIkRJQUdOT1NUSUNfUEFTU19CQ0tfSEFTSCI6IiIsIkRJQUdOT1NUSUNfVFlQRSI6IlZJUk9MRU5TIFNBTElWQSIsIlRJTUVTVEFNUCI6IjIwMjAtMTAtMTUgMTE6MDU6NDcuNjU5In0sIklTU1VFUl9JRCI6IjkwMTIzNDVKSyIsIk1FUkNIQU5UIjp7IkNBUlRSSURHRSI6eyJDQVJUUklER0VfRFVFX0RBVEUiOiIyNC8xMi8yMDIxIiwiQ0FSVFJJREdFX0lEIjoiVlJMNTU1NTU1NjY2In0sIkRFVklDRV9JRCI6IjM0NTY3ODY3IiwiTUVSQ0hBTlRfREFUQSI6eyJNRVJDSEFOVF9BRERSIjoiTEFOWkFST1RFIEFJUlBPUlQgVDEiLCJNRVJDSEFOVF9JRCI6ImRpZDplbHNpOlZBVEVTLUE4NjIxMjQyMCJ9LCJPUEVSQVRPUl9EQVRBIjp7Ik9QRVJBVE9SX0NFTExfUEhPTkVfR1BTIjoiMjguOTUxMTQ2LCAtMTMuNjA1NzYwIiwiT1BFUkFUT1JfQ0VMTF9QSE9ORV9JRCI6IjAwMzQ2Nzk4MTU1MTQiLCJPUEVSQVRPUl9JRCI6IjM2OTI2NzY2SiJ9fX0sImxldmVsT2ZBc3N1cmFuY2UiOjJ9LCJ0eXBlIjpbIlZlcmlmaWFibGVDcmVkZW50aWFsIiwiQWxhc3RyaWFWZXJpZmlhYmxlQ3JlZGVudGlhbCIsIlNhZmVJc2xhbmRDb3ZpZFRlc3RSZXN1bHQiXX19.KK4iGxfajtVMf8KsGdFuWD6F3xHnQcj5bj7DQgI_hDCHSXw7HpA1uMpGDyRK2LKIDgji1qixpmMj7oUUHsiEeQ"
var currentPassengerJWT = testJWT;

var passengerCredential = covidCredFromJWTUnsecure(currentPassengerJWT);

// When user navigates between pages of the application, the system generates "hashchange" events
// We install a listener for those changes and dispatch the event to the associated function per page
window.addEventListener("hashchange", function () {
    console.log(location.hash);

    // Execute logic on page enter for each different page
    process_page_enter();

});


function process_page_enter() {

    // Handle page transition
    // Hide all pages of the application
    $(".jrmpage").hide();
    // Show a single page: the one we are now (if hash is non-null) or the home otherwise
    if (location.hash) {
        $(location.hash).show();
    } else {
        $("#home").show();
    }

    // Passenger: display in text mode of the credential
    if (location.hash == "#passengerDisplayCredential") {
        console.log("In #passengerDisplayCredential script")
        passengerDisplayCredential();
    }

    // Passenger: display QR of the credential
    if (location.hash == "#passengerDisplayQR") {
        console.log("In #passengerDisplayQR script")
        passengerDisplayQR();
    }

    // Passenger: receive a new credential by scanning a QR from the Verifier
    if (location.hash == "#QRScanPassenger") {
        console.log("In #QRScanPassenger script")
        initiateQRScanning("Passenger");
    }

    // Verifier: receive and verify credential from a Passenger
    if (location.hash == "#QRScanVerifier") {
        console.log("In #QRScanVerifier script")
        initiateQRScanning("Verifier");
    }

    // Issuer: Obtain and display all available credentials from the server
    if (location.hash == "#issuer") {
        console.log("In #issuer script")

        // Retrieve the list of credentials from the server
        // The server must be the same one user by the verifier application
        var targetURL = apiHost + "/api/verifiable-credential/v1/credentials"
        $.get(targetURL, function (data) {
            console.log(data);
            // Fill the DOM of the verifier page with the received HTML
            // First remove all child elements
            $("#issuer_cred_list").empty();
            creds = data.payload;
            creds.forEach(get_issuer_cred_list);

        });
    }

    // Anybody except Passenger: display QR of a credential
    if (location.hash == "#genericDisplayQR") {
        console.log("In #genericDisplayQR script")

        genericDisplayQR();

    }

}


function get_issuer_cred_list (cred, index, array) {

    $("#issuer_cred_list").append(`<div class="card">
    <a onclick="transferViaQR('${cred}')">
        <header class="card-header">
            <p class="card-header-title">
                Diagnostic ID: ${cred}
            </p>
        </header>
    </a>
    </div>
    
    </br>`);

  }




// Initialize the DOM
$(async function () {

    // This function is called when a refresh is triggered in any other page
    // The application restarts from scratch, but the URL may have the page as a hash

    // Configure the local database
    localforage.config({
        name: "SafeIsland",
        storeName: "credentials"
    });

    // Try to retrieve an existing credential from the local storage
    // If no credential exists, store a testing one automatically
    // TODO: This logic is just for testing, and should be eliminated for production
    localforage.getItem('credential', function (err, jwt) {
        // Check if a credential already exists
//        if (jwt == null) {

            // There is not yet a credential, store a fake initial one just for testing
            updateCredStore(testJWT);

//        } else {

            // Credential exists. Log its value to help in debugging
//            console.log(jwt);

            // Update current JWT
//            currentPassengerJWT = jwt;

            // Update the current Credential in JSON
//            passengerCredential = covidCredFromJWTUnsecure(jwt);
          
//        }
    });

    // TEST TEST
    claims = await verifyJwtVc(testJWT);
    console.log("Verified claims");
    console.log(claims);

    // Execute logic on page enter for each different page
    process_page_enter();

});

// ***************************************************
// Support for app installation for off-line support
// ***************************************************

var deferredInstallPrompt = null;
const installButton = document.getElementById('butInstall');

installButton.addEventListener('click', installPWA);
window.addEventListener('beforeinstallprompt', saveBeforeInstallPromptEvent);

function saveBeforeInstallPromptEvent(evt) {
    console.log("saveBeforeInstallPromptEvent");

    // Save the prompt event for later when the user wants to click the Install button
    deferredInstallPrompt = evt;

    // Show the button only when the browser has generated this event
    // If the app is already installed, the browser does not generate the event
    $("#butInstall").show();

}

function installPWA(evt) {
    deferredInstallPrompt.prompt();

    // Hide install button, can only be invoked once per event
    $("#butInstall").hide();

    // Log the choice that the user made
    deferredInstallPrompt.userChoice
        .then((choice) => {
            if (choice.outcome === 'accepted') {
                console.log('User accepted the A2HS prompt', choice);
            } else {
                console.log('User dismissed the A2HS prompt', choice);
            }
            deferredInstallPrompt = null;
        });

}

// To log all events of app installation, even if the user does not click our Install button
window.addEventListener('appinstalled', logAppInstalled);
function logAppInstalled(evt) {
    console.log('SafeIsland app was installed.', evt);
}

// ********************************************************
// End of Support for app installation for off-line support
// ********************************************************


// ***************************************************
// Install service worker for better off-line support
// ***************************************************

// Check that service workers are supported
console.log("About to check for serviceworker availability")
if ('serviceWorker' in navigator) {
    // Use the window load event to keep the page load performant
    console.log("Detected. Adding listener")
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/sw.js');
    });
}
// ***************************************************
// End of Install service worker for better off-line support
// ***************************************************

// Stores the serialized JWT in local storage, and updates the JSON credential
// The JWT has been validated before, so no validation is performed here
function updateCredStore(jwt) {

    // Store the credential in indexdedDB replacing whatever is there
    localforage.setItem('credential', jwt).then(function (value) {

        // Get the credential from the jwt
        cred = covidCredFromJWTUnsecure(value);

        // Update the cached value in the global variable
        passengerCredential = cred;

        // Log the value stored, for debugging.
        console.log(value);

    }).catch(function (err) {
        // Log the error in the console
        console.log(err);
    });

}



// The hardcoded credential data (without the W3C VC wrapper format)
var credentialInitialJSON = {
    "ISSUER_ID": "9012345JK",
    "MERCHANT": {
        "MERCHANT_DATA": {
            "MERCHANT_ID": "did:elsi:VATES-A86212420",
            "MERCHANT_ADDR": "LANZAROTE AIRPORT T1"
        },
        "OPERATOR_DATA": {
            "OPERATOR_ID": "36926766J",
            "OPERATOR_CELL_PHONE_ID": "0034679815514",
            "OPERATOR_CELL_PHONE_GPS": "28.951146, -13.605760"
        },
        "DEVICE_ID": "34567867",
        "CARTRIDGE": {
            "CARTRIDGE_ID": "VRL555555666",
            "CARTRIDGE_DUE_DATE": "24/12/2021"
        }
    },
    "CITIZEN": {
        "NAME": "COSTA/ALBERTO",
        "ID_TYPE": "ID_CARD",
        "VALID_ID_NUMBER": "46106508H",
        "CITIZEN_CELL_PHONE": "0034678582354",
        "CITIZEN_EMAIL_ADDR": "externa21@gmail.com"
    },
    "DIAGNOSTIC_PASS_DATA": {
        "DIAGNOSTIC_NUMBER": "LE4RDS",
        "DIAGNOSTIC_TYPE": "VIROLENS SALIVA",
        "TIMESTAMP": "2020-10-15 11:05:47.659",
        "DIAGNOSIS": "FREE",
        "DIAGNOSIS_DUE_DATE": "2020-10-17 11:05:47.659",
        "DIAGNOSIS_QR": "",
        "DIAGNOSTIC_PASS_BCK_HASH": ""
    },
    "ACQUIRER_ID": ""
}

var credentialInitialJSON_Victor = {
    "ISSUER_ID": "9012345JK",
    "MERCHANT": {
        "MERCHANT_DATA": {
            "MERCHANT_ID": "did:elsi:VATES-A86212420",
            "MERCHANT_ADDR": "LANZAROTE AIRPORT T1"
        },
        "OPERATOR_DATA": {
            "OPERATOR_ID": "36926766J",
            "OPERATOR_CELL_PHONE_ID": "0034679815514",
            "OPERATOR_CELL_PHONE_GPS": "28.951146, -13.605760"
        },
        "DEVICE_ID": "34567867",
        "CARTRIDGE": {
            "CARTRIDGE_ID": "VRL555555666",
            "CARTRIDGE_DUE_DATE": "24/12/2021"
        }
    },
    "CITIZEN": {
        "NAME": "USOBIAGA/VICTOR",
        "ID_TYPE": "ID_CARD",
        "VALID_ID_NUMBER": "46106508H",
        "CITIZEN_CELL_PHONE": "0034699185267",
        "CITIZEN_EMAIL_ADDR": "victor.usobiaga@gmail.com"
    },
    "DIAGNOSTIC_PASS_DATA": {
        "DIAGNOSTIC_NUMBER": "LE4RDS",
        "DIAGNOSTIC_TYPE": "VIROLENS SALIVA",
        "TIMESTAMP": "2020-10-07 11:05:47.659",
        "DIAGNOSIS": "FREE",
        "DIAGNOSIS_DUE_DATE": "2020-10-08 11:05:47.659",
        "DIAGNOSIS_QR": "",
        "DIAGNOSTIC_PASS_BCK_HASH": ""
    },
    "ACQUIRER_ID": ""
}


// Populate the DOM fields with the credential data
function fillPassengerCredentialTemplate(cred) {
    console.log("In fillPassengerCredentialTemplate")

    // Citizen
    var citizen = cred["CITIZEN"];
    $("#CITIZEN_NAME").html(citizen["NAME"]);
    $("#CITIZEN_ID_TYPE").html(citizen["ID_TYPE"]);
    $("#CITIZEN_VALID_ID_NUMBER").html(citizen["VALID_ID_NUMBER"]);
    $("#CITIZEN_CELL_PHONE").html(citizen["CITIZEN_CELL_PHONE"]);
    $("#CITIZEN_EMAIL_ADDR").html(citizen["CITIZEN_EMAIL_ADDR"]);

    // Diagnostic data
    var diag = cred["DIAGNOSTIC_PASS_DATA"];
    $("#DIAGNOSTIC_NUMBER").html(diag["DIAGNOSTIC_NUMBER"]);
    $("#DIAGNOSTIC_TYPE").html(diag["DIAGNOSTIC_TYPE"]);
    $("#TIMESTAMP").html(diag["TIMESTAMP"]);
    $("#DIAGNOSIS").html(diag["DIAGNOSIS"]);

    // Merchant
    var merch = cred["MERCHANT"];
    $("#MERCHANT_ID").html(merch["MERCHANT_DATA"]["MERCHANT_ID"]);
    $("#MERCHANT_ADDR").html(merch["MERCHANT_DATA"]["MERCHANT_ADDR"]);

    $("#OPERATOR_ID").html(merch["OPERATOR_DATA"]["OPERATOR_ID"]);
    $("#OPERATOR_CELL_PHONE_ID").html(merch["OPERATOR_DATA"]["OPERATOR_CELL_PHONE_ID"]);
    $("#OPERATOR_CELL_PHONE_GPS").html(merch["OPERATOR_DATA"]["OPERATOR_CELL_PHONE_GPS"]);

    $("#OPERATOR_CELL_PHONE_ID").html(merch["OPERATOR_DATA"]["OPERATOR_CELL_PHONE_ID"]);
    $("#OPERATOR_CELL_PHONE_GPS").html(merch["OPERATOR_DATA"]["OPERATOR_CELL_PHONE_GPS"]);

    $("#DEVICE_ID").html(merch["DEVICE_ID"]);

    $("#CARTRIDGE_ID").html(merch["CARTRIDGE"]["CARTRIDGE_ID"]);
    $("#CARTRIDGE_DUE_DATE").html(merch["CARTRIDGE"]["CARTRIDGE_DUE_DATE"]);

}

// Call the server to verify a W3C VC in JWT serialized format
async function verifyJwtVc(jwt) {

    console.log(jwt);

    // Build the URL of the server to resolve the DID
//    var targetURL = window.location.origin + "/api/verifiable-credential/v1/verifiable-credential-validations"
    var targetURL = apiHost + "/api/verifiable-credential/v1/verifiable-credential-validations"

    // Build the body of the request
    body = JSON.stringify({payload: jwt})

    try {
        claims = await $.post(targetURL, body);
        console.log("W3C VC VERIFICATION SUCCESSFUL");
        return claims;
    } catch (error) {
        console.error("===== FAILED W3C VC VERIFICATION =====");
    }

}



function verifyDID(inputDID) {

    console.log(inputDID);

    // Build the URL of the server to resolve the DID
//    var targetURL = window.location.origin + "/api/did/v1/identifiers/" + inputDID
    var targetURL = apiHost + "/api/did/v1/identifiers/" + inputDID

    // Use the URL to get the DID Document from server
    $.get(targetURL, function (data) {

        // The actual data is inside a "payload" entry in the response
        console.log(data.payload);
        didDoc = data.payload;

        // Get the Merchant DID from inside the received data
        receivedDID = didDoc.id;

        // Log the merchant DID inside the received data
        console.log(receivedDID);

        // Check for equality
        if (inputDID == receivedDID) {
            console.log("VERIFICATION SUCCESSFUL");
        } else {
            console.log("ERROR: DIDs DO NOT MATCH");
        }

    }, "json");

}

// Populate the DOM fields with the result of credential data
function fillReceivedCredentialTemplate(cred) {
    console.log("In fillReceivedCredentialTemplate");
    console.log(cred);


    var merchant_DID = cred["MERCHANT"]["MERCHANT_DATA"]["MERCHANT_ID"];
//    verifyDID(merchant_DID)


    // Citizen
    var citizen = cred["CITIZEN"];
    $("#V_CITIZEN_NAME").html(citizen["NAME"]);
    $("#V_CITIZEN_ID_TYPE").html(citizen["ID_TYPE"]);
    $("#V_CITIZEN_VALID_ID_NUMBER").html(citizen["VALID_ID_NUMBER"]);
    $("#V_CITIZEN_CELL_PHONE").html(citizen["CITIZEN_CELL_PHONE"]);
    $("#V_CITIZEN_EMAIL_ADDR").html(citizen["CITIZEN_EMAIL_ADDR"]);

    // Diagnostic data
    var diag = cred["DIAGNOSTIC_PASS_DATA"];
    $("#V_DIAGNOSTIC_NUMBER").html(diag["DIAGNOSTIC_NUMBER"]);
    $("#V_DIAGNOSTIC_TYPE").html(diag["DIAGNOSTIC_TYPE"]);
    $("#V_TIMESTAMP").html(diag["TIMESTAMP"]);
    $("#V_DIAGNOSIS").html(diag["DIAGNOSIS"]);

    // Merchant
    var merch = cred["MERCHANT"];
    $("#V_MERCHANT_ID").html(merch["MERCHANT_DATA"]["MERCHANT_ID"]);
    $("#V_MERCHANT_ADDR").html(merch["MERCHANT_DATA"]["MERCHANT_ADDR"]);

    $("#V_OPERATOR_ID").html(merch["OPERATOR_DATA"]["OPERATOR_ID"]);
    $("#V_OPERATOR_CELL_PHONE_ID").html(merch["OPERATOR_DATA"]["OPERATOR_CELL_PHONE_ID"]);
    $("#V_OPERATOR_CELL_PHONE_GPS").html(merch["OPERATOR_DATA"]["OPERATOR_CELL_PHONE_GPS"]);

    $("#V_OPERATOR_CELL_PHONE_ID").html(merch["OPERATOR_DATA"]["OPERATOR_CELL_PHONE_ID"]);
    $("#V_OPERATOR_CELL_PHONE_GPS").html(merch["OPERATOR_DATA"]["OPERATOR_CELL_PHONE_GPS"]);

    $("#V_DEVICE_ID").html(merch["DEVICE_ID"]);

    $("#V_CARTRIDGE_ID").html(merch["CARTRIDGE"]["CARTRIDGE_ID"]);
    $("#V_CARTRIDGE_DUE_DATE").html(merch["CARTRIDGE"]["CARTRIDGE_DUE_DATE"]);

}


// Triggers from the #passengerDisplayCredential page change
function passengerDisplayCredential() {
    // Fill the template with the current value of the credential
    fillPassengerCredentialTemplate(passengerCredential);
}


var issuerCredentialID;

// This is triggered by the onclick event of each credential summary in the Issuer page
// We save the credential ID to display and switch to the genericDisplayQR page
// This page change will trigger the genericDisplayQR() function
// A page refresh by the user while in the genericDisplayQR page will trigger the same routine,
// using the saved variable (issuerCredentialID)
function transferViaQR(credentialID) {
    issuerCredentialID = credentialID;
    window.location = "#genericDisplayQR";
}

// Triggers from the #genericDisplayQR page change
function genericDisplayQR() {

    console.log("In genericDisplayQR")

    // Erase the display of the QR
    var qrelement = document.getElementById("genericPlaceholderQR");
    qrelement.innerText = "";

    // Build the URL to display in the QR
    // The passenger will scan the QR and request from the server the corresponding credential
//    var targetURLRead = window.location.origin + "/api/verifiable-credential/v1/" + issuerCredentialID
    var targetURLRead = apiHost + "/api/verifiable-credential/v1/" + issuerCredentialID
    var qrcode = new QRCode(
        document.getElementById("genericPlaceholderQR"),
        { text: targetURLRead }
    );

}

// Triggers from the #passengerDisplayQR page change
// This page generates the QR so it can be scanned by the Verifier
// In order to send big amounts of data, it writes the credential to the messaging server
// The QR contains the URL of the credential in the messaging server
// TODO: encrypt the credential before sending in order to improve privacy
function passengerDisplayQR() {

    // Get the target URL address to write the object to send
    // The address of the server is the host where we were loaded from
    var uid = generateUID();
//    targetURLWrite = "/api/write/" + uid;
    targetURLWrite = apiHost + "/api/write/" + uid;
    console.log(targetURLWrite)
    console.log(uid);

    // Erase the display of the QR
    qrelement = document.getElementById("placeholderQR");
    qrelement.innerText = "";

    body = {payload: currentPassengerJWT}
    console.log(body)

    // Write the object to the server
    var jqxhr = $.post(targetURLWrite, JSON.stringify(body), function (data) {
        console.log("Success writing");

        // If successful, build the URL to display in the QR
//        targetURLRead = window.location.origin + "/api/read/" + uid;
        targetURLRead = apiHost + "/api/read/" + uid;
        var qrcode = new QRCode(
            document.getElementById("placeholderQR"),
            { text: targetURLRead }
        );

    });

    // Process failure to write to the server
    jqxhr.fail(function (data) {
        qrelement.innerText = "Failed to write data to server";
    });

}


// Utility function to generate a (very) unique number
function generateUID() {
    // Get the number of milliseconds since midnight Jan 1, 1970
    n = Date.now();
    // Get a random number from 1 to 100.000
    r = Math.floor(Math.random() * 100000)
    // Combine both as a string, to make it difficult for two users making the request in the same millisecond
    uid = n.toString() + "-" + r.toString();
    return uid
}

// Utility function to draw a line in the canvas image
function drawLine(canvas, begin, end, color) {
    canvas.beginPath();
    canvas.moveTo(begin.x, begin.y);
    canvas.lineTo(end.x, end.y);
    canvas.lineWidth = 4;
    canvas.strokeStyle = color;
    canvas.stroke();
}

// These are global variables used by the background animation routine.
// They are set to the proper values by the QR scanning initialization routine
// They can be re-used by different pages, as only one scanning can be running at a given moment

// The HTML element where the video stream is going to be placed
var video = ""

// The HTML element where the video frames will be placed for analysis
var canvasElement = ""

// The canvas context with image data
var canvas = ""

// The output message with status of scanning
var verifierOutputMessage = ""

// The video stream object
var myStream = "";

// This suffix can be "Passenger" or "Verifier", depending on who calls the scanning function
var suffix = ""
var scan_page = ""

// Start the camera to scan the QR
// The scan can be used either by the Passenger or the Verifier
async function initiateQRScanning(_suffix) {

    // The received suffix identifies the caller
    // The received parameter is a suffix that has to be appended to all identifiers,
    // to make them unique across pages
    suffix = _suffix;

    // The HTML element where the video frames will be placed for analysis
    canvasElement = document.getElementById("canvasQR" + suffix);

    // Get the canvas context with image data
    canvas = canvasElement.getContext("2d");

    // The output message with status of scanning
    verifierOutputMessage = document.getElementById("outputMessage" + suffix);

    // The name of the page where scanning happens
    scan_page = "#QRScan" + suffix;

    // Disable the Decode button
    $("#qrscandecode" + suffix).hide();

    // Create the HTML element to place the video stream
    video = document.createElement("video");

    // Make sure that the canvas element is hidden for the moment
    canvasElement.hidden = true;

    // Display a message while we have not detected anything
    verifierOutputMessage.innerText = "Waiting for QR .........";

    // Request permission from user to get the video stream
    // Use "facingMode: environment" to attempt to get the main camera on phones
    navigator.mediaDevices.getUserMedia({ video: { facingMode: "environment" } }).then(function (stream) {
        // Store the stream in global variable for later
        myStream = stream;

        // Connect the video stream to the "video" element in the page
        video.srcObject = stream;
        video.setAttribute("playsinline", true); // required to tell iOS safari we don't want fullscreen
        video.play();

        // Call the "tick" function on the next animation interval
        requestAnimationFrame(QRtick);
    });

    // Switch to the Verifier screen
    window.location = scan_page;

}

// This function is called periodically until we get a result from the scan
// We use global variables to know the context on which it was called
async function QRtick() {

    // Ckeck if we are running in the context of the page that initiated scanning
    if (window.location.hash != scan_page) {
        // The user navigated out of the scan page, should stop using the camera
        stopMediaTracks(myStream);
        return
    }

    // Try to scan the QR code only when video stream is ready
    if (video.readyState !== video.HAVE_ENOUGH_DATA) {
        // We are not yet ready
        // Request to be called again in next frame
        requestAnimationFrame(QRtick);

        // Exit from the function
        return
    }

    // Video is ready, hide loading message and display canvas and output elements
    canvasElement.hidden = false;

    // Set the canvas size to match the video stream
    canvasElement.height = video.videoHeight;
    canvasElement.width = video.videoWidth;

    // Get a video frame and decode an image data using the canvas element
    canvas.drawImage(video, 0, 0, canvasElement.width, canvasElement.height);
    var imageData = canvas.getImageData(0, 0, canvasElement.width, canvasElement.height);

    // Try to decode the image as a QR code
    var code = jsQR(imageData.data, imageData.width, imageData.height, {
        inversionAttempts: "dontInvert",
    });

    // If unsuccessful, exit requesting to be called again at next animation frame
    if (!(code)) {

        // Request to be called again in next frame
        requestAnimationFrame(QRtick);

        // Exit from the function
        return
    }

    // We have a valid QR
    // If successful, draw a red square in the image for the detected QR
//    drawLine(canvas, code.location.topLeftCorner, code.location.topRightCorner, "#FF3B58");
//    drawLine(canvas, code.location.topRightCorner, code.location.bottomRightCorner, "#FF3B58");
//    drawLine(canvas, code.location.bottomRightCorner, code.location.bottomLeftCorner, "#FF3B58");
//    drawLine(canvas, code.location.bottomLeftCorner, code.location.topLeftCorner, "#FF3B58");


    // Hide the picture
    canvasElement.hidden = true;

    // The data in the QR should be a URL that we have to call
    targetURL = code.data;
    console.log(code);

    // For debugging: display in the page the result of the scan
    verifierOutputMessage.innerText = targetURL;

    // The content of the QR should be a URL where the real object is stored
    // Use the URL to get the object from the server

    data = "";
    try {
        data = await $.get(targetURL);
        console.log("Received data from Messaging server");
    } catch (error) {
        console.error("===== Error gettting data from Messaging server =====");
    }

    // We have received a JWT in the payload field of the result body
    jwt = data.payload;

    // Log the receved data
    console.log(jwt);

    // Display in the page the object received.
    verifierOutputMessage.innerText = data.payload;

    // Verify the jwt including the signature
    claims = await  verifyJwtVc(jwt);

    // Extract the credential
    cred = covidCredFromJWTUnsecure(jwt);

    // Show the Decode button
    $("#qrscandecode" + suffix).show();

    // If caller was Passenger, we have received a new credential that should be stored in the database
    if (suffix == "Passenger") {

        updateCredStore(jwt);

    }

    // Fill the template in the decoded received credential page
    fillReceivedCredentialTemplate(cred);

    // Switch to the presentation of results
    if (suffix == "Verifier") {
        window.location = "#verifierresults"
    }
    if (suffix == "Passenger") {
        window.location = "#verifierresults"
    }

    // Stop the media stream
    stopMediaTracks(myStream);

    return
}

function stopMediaTracks(stream) {
    // Stop the media stream
    tracks = stream.getTracks();
    tracks[0].stop();

    return
}



function btoaUrl (input) {

    // Encode using the standard Javascript function
    astr = btoa(input)

    // Replace non-url compatible chars with base64 standard chars
    astr = astr.replace(/\+/g, '-').replace(/\//g, '_');

    return astr;
}

function atobUrl (input) {

    // Replace non-url compatible chars with base64 standard chars
    input = input.replace(/-/g, '+').replace(/_/g, '/');

    // Decode using the standard Javascript function
    bstr = atob (input)

    return bstr;
}

function decodeJWT(jwt) {
    // jwt is a string
    // Split the input in three components using the dots "." as separator
    components = jwt.split(".");

    if (components.length != 3) {
        console.error("Malformed JWT");
        return;
    }

    return {
        header: JSON.parse(atobUrl(components[0])),
        body: JSON.parse(atobUrl(components[1]))
    }

}

function covidCredFromJWTUnsecure(jwt) {
    console.log(typeof jwt);

    components = decodeJWT(jwt);
    cred = components.body.vc.credentialSubject.covidTestResult;
    return cred;

}