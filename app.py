
import base64
import os
from flask import Flask,session,request,render_template,send_from_directory,jsonify
from uttlv import TLV
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfbase.ttfonts import TTFont
import arabic_reshaper
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
import pyqrcode
from PIL import Image
from pyzbar.pyzbar import decode
import random
from flask_sqlalchemy import SQLAlchemy
from bidi.algorithm import get_display

app = Flask(__name__)

app.config["SECRET_KEY"] = 'hussam01'

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://{}:{}@{}:{}/{}?charset=utf8mb4'.format('b92f40e7a9fe18', '0e03f261', 'us-cdbr-east-04.cleardb.com', 3306, 'heroku_51b533760613fb0')
db = SQLAlchemy(app)
class Vattable(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    seller_name = db.Column(db.String(200))
    vat_no = db.Column(db.String(80))
    invoice_date = db.Column(db.String(80))
    vat_total =db.Column(db.String(80))
    invoice_total = db.Column(db.String(80))
    barcode=db.Column(db.String(100))


@app.route('/')
def main():
    return "api e - invoicing marwan zamakah"
@app.route('/api',methods = ["POST", "GET"])
def makebarcode():
       if request.method == "POST":

         e1 = request.json["name"]
         print(e1)

         e2 = request.json["vatno"]

         e3 = request.json["date"]

         e4= request.json["vatamount"]

         e5 = request.json["invamount"]

         t = TLV()
         t[1] = e2
         t[2] = e1
         t[3] = e4
         t[4] = e5
         t[5] = e3
         TL = t[1] + t[2] + t[3] + t[4] + t[5]

         arr = t.to_byte_array()

         encoded = base64.b64encode(arr).decode("utf-8")
         print(encoded)
         e6=str(encoded)

         e7= random.randint(1, 1000000000)

         input=Vattable(id=e7,seller_name=e1,vat_no=e2,invoice_date=e3,vat_total=e4,invoice_total=e5,barcode=e6)
         db.session.add(input)
         db.session.commit()

         url="http://easy1parts.com/"+encoded

         big_code = pyqrcode.create(url)

         dd=big_code.png('code1.png', scale=6, module_color=[0, 0, 0, 128], background=[0xff, 0xff, 0xcc])
         page_width = 2156
         page_height = 3050
         margin = 70

         # Creating a pdf file and setting a naming convention
         c = canvas.Canvas("vat1check" + '.pdf')
         c.setPageSize((page_width, page_height))

         logo = ImageReader('code1.png')
         # Drawing the image
         c.drawImage(logo, 900, 2600, mask='auto')

         workingdir = os.path.abspath(os.getcwd())
         filepath = workingdir + '/'

         c.showPage()
         c.save()

         result = decode(Image.open('code1.png'))

         return send_from_directory(filepath, 'vat1check.pdf')

@app.route('/<encoded>',methods = ['POST', 'GET'])
def info(encoded):

      cure=Vattable.query.filter_by(barcode=str(encoded)).first()
      print(cure)
      if cure:
       r1=cure.seller_name
       r2=cure.vat_no
       r3=cure.invoice_date
       r4=cure.vat_total
       r5=cure.invoice_total


       url = "http://easy1parts.com/" + encoded
       big_code = pyqrcode.create(url)

       pdfmetrics.registerFont(TTFont('Arial', 'Arial.ttf'))
       # Page information
       page_width = 2156
       page_height = 3050
       margin = 70
       y = page_height - margin * 2
       x = 1 * margin
       # Creating a pdf file and setting a naming convention
       c = canvas.Canvas("vatcheck" + '.pdf')
       c.setPageSize((page_width, page_height))

       logo = ImageReader('code1.png')
       y -= margin * 2
       # Drawing the image
       c.drawImage(logo, 900, 2300, mask='auto')

       workingdir = os.path.abspath(os.getcwd())
       filepath = workingdir + '/'
       c.setFont('Arial', 80)
       text = 'INVOICE'
       text_width = stringWidth(text, 'Arial', 80)
       #c.drawString((page_width - text_width) / 2, page_height - margin, text)
       y = page_height - margin * 2
       x = 1 * margin
       x2 = x + 250
       y -= margin*15
       c.setFont('Arial', 70)
       ar = arabic_reshaper.reshape(u'اسم المورد')
       ar = get_display(ar)
       #canvas.setFont('Arabic', 32)
       c.drawString(x+1350, y, ar)
       ar = arabic_reshaper.reshape(u' رقم تسجيل ضريبة الـقـيـمـة الـمـضـافة')
       ar = get_display(ar)
       # canvas.setFont('Arabic', 32)
       c.drawString(x + 50, y, ar)
       y -= margin*2


       #c.drawString(x+1100, y, 'Vendor Name')
       #y -= margin*2
       c.drawString(x+1350, y, cure.seller_name)

       c.drawString(x + 50, y, cure.vat_no)
       y -= margin * 5
       ar = arabic_reshaper.reshape(u'الـتـاريـخ والـوقت')
       ar = get_display(ar)
       # canvas.setFont('Arabic', 32)
       c.drawString(x + 1350, y, ar)
       ar = arabic_reshaper.reshape(u' اجمالي ضريبة القيمة المضافة ')
       ar = get_display(ar)
       # canvas.setFont('Arabic', 32)
       c.drawString(x + 50, y, ar)
       y -= margin * 2
       c.drawString(x + 1350, y, cure.invoice_date)

       c.drawString(x + 50, y, cure.vat_total)
       y -= margin * 5
       ar = arabic_reshaper.reshape(u'اجمالي قيمة الفاتورة مع الضريبة')
       ar = get_display(ar)
       # canvas.setFont('Arabic', 32)
       c.drawString(x + 50, y, ar)
       y -= margin * 2
       c.drawString(x + 50, y, cure.invoice_total)
       c.showPage()
       c.save()
       return send_from_directory(filepath, 'vatcheck.pdf')
      else:

       return 'The QR Code is not available please contact your vendor'


if __name__ == '__main__':
    app.run()

