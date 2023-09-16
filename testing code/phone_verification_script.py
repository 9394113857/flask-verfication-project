# Simulate Flask session using a dictionary
session = {}

# Function to simulate phone verification
def phone_verification():
    # Get user inputs
    country_code = input("Enter country code: ")
    phone_number = input("Enter phone number: ")
    method = input("Enter verification method (e.g., SMS, CALL): ")

    # Store inputs in session dictionary
    session['country_code'] = country_code
    session['phone_number'] = phone_number

    # Simulate api.phones.verification_start
    print(f"Verification started for {phone_number} with method {method}")

    # Call the verification function
    verify()

# Function to simulate verification process
def verify():
    token = input("Enter verification token: ")

    phone_number = session.get("phone_number")
    country_code = session.get("country_code")

    # Simulate api.phones.verification_check
    verification_successful = (token == "1234")

    if verification_successful:
        print("Phone verified successfully.")
    else:
        print("Invalid verification code. Please try again.")

# Main block, runs if the script is executed directly
if __name__ == "__main__":
    # Call the phone_verification function
    phone_verification()
