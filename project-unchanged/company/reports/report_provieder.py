from users.service import UserService
from topup.service import TopupService
from notification.notification_provider import get_notifications_new
from users.models import UserStation
from company.models import CompanyAdminUser
from .report_csv import ReportCsv
from .report_pdf import ReportPdf
from purchase.service import PurchaseService
from datetime import datetime
from purchase.service import RatingService

purchase_service = PurchaseService()
top_up_service = TopupService()
user_service = UserService()
rating_service = RatingService()

PDF = 'pdf'
CSV = 'csv'
XLSX = 'xlsx'
HTML = 'html'


def __generate_pdf__(generate_by, titles=[], data=[], dir='', filename='', title=""):
    if generate_by.is_admin:
        company = CompanyAdminUser.objects.get(user=generate_by).company
    else:
        company = UserStation.objects.get(user=generate_by).gas_station.company
    pdf = ReportPdf(dir, filename, 15)
    name = generate_by.first_name
    last = generate_by.last_name
    generate_at = datetime.now().strftime("%d/%m/%Y %H:%M")
    pdf.addImage(company.company_logo_path, pdf.height*0.08, company.trade_name, "Helvetica", 12)
    pdf.addMetadata(f'Generado por: {name} {last}', f'Fecha: {generate_at}', font_size=8)
    pdf.addTitle(title, "Helvetica-Bold", 14)
    pdf.addTable(titles, data, "Helvetica-Bold", "Helvetica", 11)
    pdf.generate()
    return pdf.url

def __generate_csv__(titles=[], data=[], dir='', filename=''):
    csv = ReportCsv(dir, filename)
    csv.generate(titles, data)
    return csv.url

def __generate_xlsx__(titles=[], data=[], dir='', filename=''):
    csv = ReportCsv(dir, filename)
    csv.generate(titles, data)
    csv.to_excel()
    return csv.url

def __generate_html__(titles=[], data=[], dir='', filename=''):
    csv = ReportCsv(dir, filename)
    csv.generate(titles, data)
    csv.to_html()
    return csv.url

def generate_report(format='pdf', generate_by=None, titles=[], data=[], filename='', title=''):
    formato = "%Y%m%d%H%M%S"
    dt = datetime.now()
    dir = dt.strftime(formato)
    filename = f"{filename}.{format}"

    if format == PDF:
        return __generate_pdf__(generate_by, titles, data, dir, filename, title)
    elif format == CSV:
        return __generate_csv__(titles, data, dir, filename)
    elif format == XLSX:
        return __generate_xlsx__(titles, data, dir, filename)
    elif format == HTML:
        return __generate_html__(titles, data, dir, filename)
    else:
        return None

def purchase_report(generate_by=None, from_date=None, to_date=None, gas_stations=[], fuel_types=[]):
    def getFormat(data, format_datetime=None):
        p = data["purchase"]
        f = data["fuel_type"]
        state = "No completada"
        if p["is_done"]:
            state = "Completada"
        f_date = p["created_at"]
        if format_datetime:
            f_date = datetime.fromisoformat(p["created_at"].replace("T", " ").replace("Z", "")).strftime(format_datetime)
        user = None
        if p["user"] != None:
            user = f'{p["user"]["first_name"]} {p["user"]["last_name"]}'
       
        return {
            "number_code": p["number_code"],
            "created_at": f_date,
            "state": state,
            "gas_station": p["gas_station"]["name"],
            "client": user,
            "fuel_type": f["name"],
            "gallons": p["gallons"],
            "amount": p["amount"]
        }
    
    titles = ["Código", "Fecha de creación", 
		"Estado", "Gasolinera", "Cliente", "Gasolina", "Galones", "Monto"]
    has_fuel_types = len(fuel_types) > 0
    if generate_by.is_admin:
        if has_fuel_types:
            data = purchase_service.get_purchase_fuel_type_company_filtered(generate_by, from_date, to_date, gas_stations=gas_stations, fuel_types=fuel_types)
        else:
            data = purchase_service.get_purchase_company_filtered(generate_by, from_date, to_date, gas_stations=gas_stations)
    else:
        if has_fuel_types:
            data = purchase_service.get_purchase_fuel_type_gas_station_filtered(generate_by, from_date, to_date, fuel_types=fuel_types)
        else:
            data = purchase_service.get_purchase_gas_station_filtered(generate_by, from_date, to_date)
    data = [getFormat(d, format_datetime="%d/%m/%Y %H:%M:%S") for d in data]
    pdf_r = generate_report(PDF, generate_by, titles=titles, data=data, filename="compras", title="Reporte de Compras")
    csv_r = generate_report(CSV, generate_by, titles=titles, data=data, filename="compras", title="Reporte de Compras")
    xlsx_r = generate_report(XLSX, generate_by, titles=titles, data=data, filename="compras", title="Reporte de Compras")
    return {'pdf': pdf_r, 'csv': csv_r, 'xlsx': xlsx_r}

