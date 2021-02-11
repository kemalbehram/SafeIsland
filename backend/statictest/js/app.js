//"use strict";

// import { webcrypto as crypto} from "crypto";

// The host where the API is hosted
var serverSameOrigin = window.location.origin;
var serverSafeIsland = "https://safeisland.hesusruiz.org";
var apiHost = null;

// This variable holds at all times in memory the value of the current credential
//var passengerCredential = credentialInitialJSON;
//var testJWT = "eyJhbGciOiJFUzI1NksiLCJraWQiOiJkaWQ6ZWxzaTpWQVRFUy1BODYyMTI0MjAja2V5LXZlcmlmaWNhdGlvbiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE2MDc5ODQ4NDEsImlhdCI6MTYwNzU1Mjg0MSwiaXNzIjoiZGlkOmVsc2k6VkFURVMtQTg2MjEyNDIwIiwibmJmIjoxNjA3NTUyODQxLCJzdWIiOiI0NjEwNjUwOEgiLCJ2YyI6eyJAY29udGV4dCI6WyJodHRwczovL3d3dy53My5vcmcvMjAxOC9jcmVkZW50aWFscy92MSIsImh0dHBzOi8vYWxhc3RyaWEuZ2l0aHViLmlvL2lkZW50aXR5L2NyZWRlbnRpYWxzL3YxIiwiaHR0cHM6Ly9zYWZlaXNsYW5kLm9yZy8ud2VsbC1rbm93bi93M2MtY292aWQtdGVzdC92MSJdLCJjcmVkZW50aWFsU3ViamVjdCI6eyJjb3ZpZFRlc3RSZXN1bHQiOnsiQUNRVUlSRVJfSUQiOiIiLCJDSVRJWkVOIjp7IkNJVElaRU5fQ0VMTF9QSE9ORSI6IjAwMzQ1ODQ5OTY1MzIiLCJDSVRJWkVOX0VNQUlMX0FERFIiOiJwYXNzZW5nZXJAZ21haWwuY29tIiwiSURfVFlQRSI6IklEX0NBUkQiLCJOQU1FIjoiQ09TVEEvQUxCRVJUTyIsIlZBTElEX0lEX05VTUJFUiI6IjQ2MTA2NTA4SCJ9LCJESUFHTk9TVElDX1BBU1NfREFUQSI6eyJESUFHTk9TSVMiOiJGUkVFIiwiRElBR05PU0lTX0RVRV9EQVRFIjoiMjAyMC0xMC0xNyAxMTowNTo0Ny42NTkiLCJESUFHTk9TSVNfUVIiOiIiLCJESUFHTk9TVElDX05VTUJFUiI6IkxFNFJEUyIsIkRJQUdOT1NUSUNfUEFTU19CQ0tfSEFTSCI6IiIsIkRJQUdOT1NUSUNfVFlQRSI6IlZJUk9MRU5TIFNBTElWQSIsIlRJTUVTVEFNUCI6IjIwMjAtMTAtMTUgMTE6MDU6NDcuNjU5In0sIklTU1VFUl9JRCI6IjkwMTIzNDVKSyIsIk1FUkNIQU5UIjp7IkNBUlRSSURHRSI6eyJDQVJUUklER0VfRFVFX0RBVEUiOiIyNC8xMi8yMDIxIiwiQ0FSVFJJREdFX0lEIjoiVlJMNTU1NTU1NjY2In0sIkRFVklDRV9JRCI6IjM0NTY3ODY3IiwiTUVSQ0hBTlRfREFUQSI6eyJNRVJDSEFOVF9BRERSIjoiTEFOWkFST1RFIEFJUlBPUlQgVDEiLCJNRVJDSEFOVF9JRCI6ImRpZDplbHNpOlZBVEVTLUE4NjIxMjQyMCJ9LCJPUEVSQVRPUl9EQVRBIjp7Ik9QRVJBVE9SX0NFTExfUEhPTkVfR1BTIjoiMjguOTUxMTQ2LCAtMTMuNjA1NzYwIiwiT1BFUkFUT1JfQ0VMTF9QSE9ORV9JRCI6IjAwMzQ2Nzk4MTU1MTQiLCJPUEVSQVRPUl9JRCI6IjM2OTI2NzY2SiJ9fX0sImxldmVsT2ZBc3N1cmFuY2UiOjJ9LCJ0eXBlIjpbIlZlcmlmaWFibGVDcmVkZW50aWFsIiwiQWxhc3RyaWFWZXJpZmlhYmxlQ3JlZGVudGlhbCIsIlNhZmVJc2xhbmRDb3ZpZFRlc3RSZXN1bHQiXX19.KK4iGxfajtVMf8KsGdFuWD6F3xHnQcj5bj7DQgI_hDCHSXw7HpA1uMpGDyRK2LKIDgji1qixpmMj7oUUHsiEeQ"
//var testJWT = "eyJhbGciOiJFUzI1NksiLCJraWQiOiJkaWQ6ZWxzaTpWQVRFUy1BODYyMTI0MjAja2V5LXZlcmlmaWNhdGlvbiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE2MTMyMDQwMjYsImlhdCI6MTYxMjY4NTYyNiwiaXNzIjoiZGlkOmVsc2k6VkFURVMtQTg2MjEyNDIwIiwic3ViIjoiNDYxMDY1MDhIIiwidXVpZCI6ImU4MmFmMzY3YWJhNDQ5ZmZiOWJkODU4NDIzNTRiMDFiIiwidmMiOnsiQGNvbnRleHQiOlsiaHR0cHM6Ly93d3cudzMub3JnLzIwMTgvY3JlZGVudGlhbHMvdjEiLCJodHRwczovL2FsYXN0cmlhLmdpdGh1Yi5pby9pZGVudGl0eS9jcmVkZW50aWFscy92MSIsImh0dHBzOi8vc2FmZWlzbGFuZC5vcmcvLndlbGwta25vd24vdzNjLWNvdmlkLXRlc3QvdjEiXSwiY3JlZGVudGlhbFN1YmplY3QiOnsiY292aWRUZXN0UmVzdWx0Ijp7ImFuYWx5c2lzIjp7ImRhdGUiOjE2MTI2ODU2MjYsImlkIjoiTEU0UkRTIiwicmVzdWx0IjoiRlJFRSIsInR5cGUiOiJWaXJvbGVucyIsInZlciI6IjEifSwiY29tbWVudHMiOiJUaGVzZSBhcmUgc29tZSBjb21tZW50cyIsImxhYiI6eyJhZGRyZXNzIjoiTm8gUHJvYmxlbSBTdHJlZXQgMTIzLCBQZXJmZWN0IENpdHksIFZhbGhhbGxhIiwibmFtZSI6IlBlcmZlY3QgSGVhbHRoIHBsYyIsInBob25lIjoiKzM0NjM1NDAwNDAifSwicGF0aWVudCI6eyJkb2IiOiIyNy0wNC0xOTgyIiwiaWRudW1iZXIiOiI0NjEwNjUwOEgiLCJuYW1lIjoiQ09TVEEvQUxCRVJUTyJ9fSwiaXNzdWVkQXQiOlsiYWxhc3RyaWEucmVkdCJdLCJsZXZlbE9mQXNzdXJhbmNlIjoyfSwidHlwZSI6WyJWZXJpZmlhYmxlQ3JlZGVudGlhbCIsIkFsYXN0cmlhVmVyaWZpYWJsZUNyZWRlbnRpYWwiLCJTYWZlSXNsYW5kQ292aWRUZXN0UmVzdWx0Il19fQ.YJUWbf-A8Lsrg1kJ4zZwdCt9xnOpCo0f84R0LSuWS6eH5kmI0OBAa-4dtJJIOjPMk0yLJrrcLvlzcYRP2KXfnQ"
var testJWT = "eyJhbGciOiJFUzI1NksiLCJraWQiOiJkaWQ6ZWxzaTpWQVRFUy1YMTIzNDU2NzhYI2tleS12ZXJpZmljYXRpb24iLCJ0eXAiOiJKV1QifQ.eyJleHAiOjE2MTM1NDEwNDYsImlhdCI6MTYxMzAyMjY0NiwiaXNzIjoiZGlkOmVsc2k6VkFURVMtWDEyMzQ1Njc4WCIsInN1YiI6Ijg3MzM1NjIwTCIsInV1aWQiOiIwZmQzOTEwZTUwODY0MWE0YmY5ZjNjYWMyNDBjY2RiMCIsInZjIjp7IkBjb250ZXh0IjpbImh0dHBzOi8vd3d3LnczLm9yZy8yMDE4L2NyZWRlbnRpYWxzL3YxIiwiaHR0cHM6Ly9hbGFzdHJpYS5naXRodWIuaW8vaWRlbnRpdHkvY3JlZGVudGlhbHMvdjEiLCJodHRwczovL3NhZmVpc2xhbmQub3JnLy53ZWxsLWtub3duL3czYy1jb3ZpZC10ZXN0L3YxIl0sImNyZWRlbnRpYWxTY2hlbWEiOnsiaWQiOiJ2YWNjaW5hdGlvbkNyZWRlbnRpYWwiLCJ0eXBlIjoiSnNvblNjaGVtYVZhbGlkYXRvcjIwMTgifSwiY3JlZGVudGlhbFN1YmplY3QiOnsiaXNzdWVkQXQiOlsicmVkdC5hbGFzdHJpYSJdLCJsZXZlbE9mQXNzdXJhbmNlIjoyLCJ2YWNjaW5hdGlvbkNyZWRlbnRpYWwiOnsiY29tbWVudHMiOiJUaGVzZSBhcmUgc29tZSBjb21tZW50cyIsInBhdGllbnQiOnsiZG9iIjoiMTEtMDUtMTk3NyIsImlkbnVtYmVyIjoiODczMzU2MjBMIiwibmFtZSI6IlBFUkVaL1BFUklDTyJ9LCJ2YWNjaW5hdGlvbiI6eyJhdXRoX2hvbGRlciI6IlBmaXplciBCaW9OVGVjaCIsImJhdGNoIjoiQUg2NTM3NFUiLCJjZW50ZXIiOiJQZXJmZWN0IEhlYWx0aCBwbGMiLCJjb3VudHJ5IjoiRVMiLCJkYXRlIjoxNjEzMDIyNjQ2LCJkaXNlYXNlIjoiQ09WSUQxOSIsImRvc2VfbnVtYmVyIjoiMSIsIm5leHRfZGF0ZSI6MTYxNTYxNDY0NiwicHJvZHVjdCI6IkNPTUlSTkFUWSBjb25jZW50cmF0ZSBmb3IgZGlzcGVyc2lvbiBmb3IgaW5qZWN0aW9uIiwicHJvZmVzc2lvbmFsIjoiRVM0NjEwNjUwOEgiLCJ0b3RhbF9kb3NlcyI6IjIiLCJ2YWNjaW5lIjoiMTExOTM0OTAwNyB8IENPVklELTE5IG1STkEgdmFjY2luZSJ9fX0sInR5cGUiOlsiVmVyaWZpYWJsZUNyZWRlbnRpYWwiLCJBbGFzdHJpYVZlcmlmaWFibGVDcmVkZW50aWFsIiwiU2FmZUlzbGFuZFZhY2NpbmF0aW9uQ3JlZGVudGlhbCJdfX0.1kVMhiI64XIHZ9KMrcAGIdKPBChEU2Xbwf560XyxmbpDtgTt-S8cP7V9QySWq3HWFB70lk47X_KPussswPWLNA"

