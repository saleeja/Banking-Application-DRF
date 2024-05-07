from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from io import BytesIO


def generate_account_statement_pdf(transactions):
    buffer = BytesIO()

    doc = SimpleDocTemplate(buffer, pagesize=letter)

    data = [['Date', 'Amount', "Receiver",'Description']]
    for transaction in transactions:
        data.append([transaction.transaction_date.strftime('%Y-%m-%d %H:%M:%S'),
                     transaction.amount,
                     transaction.receiver.account_number,
                     transaction.description])


    table = Table(data)

    style = TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.gray),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black)])
    table.setStyle(style)

    elements = [table]
    doc.build(elements)

    buffer.seek(0)

    return buffer