def topup_report(generate_by=None, from_date=None, to_date=None, gas_stations=[]):
    def getFormat(data, format_datetime):
        return {
            "id": data["id"],
            "created_at": datetime.fromisoformat(data["created_at"].replace("T", " ").replace("Z", "")).strftime(format_datetime),
            "gas_station": data["gas_station"]["name"],
            "client": f'{data["user"]["first_name"]} {data["user"]["last_name"]}',
            "amount": data["amount"]
        }
    titles = ["id", "Fecha de creación", "Gasolinera", "Cliente", "Monto"]
    if generate_by.is_admin:
        data = top_up_service.get_topup_company_filtered(generate_by, from_date, to_date, gas_stations=gas_stations)
    else:
        data = top_up_service.get_topup_gas_station_filtered(generate_by, from_date, to_date)
    data = [getFormat(d, format_datetime="%d/%m/%Y %H:%M:%S") for d in data]
    pdf_r = generate_report(PDF, generate_by, titles=titles, data=data, filename="recargas", title="Reporte de Recargas")
    csv_r = generate_report(CSV, generate_by, titles=titles, data=data, filename="recargas", title="Reporte de Recargas")
    xlsx_r = generate_report(XLSX, generate_by, titles=titles, data=data, filename="recargas", title="Reporte de Recargas")
    return {'pdf': pdf_r, 'csv': csv_r, 'xlsx': xlsx_r}

def users_report(generate_by=None, gas_stations=[], is_active=None):
    def getFormat(data):
        status = "Activo"
        if not data["user"]["is_active"]:
            status = "Inhabilitado"
        return {
            "id": data["user"]["cedula"],
            "first_name": data["user"]["first_name"],
            "last_name": data["user"]["last_name"],
            "email": data["user"]["email"],
            "city": data["user"]["city"],
            "is_active": status,
            "gas_station": data["gas_station"]["name"],
            "total": data["total"]
        }
    titles = ["Id", "Nombres", "Apellidos", "Correo", "Ciudad", "Estado", "Gasolinera", "Balance"]
    if generate_by.is_admin:
        data = user_service.get_users_by_compnay_filtered(generate_by, is_active, gas_stations)
    else:
        data = user_service.get_users_by_station_filtered(generate_by, is_active)
    data = [getFormat(d) for d in data]
    pdf_r = generate_report(PDF, generate_by, titles=titles, data=data, filename="usuarios", title="Reporte de Usuarios")
    csv_r = generate_report(CSV, generate_by, titles=titles, data=data, filename="usuarios", title="Reporte de Usuarios")
    xlsx_r = generate_report(XLSX, generate_by, titles=titles, data=data, filename="usuarios", title="Reporte de Usuarios")
    return {'pdf': pdf_r, 'csv': csv_r, 'xlsx': xlsx_r}


def rating_report(generate_by=None, from_date=None, to_date=None, gas_stations=[]):
    def getFormat(data, format_datetime, comments=True):
        p = data["purchase"]
        res = {
            "created_at": datetime.fromisoformat(data["created_at"].replace("T", " ").replace("Z", "")).strftime(format_datetime),
            "number_code": p["number_code"],
            "user": f'{data["user"]["first_name"]} {data["user"]["last_name"]}',
            "gas_station": p["gas_station"]["name"],
            "rating": data["rating"],
        }
        if comments:
            res["comment"] = data["comment"]
        return res

    titles = ["Fecha de creación", "Código de compra", "Cliente", "Gasolinera", "Calificación"]
        
    if generate_by.is_admin:
        data = rating_service.get_ratings_company_filtered(generate_by, from_date, to_date, gas_stations)
    else:
        data = rating_service.get_ratings_station_filtered(generate_by, from_date, to_date)
    data_pdf = [getFormat(d, format_datetime="%d/%m/%Y %H:%M:%S", comments=False) for d in data]
    pdf_r = generate_report(PDF, generate_by, titles=titles, data=data_pdf, filename="calificaciones", title="Reporte de Calificaciones")
    titles.append("Comentario")
    data = [getFormat(d, format_datetime="%d/%m/%Y %H:%M:%S", comments=True) for d in data]
    csv_r = generate_report(CSV, generate_by, titles=titles, data=data, filename="calificaciones", title="Reporte de Calificaciones")
    xlsx_r = generate_report(XLSX, generate_by, titles=titles, data=data, filename="calificaciones", title="Reporte de Calificaciones")
    return {'pdf': pdf_r, 'csv': csv_r, 'xlsx': xlsx_r}
