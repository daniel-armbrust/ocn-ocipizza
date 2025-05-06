import os
import smtpd
import asyncore

SMTP_IP = os.getenv('SMTP_IP')
SMTP_PORT = os.getenv('SMTP_PORT')

class CustomSMTPServer(smtpd.SMTPServer):
    def process_message(self, peer, mailfrom, rcpttos, data, 
                        mail_options=None, rcpt_options=None):
        print("\n")
        print("-" * 40)
        print('Receiving message from:', peer)
        print('Mail from:', mailfrom)
        print('Rcpt to:', rcpttos)
        print('Data:', data.decode('utf-8'))
        print('Message accepted.\n')
        print("-" * 40)
        print("\n")
        return '250 OK'

if __name__ == '__main__':
    server = CustomSMTPServer((SMTP_IP, int(SMTP_PORT)), None)
    print(f'Running mail server on {SMTP_IP}:{SMTP_PORT}')
    asyncore.loop()