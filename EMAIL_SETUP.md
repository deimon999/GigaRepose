# Email Setup Instructions

## To Enable Email Notifications for Contact Form

The contact form currently **logs emails to a file** (`email_notifications.txt`). To actually send emails to your Gmail (`kyndiahdeimon753@gmail.com`), follow these steps:

### Step 1: Generate Gmail App Password

1. Go to your Google Account: https://myaccount.google.com/
2. Click on "Security" in the left sidebar
3. Under "How you sign in to Google", enable **2-Step Verification** (if not already enabled)
4. After 2-Step Verification is enabled, go back to Security
5. Click on "App passwords" (you'll see this option only if 2-Step Verification is on)
6. Select app: **Mail**
7. Select device: **Other (Custom name)** → Type: "DeepFake Detector"
8. Click **Generate**
9. **Copy the 16-character password** (it will look like: `abcd efgh ijkl mnop`)

### Step 2: Add App Password to app.py

1. Open `app.py`
2. Find the `send_contact_email()` function (around line 140)
3. Look for this commented section:
   ```python
   # Uncomment below and add your Gmail App Password to actually send emails
   """
   GMAIL_APP_PASSWORD = "your-16-character-app-password-here"
   ```

4. **Uncomment the code** and replace `"your-16-character-app-password-here"` with your actual app password:
   ```python
   GMAIL_APP_PASSWORD = "abcd efgh ijkl mnop"  # Your 16-char password (remove spaces)
   
   server = smtplib.SMTP('smtp.gmail.com', 587)
   server.starttls()
   server.login(SENDER_EMAIL, GMAIL_APP_PASSWORD)
   server.sendmail(SENDER_EMAIL, RECIPIENT_EMAIL, msg.as_string())
   server.quit()
   print(f"Email sent successfully to {RECIPIENT_EMAIL}")
   ```

5. **Remove the triple quotes** (`"""`) above and below that block to uncomment it

### Step 3: Restart Flask Server

```powershell
# Stop current server
Stop-Process -Name python -Force

# Start server
python app.py
```

### Step 4: Test

Submit a test message via the contact form and check your Gmail inbox!

---

## Current Behavior (Without Setup)

✅ **Already Working:**
- Contact form submissions are saved to `contact_messages.json`
- Email notifications are logged to `email_notifications.txt`
- Form shows success message to users

❌ **Not Yet Active:**
- Actual email delivery to Gmail (requires App Password setup above)

---

## Security Notes

⚠️ **IMPORTANT:**
- **Never commit your App Password to GitHub!**
- Consider using environment variables:
  ```python
  import os
  GMAIL_APP_PASSWORD = os.environ.get('GMAIL_APP_PASSWORD', '')
  ```
  
- Or create a `.env` file (add to `.gitignore`):
  ```
  GMAIL_APP_PASSWORD=your-password-here
  ```
  Then load with `python-dotenv`:
  ```python
  from dotenv import load_dotenv
  load_dotenv()
  ```

---

## Alternative: Use Gmail API (More Secure)

If you want a more secure solution without storing passwords:
1. Use Gmail API with OAuth2
2. Requires more setup but no password storage
3. Let me know if you want me to implement this!

---

## Your Contact Details (Configured)

- **Email:** kyndiahdeimon753@gmail.com
- **GitHub:** https://github.com/deimon999
- **Project:** DeepFake Detection Studio

All contact form submissions will be sent to your Gmail with:
- Sender name and email
- Subject line
- Message content
- Timestamp
- Professional HTML formatting
- Reply-To header for easy responses
