# scripts/monitor_email.py
import imaplib
import email
import os, ssl
from dotenv import load_dotenv

load_dotenv()

class EmailMonitor:
    def __init__(self, imap_server, imap_port,username, password):
        self.server = imap_server
        self.port = imap_port # Add port
        self.username = username
        self.password = password
        self.mail = None
        print("EmailMonitor initialized.")

    def connect(self):
        try:
            print(f"Connecting to server: {self.server}:{self.port}...")
            # Create a default SSL context
            context = ssl.create_default_context()
            # Disable hostname checking and certificate verification
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE

            self.mail = imaplib.IMAP4_SSL(self.server,993, ssl_context=context) # Pass context
            self.mail.login(self.username, self.password)
            print("Login successful.")
            return True
        except Exception as e:
            print(f"Failed to connect or log in: {e}")
            return False

    def find_emails(self, criteria):
        """Finds emails based on a search criteria string (e.g., 'UNSEEN FROM "sender@example.com"')."""
        if not self.mail:
            print("Not connected.")
            return []
        
        self.mail.select("inbox")
        status, data = self.mail.search(None, criteria)
        
        if status != "OK":
            print(f"Error searching for emails: {data}")
            return []
            
        email_ids = data[0].split()
        print(f"Found {len(email_ids)} emails matching criteria '{criteria}'.")
        return email_ids

    def close(self):
        if self.mail:
            self.mail.close()
            self.mail.logout()
            print("Connection closed.")

def main():
    # --- Configuration ---
    IMAP_SERVER = os.getenv("EMAIL_IMAP_SERVER")
    USERNAME = os.getenv("EMAIL_USERNAME")
    PASSWORD = os.getenv("EMAIL_APP_PASSWORD")
    IMAP_PORT = int(os.getenv("EMAIL_IMAP_PORT",993)) # Read the port
    
    # --- Execution ---
    monitor = EmailMonitor(IMAP_SERVER,IMAP_PORT, USERNAME, PASSWORD)
    if monitor.connect():
        # Example: Find all unread emails from a specific sender
        search_criteria = '(UNSEEN FROM "rayngugu@gmail.com")' # Change this to a real sender
        email_ids = monitor.find_emails(search_criteria)
        
        # For now, we just print the number of emails found.
        # Next step will be to download attachments from them.
        print(f"Number of unread emails from specified sender: {len(email_ids)}")
        
        monitor.close()

if __name__ == "__main__":
    main()

#### **Step 3: Initial Test**