var currentPassengerJWT = testJWT;

var passengerCredential = covidCredFromJWTUnsecure(currentPassengerJWT);
var displayCredentialTemplate = "";
var displayVaccinationCredentialTemplate = "";

// This routine dispatches the appropriate functions when the user navigates among pages
// When user navigates between pages of the application, the system generates "hashchange" events
// We install a listener for those changes and dispatch the event to the associated function per page
window.addEventListener("hashchange", function () {

    // Execute logic on page enter for each different page
    process_page_enter();

});


function menuClose() {
    $(".navbar-burger").removeClass("is-active");
    $(".navbar-menu").removeClass("is-active");
}

async function process_page_enter() {

    // Handle page transition
    // When user navigates to a page, we should hide all other pages and show the target one

    // Hide all pages of the application. Later we unhide the one we are entering
    $(".jrmpage").hide();
    $("#loader").hide();
    menuClose();

    // Show a single page: the one we are entering (if hash is non-null) or the home otherwise
    newPage = location.hash
    if (newPage.length == 0) {
        newPage = "#homePage"
    }
    $(newPage).show();

    // Invoke the registered function on page enter
    if (pages[newPage] != null) {
        pages[newPage]();
    }

}

// The local stores
var dbCredentials = null;
var dbSettings = null;

// DOM is fully loaded and safe to manipulate
// We can start th einitializetion of the system
$(async function () {

    // This function is called when a refresh is triggered in any other page
    // The application restarts from scratch, but the URL may have the page as a hash

    // Navigation bar: Register the click events on the navbar burger icon
    $(".navbar-burger").click(function() {

        // Toggle the "is-active" class on both the "navbar-burger" and the "navbar-menu"
        $(".navbar-burger").toggleClass("is-active");
        $(".navbar-menu").toggleClass("is-active");

    });

    // Configure the local database instances for credentials and settings
    dbCredentials = localforage.createInstance({
        name: "SafeIsland",
        storeName: "credentials"
    });
    dbSettings = localforage.createInstance({
        name: "SafeIsland",
        storeName: "settings"
    });

    // Handle one-time initialization when the user executes for the first time the app
    await performOneTimeInitialization();

    // Get or initialize the DID and symmetric encription key
    var didData = await getOrGenerateDID();
    console.log(didData.did);

    // Compile the Display Credential Page template
    compileCredentialTemplates();
    console.log("Templates compiled")

//    var displayCredentialSource = document.getElementById("covidTestResult").innerHTML;
//    displayCredentialTemplate = Handlebars.compile(displayCredentialSource);

//    var displayVaccinationCredentialSource = document.getElementById("vaccinationCredential").innerHTML;
//    displayVaccinationCredentialTemplate = Handlebars.compile(displayVaccinationCredentialSource);

    // Show current page and execute logic on page transition
    process_page_enter();

});


