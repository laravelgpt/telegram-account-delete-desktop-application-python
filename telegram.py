import tkinter as tk
from tkinter import ttk, messagebox
from telethon import TelegramClient, functions
from telethon.errors import FloodWaitError, PhoneNumberInvalidError, CodeInvalidError, PasswordHashInvalidError
import requests  # For making HTTP requests to RapidAPI
import random  # For generating OTPs

# Replace these with your API ID and Hash from my.telegram.org
api_id = '29877679'  # Replace with your API ID
api_hash = 'fdc01502f2ed6516e1d17f8d27b1aa6a'  # Replace with your API Hash

# RapidAPI SMS configuration
RAPIDAPI_KEY = "0fea2c844fmshc4c162470bfb883p10b6edjsnff4a4ebe8023"  # Your RapidAPI key
RAPIDAPI_HOST = "twilio-sms.p.rapidapi.com"  # Replace with the host of the SMS API you choose
RAPIDAPI_URL = "https://twilio-sms.p.rapidapi.com/2010-04-01/Accounts/{AccountSID}/Messages.json"  # Replace with the endpoint URL

# Initialize the Telegram client
client = TelegramClient('session_name', api_id, api_hash)

def generate_otp():
    """Generate a 6-digit OTP."""
    return str(random.randint(100000, 999999))

async def send_otp():
    """Send OTP to the user via Telegram app or SMS (using RapidAPI)."""
    phone_number = phone_entry.get().strip()
    if not phone_number:
        messagebox.showerror("Error", "Please enter your phone number.")
        return

    try:
        # Determine the OTP delivery method
        otp_method = otp_method_combobox.get().lower()
        if otp_method not in ["telegram", "sms"]:
            messagebox.showerror("Error", "Invalid OTP delivery method. Choose 'Telegram' or 'SMS'.")
            return

        if otp_method == "telegram":
            # Send OTP via Telegram app
            await client.connect()
            sent_code = await client.send_code_request(phone_number)
            messagebox.showinfo("OTP Sent", "OTP has been sent via Telegram app.")
        else:
            # Send OTP via SMS using RapidAPI
            otp_code = generate_otp()
            sms_payload = {
                "To": phone_number,
                "From": "+1234567890",  # Replace with your Twilio phone number
                "Body": f"Your OTP is: {otp_code}"
            }
            headers = {
                "X-RapidAPI-Key": RAPIDAPI_KEY,
                "X-RapidAPI-Host": RAPIDAPI_HOST,
                "Content-Type": "application/x-www-form-urlencoded"
            }
            response = requests.post(
                RAPIDAPI_URL,
                data=sms_payload,
                headers=headers
            )
            if response.status_code == 200:
                messagebox.showinfo("OTP Sent", "OTP has been sent via SMS.")
            else:
                messagebox.showerror("Error", f"Failed to send SMS: {response.text}")
    except PhoneNumberInvalidError:
        messagebox.showerror("Error", "Invalid phone number. Please check and try again.")
    except FloodWaitError as e:
        messagebox.showerror("Error", f"Too many attempts. Please wait {e.seconds} seconds before trying again.")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

async def delete_account():
    """Function to delete the Telegram account."""
    phone_number = phone_entry.get().strip()
    if not phone_number:
        messagebox.showerror("Error", "Please enter your phone number.")
        return

    try:
        # Connect and authenticate
        await client.start(phone=phone_number)
        if not await client.is_user_authorized():
            code = code_entry.get().strip()
            if not code:
                messagebox.showerror("Error", "Please enter the verification code.")
                return
            await client.sign_in(phone_number, code)

        # Check if the account has 2FA enabled
        if await client.is_password_required():
            password = password_entry.get().strip()
            if not password:
                messagebox.showerror("Error", "This account has 2FA enabled. Please enter your password.")
                return
            await client(functions.account.DeleteAccountRequest(
                reason="I want to delete my account",
                password=password
            ))
        else:
            # Delete the account without 2FA
            await client(functions.account.DeleteAccountRequest(
                reason="I want to delete my account"
            ))

        messagebox.showinfo("Success", "Your Telegram account has been deleted.")
    except PhoneNumberInvalidError:
        messagebox.showerror("Error", "Invalid phone number. Please check and try again.")
    except CodeInvalidError:
        messagebox.showerror("Error", "Invalid verification code. Please check and try again.")
    except PasswordHashInvalidError:
        messagebox.showerror("Error", "Invalid 2FA password. Please check and try again.")
    except FloodWaitError as e:
        messagebox.showerror("Error", f"Too many attempts. Please wait {e.seconds} seconds before trying again.")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")
    finally:
        await client.disconnect()

def on_send_otp():
    """Trigger the OTP sending process."""
    import asyncio
    asyncio.run(send_otp())

def on_delete():
    """Trigger the account deletion process."""
    import asyncio
    asyncio.run(delete_account())

# Create the main application window
root = tk.Tk()
root.title("tgdelete - Delete Telegram Account")
root.geometry("400x300")
root.resizable(False, False)  # Disable resizing

# Apply a modern theme
style = ttk.Style()
style.theme_use("clam")  # Use the 'clam' theme for a modern look

# Create a main frame for better organization
main_frame = ttk.Frame(root, padding="20")
main_frame.grid(row=0, column=0, sticky="nsew")

# Phone number input
ttk.Label(main_frame, text="Phone Number:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
phone_entry = ttk.Entry(main_frame, width=30)
phone_entry.grid(row=0, column=1, padx=10, pady=10)

# OTP delivery method
ttk.Label(main_frame, text="OTP Delivery Method:").grid(row=1, column=0, padx=10, pady=10, sticky="w")
otp_method_combobox = ttk.Combobox(main_frame, values=["Telegram", "SMS"], width=27)
otp_method_combobox.grid(row=1, column=1, padx=10, pady=10)
otp_method_combobox.current(0)  # Default to Telegram

# Send OTP button
send_otp_button = ttk.Button(main_frame, text="Send OTP", command=on_send_otp)
send_otp_button.grid(row=2, column=0, columnspan=2, pady=10)

# Verification code input
ttk.Label(main_frame, text="Verification Code:").grid(row=3, column=0, padx=10, pady=10, sticky="w")
code_entry = ttk.Entry(main_frame, width=30)
code_entry.grid(row=3, column=1, padx=10, pady=10)

# 2FA Password input
ttk.Label(main_frame, text="2FA Password (if any):").grid(row=4, column=0, padx=10, pady=10, sticky="w")
password_entry = ttk.Entry(main_frame, width=30, show="*")
password_entry.grid(row=4, column=1, padx=10, pady=10)

# Delete button
delete_button = ttk.Button(main_frame, text="Delete Account", command=on_delete)
delete_button.grid(row=5, column=0, columnspan=2, pady=20)

# Run the application
root.mainloop()