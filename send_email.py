# importing libraries
from flask import Flask
from flask_mail import Mail, Message

app = Flask(__name__)
mail = Mail(app)  # instantiate the mail class

# configuration of mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'ushabr1969@gmail.com'  # Your Gmail address
app.config['MAIL_PASSWORD'] = 'Usha_123'  # Your Gmail password
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)


# message object mapped to a particular URL ‘/’
@app.route("/")
def index():
    msg = Message(
        'Hello',
        sender='ushabr1969@gmail.com',  # Your Gmail address
        recipients=['raghunadh28@gmail.com']  # Receiver's email address
    )
    msg.body = 'Hello Flask message sent from Flask-Mail'
    mail.send(msg)
    return 'Sent'


if __name__ == '__main__':
    app.run(debug=True)