// Initialize the app when the user downloads the application for the first time,
// or when a factory reset is performed by the user
// The function is safe to be called many times
async function performOneTimeInitialization() {
    console.log("Performing OneTime Initialization")

    // Check if this is the first time that the user downloads the app
    // There is a persistent flag in the local storage
    var alreadyInitialized = await getSetting("initialized");
    if (alreadyInitialized == true) {

        // Initialize global variable with the default address for sending and receiving messages
        apihost = await getSetting("apiHost");
        if (apiHost == null) {
            apiHost = serverSameOrigin;
            await updateSetting("apiHost", apiHost);
        }

    }

    await updateSetting("initialized", true);
}

// Generate the Peer DID for the user
async function getOrGenerateDID() {

    // Check if we already have the peerDID in the database
    var didData = await getSetting("didData");
    if (didData == null) {
        didData = await generateDidPeer();
        console.log(didData.did);
        console.log(didData.keyPair);
        await updateSetting("didData", didData);
    }

    return didData;    

}

// *******************************
// *******************************
// Handle the Settings table
//

async function getSetting(name) {
    setting = null;
    try {
        setting = await dbSettings.getItem(name);
    } catch (err) {
        console.log(err);
    }
    return setting;
}

async function updateSetting(name, value) {
    
    try {
        setting = await dbSettings.setItem(name, value);
    } catch (err) {
        console.log(err);
        return null;
    }
    return setting;
}

async function resetAllSettings() {
    try {
        await dbSettings.clear();
    } catch (err) {
        console.log(err);
    }
}

//
// End Handle the Settings table
// *******************************
// *******************************


// ***************************************************
// ***************************************************
// Support for app installation for off-line support
//

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

