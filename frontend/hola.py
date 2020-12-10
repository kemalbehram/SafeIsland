__pragma__ ('alias', 'S', '$')

def hashchange ():
    console.log(location.hash)

    # Execute logic on page enter for each different page
    process_page_enter()

window.addEventListener("hashchange", hashchange)

def process_page_enter():

    # Handle page transition
    # Hide all pages of the application
    S (".jrmpage").hide()
    # Show a single page: the one we are now (if hash is non-null) or the home otherwise
    if location.hash:
        S (location.hash).show()
    else:
        S ("#home").show()

    if location.hash == "#passengerDisplayCredential":
        console.log("In #passengerDisplayCredential script")
        # Start scanning system for passenger


    if (location.hash == "#passengerDisplayQR"):
        console.log("In #passengerDisplayQR script")
        # Start scanning system for passenger

    if (location.hash == "#QRScanPassenger"):
        console.log("In #QRScanPassenger script")
        # Start scanning system for passenger

# Initialize the DOM
def initdom():

    # This function is called when a refresh is triggered in any other page

    # Try to retrieve an existing credential from the local storage
    # If no credential exists, store a testing one automatically
    # TODO: This logic is just for testing, and should be eliminated for production

    # Execute logic on page enter for each different page
    process_page_enter()

S (document).ready(initdom)

