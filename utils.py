import imaplib
import pyzmail
import pandas as pd
import os
from datetime import datetime, timedelta
from openpyxl import load_workbook

def gmail_extract():
    # === Email credentials ===
    EMAIL = 'akki.reddy1009@gmail.com'
    APP_PASSWORD = 
    DOWNLOAD_FOLDER = 'excel_attachments'

    os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

    # === Connect to Gmail via IMAP ===
    imap_server = imaplib.IMAP4_SSL('imap.gmail.com')
    imap_server.login(EMAIL, APP_PASSWORD)
    imap_server.select('INBOX')
    cob = datetime.today().strftime('%Y%m%d')
    #cob = (datetime.today() - timedelta(days=1)).strftime('%Y%m%d')

    # === Search unread emails ===
    status, response = imap_server.search(None, 'FROM','akki.reddy1009@gmail.com','SUBJECT',f'Portfolio_Holdings_UB5C0_{cob}')
    print(status)
    print(response)
    email_ids = response[0].split()
    print(email_ids)

    for eid in email_ids:
        # Fetch raw email
        status, msg_data = imap_server.fetch(eid, '(RFC822)')
        raw_email = msg_data[0][1]

        # Parse email
        msg = pyzmail.PyzMessage.factory(raw_email)

        subject = msg.get_subject()
        print(f"Email Subject: {subject}")

        # Check if subject contains keyword (optional)
        if 'Portfolio_Holdings_UB5C0_' in subject:
            # Loop over parts and find Excel attachments
            for part in msg.mailparts:
                if part.filename and (part.filename.endswith('.xlsx') or part.filename.endswith('.xls')):
                    file_path = os.path.join(DOWNLOAD_FOLDER, part.filename)
                    with open(file_path, 'wb') as f:
                        f.write(part.get_payload())
                    print(f"Downloaded: {part.filename}")
                else:
                    continue

    imap_server.logout()

    return 'Done'

def excel_load():
    today_date = datetime.today().strftime('%d-%m-%Y')
    cob = datetime.today().strftime('%Y%m%d')
    #today_dt = datetime.today().strftime('%d-%m-%Y')

    df = pd.read_excel(f'excel_attachments\Portfolio_Holdings_UB5C0_{cob}.xlsx', header=5)
    df= df[(df["Script Name"] != 'Equity') & (df["Script Name"] != 'Mutual Funds') &(df["Security Type"] == 'EQUITY STOCK')]
    df["Date"]=today_date
    print(df)

    file_path = 'excel_attachments\Master_Portfolio_Tracker.xlsx'
    sheet_name = 'Sheet1'

    existing_df = pd.read_excel(file_path, sheet_name=sheet_name)
    startrow = len(existing_df) + 1

    # Append without setting book/sheets manually
    with pd.ExcelWriter(file_path, engine='openpyxl', mode='a', if_sheet_exists='overlay') as writer:
        df.to_excel(writer, sheet_name=sheet_name, index=False, header=False, startrow=startrow)

    return 'Done'