//
// End of Support for app installation for off-line support
// ********************************************************
// ********************************************************


// ***************************************************
// ***************************************************
// Install service worker for better off-line support
//

// Check that service workers are supported
console.log("About to check for serviceworker availability")
if ('serviceWorker' in navigator) {
    // Use the window load event to keep the page load performant
    console.log("Detected. Adding listener")
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/sw.js');
    });
}

//
// End of Install service worker for better off-line support
// ***************************************************
// ***************************************************


// **************************************************
// Local database management
// **************************************************


// Stores the serialized JWT in local storage, and updates the JSON credential
// The JWT has been validated before, so no validation is performed here
async function dbCredentialsSetItem(jwt) {

    // Create the key with the current time
    key = Date.now().toString();

    // Store the credential in indexdedDB
    await dbCredentials.setItem(key, jwt);

    // Decode from JWT format to JSON. Assumes JWT was already verified
    passengerCredential = covidCredFromJWTUnsecure(jwt);

}


// Resets the databases
async function resetCredStore() {

    // Log the current number of records in both Credential and Settings databases
    numCreds = await dbCredentials.length();
    numSettings = await dbSettings.length();
    console.log(numCreds, numSettings);

    // delete all records in databases
    await dbCredentials.clear();
    await dbSettings.clear();

    console.log("Credential and Settings databases erased!");
}


// Call the server to verify a W3C VC in JWT serialized format
async function verifyJwtVc(jwt) {

    console.log(jwt);

    // The URL of the server to resolve the DID
    var targetURL = apiHost + "/api/verifiable-credential/v1/verifiable-credential-validations"

    // Build the body of the request
    body = JSON.stringify({ payload: jwt })

    // Perform validation as a POST request
    try {
        claims = await $.post(targetURL, body);
        console.log("W3C VC VERIFICATION SUCCESSFUL");
        return claims;
    } catch (error) {
        console.error("===== FAILED W3C VC VERIFICATION =====");
        return;
    }

}

// Perform DID Resolution, which is also a DID verification
function verifyDID(inputDID) {

    console.log(inputDID);

    // Build the URL of the server to resolve the DID
    var targetURL = apiHost + "/api/did/v1/identifiers/" + inputDID

    // Use the URL to get the DID Document from server
    $.get(targetURL, function (data) {

        // The actual data is inside a "payload" entry in the response
        console.log(data.payload);
        didDoc = data.payload;

        // Get the Issuer DID from inside the received data
        receivedDID = didDoc.id;

        // Log the Issuer DID inside the received data
        console.log(receivedDID);

        // The DID that we resolved should be the same as the one inside the DID Document
        if (inputDID == receivedDID) {
            console.log("VERIFICATION SUCCESSFUL");
        } else {
            console.log("ERROR: DIDs DO NOT MATCH");
        }

    }, "json");

}


// Triggers from the #displayCredentialPage page change
// Generates the HTML corresponding to the current credential and sets it in the received page element
async function displayCredentialPage(pageElementName) {

    // Retrieve the plain credential to display. This is already decoded (no JWT)
    var passengerCredential = await dbSettings.getItem("passengerCredential");

    // get the credential schema to see what template to apply when displaying
    var schema = passengerCredential['body']['vc']['credentialSchema']['id']

    // get the corresponding compiled Handlebars template
    var template = getTemplate(schema)

    // Generate the HTML using the "body" field of the credential
    var html = template(passengerCredential["body"])

    // Set the generated HTML into the page element
    document.getElementById(pageElementName).innerHTML = html

}

// Triggers from the #displayCredentialPage page change
async function displayReceivedCredentialPage() {

    // Retrieve the plain credential to display
    var passengerCredential = await dbSettings.getItem("passengerCredential");

    // Fill the template with the current value of the credential
    var html = displayCredentialTemplate(passengerCredential["body"]);
    document.getElementById("displayReceivedCredentialPlaceholder").innerHTML = html

}


// This is triggered by the onclick event of each credential summary in the Issuer page
// We save the credential ID to display and switch to the genericDisplayQR page
// This page change will trigger the genericDisplayQR() function
// A page refresh by the user while in the genericDisplayQR page will trigger the same routine,
// using the saved variable (issuerCredentialID)
async function transferViaQR(credentialID) {
    console.log("In transferViaQR")

    // Build the URL to display in the QR
    // The passenger will scan the QR and request from the server the corresponding credential
    var targetURLRead = apiHost + "/api/verifiable-credential/v1/" + credentialID

    data = "";
    try {
        data = await $.get(targetURLRead);
        console.log("Received credential from Issuer");
    } catch (error) {
        console.error("===== Error gettting credential from Issuer =====");
        alert("Error gettting credential from Issuer")
        return;
    }

    // We have received a JWT in the payload field of the result body
    jwt = data.payload;

    // Extract the credential
    try {
        cred = decodeJWT(jwt);
        await dbSettings.setItem("passengerCredential", cred);
    } catch (error) {
        console.error(error);
        alert("Error decoding credential")
        return;
    }
    
    // Transfer control to the page for display
    window.location = "#displayReceivedCredentialPage";

}

// Triggers from the #passengerDisplayQR page change
// This page generates the QR so it can be scanned by the Verifier
// In order to send big amounts of data, it writes the credential to the messaging server
// The QR contains the URL of the credential in the messaging server
// TODO: encrypt the credential before sending in order to improve privacy

