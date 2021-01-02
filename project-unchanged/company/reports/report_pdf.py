#from company.reports.report_base import ReportBase, genrate
from functools import update_wrapper
import re
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader

from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle

import os
from django.conf import settings

class ReportPdf:

    def __init__(self, directory, filename, margin):
        self.file_path = os.path.join(settings.BASE_DIR, 'assets', 'reports', directory)
        self.url = f'/static/reports/{directory}/{filename}'
        try:
            
            os.mkdir(self.file_path)
        except:
            pass
        self.filename = os.path.join(self.file_path, filename)

        self.pdf = canvas.Canvas(self.filename, pagesize=A4)
        self.width = A4[0]
        self.height = A4[1]
        self.margin = margin*mm
        self.x = self.margin
        self.y = self.height

    def centerText(self, text, font, size):
        textWidth = stringWidth(text, font, size)
        return self.margin + ((self.width - (self.margin*2)) - textWidth)/2

    def centerTextByOther(self, text, font, size, width):
        textWidth = stringWidth(text, font, size)
        return (width - textWidth)/2

    def addImage(self, image, size, text, font, font_size):
        image = ImageReader(image)
        y = self.height - self.margin - size
        self.y = y - font_size
        self.pdf.drawImage(image=image, x=self.margin, y=y, height=size, width=size, mask='auto')
        self.pdf.setFont(font, font_size)
        positon = self.centerTextByOther(text, font, font_size, size)
        self.pdf.drawString(x=self.margin+positon, y=self.y, text=text)
        self.y -= font_size

    def setFont(self, font=None, font_size=None):
        if font and font_size:
            self.pdf.setFont(font, font_size)
        if font_size:
            self.pdf.setFontSize(font_size)
    
    def addMetadata(self, generatedby, timestamp, font=None, font_size=None):
        self.setFont(font, font_size)
        width1 = stringWidth(generatedby, self.pdf._fontname, self.pdf._fontsize)
        width2 = stringWidth(timestamp, self.pdf._fontname, self.pdf._fontsize)
        if width1 >= width2:
            width = width1
        else:
            width = width2
        x = self.width - self.margin - width
        y = self.height - self.margin - self.pdf._fontsize
        self.pdf.drawString(x=x, y=y, text=generatedby)
        self.pdf.drawString(x=x, y=y-self.pdf._fontsize-5, text=timestamp)

    def __ajust_table_width__(self, cols_w):
        current = sum(cols_w)
        real_width = self.width - self.margin*2
        diff = current - real_width
        if diff <= 0:
            return cols_w
        razon = (diff/real_width) + 1
        result = [v/razon for v in cols_w]
        return result
    
    def addTitle(self, title, font, size):
        self.setFont(font, size)
        self.y -= size
        pos = self.centerText(title, font, size)
        self.pdf.drawString(x=pos, y=self.y, text=title)
        self.y -= size

    def addTable(self, titles=[], data=[], headers_font=None, body_font=None, font_size=None):
        style = [
                    ('FONT', (0, 0), (-1, 0), headers_font), 
                    ('FONT',(0, 1), (-1, -1), body_font),
                    ('FONTSIZE', (0, 0), (-1, -1), font_size),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
                    ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
                ]
        grid = []
        pad = 10
        max_font = headers_font
        max_text = ""
        max_w = 0
        cols_w = []
        for t in titles:
            w = stringWidth(t, headers_font, font_size) + pad
            if w > max_w:
                max_w = w
                max_text = t
            cols_w.append(w)

        grid.append(titles)
        for dat in data:
            row = []
            i = 0
            for k in dat:
                row.append(dat[k])
                w = stringWidth(str(dat[k]), body_font, font_size)
                if w > max_w:
                    max_w = w + pad
                    max_text = str(dat[k])
                    max_font = body_font

                if cols_w[i] < (w + pad):
                    cols_w[i] = w + pad
                i += 1

            grid.append(row)
        new_cols_w = self.__ajust_table_width__(cols_w)

        new_max_w = max(new_cols_w)
        size = font_size
        while new_max_w < max_w and size > 5:
            size -= 0.1
            max_w = stringWidth(max_text, max_font, size) + pad
        style[2] = ('FONTSIZE', (0, 0), (-1, -1), size)

        row_h = font_size + (font_size*0.9)
        n = len(grid)
        table = Table(grid, rowHeights=n*[row_h], colWidths=new_cols_w)
        table.setStyle(TableStyle(style))
        tables = table.split(self.width, self.y-self.margin)
        nt = len(tables)
        end = False
        while nt <= 2 and not end:
            table = tables[0]
            n = table._nrows
            table.wrapOn(self.pdf, self.width, self.height)
            table.drawOn(self.pdf, self.margin, self.y - ((n-1)*row_h) - self.margin)
            if nt == 1:
                end = True
            if nt == 2:
                self.pdf.showPage()
                self.y = self.height
                tables = tables[1].split(self.width, self.y-self.margin)
                nt = len(tables)
                
        

    
    def generate(self):
        self.pdf.showPage()
        self.pdf.save()