var QRpieces = []
var qrelement = ""
var elwidth = 0

async function passengerDisplayQR(credentialJWT) {

    qrelement = document.getElementById("placeholderQR");
    realqrelement = document.getElementById("realqrcontent");
    $("#placeholderQR").hide()
    
    elwidth = Math.floor($(realqrelement).width())
    console.log("Element width:", elwidth)

    console.log("JWT Legnth: ", credentialJWT.length)

    // Calculate a number of pieces to divide the whole JWT
    var totalLength = credentialJWT.length
    var targetPieceSize = 300

    var numPieces = Math.floor(totalLength / targetPieceSize)
    var remainder = totalLength % targetPieceSize
    var extraChars = Math.ceil(remainder / numPieces)

    var pieceSize = targetPieceSize + extraChars
    console.log(pieceSize)
    // Divide the credential string into pieces
//    var pieceSize = 300
    QRpieces = credentialJWT.match(new RegExp('.{1,' + pieceSize + '}', 'g'));

    console.log(QRpieces)

    await QRDisplayTick(0)

    return

}



async function QRDisplayTick(index) {

    // Ckeck if we are running in the context of the page that initiated scanning
    if (window.location.hash != "#passengerDisplayQR") {
        // The user navigated out of the passengerDisplayQR page, should stop displaying QR
        // Return without activating the callback again, so it will stop
        console.log("Exiting QR timer")
        return
    }

    // Erase the display of the QR
    qrelement.innerText = "";

    numPieces = QRpieces.length
    // Get the current piece to display
    var body = `${numPieces}|${index}|${QRpieces[index]}`

    // Build the QR and display in the DOM element
    var qrcode = new QRCode(
        qrelement,                              // Place to display QR image
        {
            drawer: "canvas",
            height: elwidth,
            width: elwidth,
            text: body,  // Contents of the QR
            onRenderingStart:function(options){
            },
            onRenderingEnd:function(options, dataURL){
                var imageQR = document.getElementById('realplaceholderQR')
                imageQR.setAttribute(
                    'src', dataURL
                );
                $("#realplaceholderQR").width(elwidth)

            }
        }
    );

//    document.getElementById("passengerDisplayQRMessage").innerText = elwidth;


    // Set the next timer for displaying the netx piece of the QR
    var nextIndex = index + 1
    if (nextIndex >= QRpieces.length) {
        nextIndex = 0
    }
    setTimeout(QRDisplayTick, 300, nextIndex)

}







async function passengerDisplayQR_justURL(credentialJWT) {

    // Erase the display of the QR
    var qrelement = document.getElementById("placeholderQR");
    qrelement.innerText = "";

    // Check if there is something to display
    if (credentialJWT == null) {
        qrelement.innerText = "Nothing to display";
        return;
    }

    // Generate a unique ID to use for the URL link to the contents of the credential
    var uid = await generateUID();

    // Build the target URL address to write the object to send
    // The address of the server is the host where we were loaded from
    var targetURLWrite = apiHost + "/api/write/" + uid;
    console.log(targetURLWrite)

    // Build the data to send to the Secure Messaging Server
    var body = { payload: credentialJWT }

    // Write to the server
    try {
        await $.post(targetURLWrite, JSON.stringify(body));
        console.log("Success writing to Secure Message Server");
    } catch (error) {
        qrelement.innerText = "Failed to write data to server";
        console.error("FAILED to write to SMS: ", error);
        return;
    }

    // If successful, build the URL to display in the QR
    var qrcode = new QRCode(
        qrelement,                              // Place to display QR image
        {
            text: apiHost + "/api/read/" + uid  // Contents of the QR
        }
    );

}

async function passengerDisplayQR_justPII(credentialJWT) {

    // Erase the display of the QR
    var qrelement = document.getElementById("placeholderQR");
    qrelement.innerText = "";

    // Check if there is something to display
    if (credentialJWT == null) {
        qrelement.innerText = "Nothing to display";
        return;
    }

    // Get the credentials from the JWT
    var components = credentialJWT.split(".");

    if (components.length != 3) {
        console.error("Malformed JWT");
        return;
    }

    header = JSON.parse(atobUrl(components[0]))
    body = JSON.parse(atobUrl(components[1]))
    signature = components[2]

    var credential_type = "1234"

    // Create a minimal structure
    var body = `${credential_type}
${header.kid}
${body.exp}
${body.iat}
${body.sub}
${body.vc.credentialSubject.covidTestResult.CITIZEN.NAME}
${body.vc.credentialSubject.covidTestResult.DIAGNOSTIC_PASS_DATA.DIAGNOSTIC_NUMBER}
${signature}
`
    console.log(body)

    elwidth = $(qrelement).width()

    // If successful, build the URL to display in the QR
    var qrcode = new QRCode(
        qrelement,                              // Place to display QR image
        {
            height: elwidth,
            width: elwidth,
            text: body  // Contents of the QR
        }
    );

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
var prefix = ""
var scan_page = ""

// Start the camera to scan the QR
// The scan can be used either by the Passenger or the Verifier
async function initiateQRScanning(_prefix) {

    // The received suffix identifies the caller
    // The received parameter is a suffix that has to be appended to all identifiers,
    // to make them unique across pages
    prefix = _prefix
    scan_page = "#" + prefix;

    // The HTML element where the video frames will be placed for analysis
    canvasElement = document.getElementById(prefix + "Canvas");

    // Get the canvas context with image data
    canvas = canvasElement.getContext("2d");

    // The output message with status of scanning
    verifierOutputMessage = document.getElementById(prefix + "Message");

    // Disable the Decode button
    $(scan_page + "DecodeButton").hide();

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

        // Return without activating the callback again, so it will stop completely
        return
    }

    // Try to scan the QR code only when video stream is ready
    if (video.readyState !== video.HAVE_ENOUGH_DATA) {
        // We are not yet ready

        // Request to be called again in next frame
        requestAnimationFrame(QRtick);

        // Exit from the function until it will be called again
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

    // If we reached up to here, we have a valid QR

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
        // Stop the media stream
        stopMediaTracks(myStream);
        return
    }

    // We have received a JWT in the payload field of the result body
    jwt = data.payload;

    // Log the receved data
    console.log(jwt);

    // Verify the jwt including the signature (goes to the blockchain)
    claims = await verifyJwtVc(jwt);
    if (!claims) {
        // Set an error on the message field of the page
        verifierOutputMessage.innerText = "Error: verification failed!";
    }

    // Extract the credential
    cred = covidCredFromJWTUnsecure(jwt);

    // Show the Decode button
    $(scan_page + "DecodeButton").show();

    // If caller was Passenger, we have received a new credential that should be stored in the database
    if (scan_page == "#passengerQRScan") {

        await dbCredentialsSetItem(jwt);

    }

    // Fill the template in the decoded received credential page
    fillReceivedCredentialTemplate(cred);

    // Switch to the presentation of results
    window.location = "#displayReceivedQR"

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



function btoaUrl(input) {

    // Encode using the standard Javascript function
    astr = btoa(input)

    // Replace non-url compatible chars with base64 standard chars
    astr = astr.replace(/\+/g, '-').replace(/\//g, '_');

    return astr;
}

function atobUrl(input) {

    // Replace non-url compatible chars with base64 standard chars
    input = input.replace(/-/g, '+').replace(/_/g, '/');

    // Decode using the standard Javascript function
    bstr = atob(input)

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

    components = decodeJWT(jwt);
    cred = components.body.vc.credentialSubject.covidTestResult;
    return cred;

}


// Utility function to generate a cryptographically unique number
async function generateUID() {
    // Get the Crypto object (with support for IE11)
//    var cryptoObj = window.crypto || window.msCrypto;
    const array = new Uint32Array(2);
    crypto.getRandomValues(array);
    var UID = array[0].toString() + array[1].toString();
    console.log(`New UID: ${UID}`)
    return UID;
}

// Generate key fingerprint to use in DIDs and Key identifiers
// The format used here is for Peer DIDs (see spec for details)
async function keyPairFingerprint(keyPair) {

    // Get the Public key
    let PK = keyPair.publicKey;

    // Export the Public Key in a byte array
    let PKexported = await crypto.subtle.exportKey("raw", PK);
    let byteView = new Uint8Array(PKexported);

    // Create a bigger array to concatenate with the multicodec value
    let wholeArray = new Uint8Array(byteView.length + 2);

    // The multicodec for P-256 is 0x1200
    const multicodecP256 = 0x1200;
    wholeArray[0] = 0x12;
    wholeArray[1] = 0x00;

    // Concatenate the public key raw values
    wholeArray.set(byteView, 2);

    // Encode in Base58 the result of concatenation
    let b58encoded = to_b58(wholeArray);

    let fingerprint = `0z${b58encoded}`;

    return fingerprint;

}

// Generate a DID in format of Peer DID (see spec for details)
// The key used is Elliptic but restricted to the one supported by browsers
// in the standard crypto Subtle subsystem
async function generateDidPeer() {

    // Ask browser to create a key pair with the p256 curve
    var keyPair = await crypto.subtle.generateKey(
        {
            name: "ECDSA",
            namedCurve: "P-256"
        },
        true,
        ["sign", "verify"]
    );

    // Export both keys to the JWK format (see spec for details)
    var privateKeyJWK = await crypto.subtle.exportKey("jwk", keyPair.privateKey);
    var publicKeyJWK = await crypto.subtle.exportKey("jwk", keyPair.publicKey);

    // Get the key fingerprint in Peer DID format
    let fingerprint = await keyPairFingerprint(keyPair);

    // Buid the DID string
    var did = `did:peer:${fingerprint}`;

    // Return an object with the DID and both keys
    return {did: did, privateKey: privateKeyJWK, publicKey: publicKeyJWK};

}

// Generate a symmetric key for encrypting credentials when in transit
// The credentials (and other material) will be encrypted when sent to the
// Secure Messaging Server
async function generateEncryptionKey() {

    // Ask browser to create a symmetric key
    var key = await crypto.subtle.generateKey(
        {
          name: "AES-GCM",
          length: 256
        },
        true,
        ["encrypt", "decrypt"]
      );



    // The JWK format is verbose, but the advantage is that it isself-describing
    return keyJWK;

}

// Convert a key in CryptoKey (native) format to JWK format
async function exportToJWK(key) {
    // Export the key to the JWK format (see spec for details)
    var keyJWK = await crypto.subtle.exportKey("jwk", key);
    return keyJWK;
}

// Convert a private key in JWK format to CryptoKey (native) format
async function importFromJWK(jwk) {

    // Assume for the moment that it is a private key
    var keyUsages = ["sign"];

    // Check if it is a public key
    // In that case, the field "d" should not exist
    if (jwk["d"] == undefined) {
        keyUsages = ["verify"];
    }
    
    // Perform the import
    return await crypto.subtle.importKey(
      "jwk",
      jwk,
      {
        name: "ECDSA",
        namedCurve: "P-384"
      },
      true,
      keyUsages
    );
}

// Encrypt a string message with a symmetric key
async function encryptMessage(keyJWT, stringdata) {

    // Encode the received string into UTF8 bytes
    var enc = new TextEncoder();
    var encodedBytes = enc.encode(stringdata);

    // Generate the iv
    // The iv must never be reused with a given key.
    iv = crypto.getRandomValues(new Uint8Array(12));

    // Perform the actual encryption
    ciphertext = await crypto.subtle.encrypt(
      {
        name: "AES-GCM",
        iv: iv
      },
      key,
      encodedBytes
    );

    // Return the resulting ArrayBuffer, together with the iv
    return {iv: iv, ciphertext: ciphertext};

}

async function decryptMessage(key, iv, ciphertext) {

    // Perform the decryption of the received ArrayBuffer
    var decrypted = await window.crypto.subtle.decrypt(
      {
        name: "AES-GCM",
        iv: iv
      },
      key,
      ciphertext
    );

    // We got UTF8 bytes, should decode into a string
    var dec = new TextDecoder();
    return dec.decode(decrypted);
}


async function didDocFromDid(did) {

}

var MSB = 0x80
  , REST = 0x7F
  , MSBALL = ~REST
  , INT = Math.pow(2, 31)

function encode(num, out, offset) {
  if (Number.MAX_SAFE_INTEGER && num > Number.MAX_SAFE_INTEGER) {
    encode.bytes = 0
    throw new RangeError('Could not encode varint')
  }
  out = out || []
  offset = offset || 0
  var oldOffset = offset

  while(num >= INT) {
    out[offset++] = (num & 0xFF) | MSB
    num /= 128
  }
  while(num & MSBALL) {
    out[offset++] = (num & 0xFF) | MSB
    num >>>= 7
  }
  out[offset] = num | 0
  
  encode.bytes = offset - oldOffset + 1
  
  return out
}

var B58MAP = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz";

var to_b58 = function(
    B            //Uint8Array raw byte input
) {
    var d = [],   //the array for storing the stream of base58 digits
        s = "",   //the result string variable that will be returned
        i,        //the iterator variable for the byte input
        j,        //the iterator variable for the base58 digit array (d)
        c,        //the carry amount variable that is used to overflow from the current base58 digit to the next base58 digit
        n;        //a temporary placeholder variable for the current base58 digit
    for(i in B) { //loop through each byte in the input stream
        j = 0,                           //reset the base58 digit iterator
        c = B[i];                        //set the initial carry amount equal to the current byte amount
        s += c || s.length ^ i ? "" : 1; //prepend the result string with a "1" (0 in base58) if the byte stream is zero and non-zero bytes haven't been seen yet (to ensure correct decode length)
        while(j in d || c) {             //start looping through the digits until there are no more digits and no carry amount
            n = d[j];                    //set the placeholder for the current base58 digit
            n = n ? n * 256 + c : c;     //shift the current base58 one byte and add the carry amount (or just add the carry amount if this is a new digit)
            c = n / 58 | 0;              //find the new carry amount (floored integer of current digit divided by 58)
            d[j] = n % 58;               //reset the current base58 digit to the remainder (the carry amount will pass on the overflow)
            j++                          //iterate to the next base58 digit
        }
    }
    while(j--)        //since the base58 digits are backwards, loop through them in reverse order
        s += B58MAP[d[j]]; //lookup the character associated with each base58 digit
    return s          //return the final base58 string
}


var from_b58 = function(
    S            //Base58 encoded string input
) {
    var d = [],   //the array for storing the stream of decoded bytes
        b = [],   //the result byte array that will be returned
        i,        //the iterator variable for the base58 string
        j,        //the iterator variable for the byte array (d)
        c,        //the carry amount variable that is used to overflow from the current byte to the next byte
        n;        //a temporary placeholder variable for the current byte
    for(i in S) { //loop through each base58 character in the input string
        j = 0,                             //reset the byte iterator
        c = B58MAP.indexOf( S[i] );             //set the initial carry amount equal to the current base58 digit
        if(c < 0)                          //see if the base58 digit lookup is invalid (-1)
            return undefined;              //if invalid base58 digit, bail out and return undefined
        c || b.length ^ i ? i : b.push(0); //prepend the result array with a zero if the base58 digit is zero and non-zero characters haven't been seen yet (to ensure correct decode length)
        while(j in d || c) {               //start looping through the bytes until there are no more bytes and no carry amount
            n = d[j];                      //set the placeholder for the current byte
            n = n ? n * 58 + c : c;        //shift the current byte 58 units and add the carry amount (or just add the carry amount if this is a new byte)
            c = n >> 8;                    //find the new carry amount (1-byte shift of current byte value)
            d[j] = n % 256;                //reset the current byte to the remainder (the carry amount will pass on the overflow)
            j++                            //iterate to the next byte
        }
    }
    while(j--)               //since the byte array is backwards, loop through it in reverse order
        b.push( d[j] );      //append each byte to the result
    return new Uint8Array(b) //return the final byte array in Uint8Array format
}


/**
 * Converts an Ed25519KeyPair object to a `did:key` method DID Document.
 *
 * @param {Ed25519KeyPair} edKey
 * @returns {DidDocument}
 */
async function keyToDidDoc(keyPair) {
const did = `did:peer:${await keyPairFingerprint(keyPair)}`;
const keyId = `${did}#${await keyPairFingerprint(keyPair)}`;
const keyController = did;
const keyType = "Ed25519VerificationKey2018";

const didDoc = {
    '@context': ['https://w3id.org/did/v0.11'],
    id: did,
    publicKey: [{
    id: keyId,
    type: keyType,
    controller: keyController,
    publicKeyBase58: did
    }],
    authentication: [keyId],
    assertionMethod: [keyId],
    capabilityDelegation: [keyId],
    capabilityInvocation: [keyId],
    keyAgreement: [{
    id: keyId,
    type: keyType,
    controller: did,
    publicKeyBase58: did
    }]
};

return didDoc;
}

/**
 * Computes and returns the id of a given key. Used by `did-io` drivers.
 *
 * @param {LDKeyPair} key
 *
 * @returns {string} Returns the key's id.
 */
async function computeKeyId({key}) {
return `did:peer:${keyPairFingerprint(key)}#${keyPairFingerprint(key)}`;
}



var receivedQRPieces = []
var receivedPieces = new Set()


// Start the camera to scan the QR
// The scan can be used either by the Passenger or the Verifier
async function initiateReceiveQRScanning(_prefix) {

    // The received suffix identifies the caller
    // The received parameter is a suffix that has to be appended to all identifiers,
    // to make them unique across pages
    prefix = _prefix
    scan_page = "#" + prefix;

    // Reset the received pieces variables
    receivedQRPieces = []
    receivedPieces = new Set()

    // The HTML element where the video frames will be placed for analysis
    canvasElement = document.getElementById(prefix + "Canvas");

    // Get the canvas context with image data
    canvas = canvasElement.getContext("2d");

    // The output message with status of scanning
    verifierOutputMessage = document.getElementById(prefix + "Message");

    // Disable the Decode button
    $(scan_page + "DecodeButton").hide();

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
        requestAnimationFrame(ReceiveQRtick);
    });

    // Switch to the Verifier screen
    window.location = scan_page;

}

// This function is called periodically until we get a result from the scan
// We use global variables to know the context on which it was called
async function ReceiveQRtick() {

    // Ckeck if we are running in the context of the page that initiated scanning
    if (window.location.hash != scan_page) {
        // The user navigated out of the scan page, should stop using the camera
        stopMediaTracks(myStream);

        // Return without activating the callback again, so it will stop completely
        return
    }

    // Try to scan the QR code only when video stream is ready
    if (video.readyState !== video.HAVE_ENOUGH_DATA) {
        // We are not yet ready

        // Request to be called again in next frame
        requestAnimationFrame(ReceiveQRtick);

        // Exit from the function until it will be called again
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
        requestAnimationFrame(ReceiveQRtick);

        // Exit from the function
        return
    }

    // If we reached up to here, we have a valid QR
    console.log("RECEIVED A PIECE")

    // Split the data in the QR in the components
    components = code.data.split("|")

    // The first component is the total number of pieces to receive
    total = components[0]

    // The second is the index of the received component
    index = components[1]

    // And the third is the actual piece of data
    piece = components[2]

    // Check if we already received this piece
    if (receivedPieces.has(index)) {
        // Continue scanning

        // Request to be called again in next frame
        requestAnimationFrame(ReceiveQRtick);

        // Exit from the function
        return

    }

    // This is a new piece. Add it to the set
    receivedPieces.add(index)
    receivedQRPieces[index] = piece

    // Display in the page the object received.
    verifierOutputMessage.innerText = "Received piece: " + index;


    // Check if we need more pieces
    if (receivedPieces.size < total) {
        // Continue scanning

        // Request to be called again in next frame
        requestAnimationFrame(ReceiveQRtick);

        // Exit from the function
        return

    }

    // We have received all pieces
    // Hide the picture
    canvasElement.hidden = true;

    console.log("RECEIVED ALL PIECES")
    console.log(receivedQRPieces)

    // Assemble all pieces together
    jwt = receivedQRPieces.join("")

    // Log the receved data
    console.log(jwt);


    // Verify the jwt including the signature (goes to the blockchain)
    claims = await verifyJwtVc(jwt);
    if (!claims) {
        // Set an error on the message field of the page
        verifierOutputMessage.innerText = "Error: verification failed!";

        // Stop the media stream
        stopMediaTracks(myStream);

        return
    }

    // Extract the credential
    try {
        cred = decodeJWT(jwt);
        await dbSettings.setItem("passengerCredential", cred);
    } catch (error) {
        verifierOutputMessage.innerText = error;
        // expected output: ReferenceError: nonExistentFunction is not defined
        // Note - error messages will vary depending on browser

        // Stop the media stream
        stopMediaTracks(myStream);

        return
    }

    // If caller was Passenger, we have received a new credential that should be stored in the database
    if (scan_page == "#passengerQRScan") {

        await dbCredentialsSetItem(jwt);

    }

    // Switch to the presentation of results
    window.location = "#displayReceivedCredentialPage"

    // Stop the media stream
    stopMediaTracks(myStream);

    return
}



