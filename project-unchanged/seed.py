from faker import Faker
from faker.providers import internet
import psycopg2
import sys, math, uuid, random, datetime

conn = psycopg2.connect("host=localhost port=5432 dbname=ds user=dev password=devpass")
cur = conn.cursor()


fake = Faker()

DEFAULT_N = 25000
SPLITS = 6

def get_params():
    model = sys.argv[1]
    n = DEFAULT_N
    try:
        c = sys.argv[2]
        if c.isdigit():
            n = int(c)
    except:
        pass
    return model, int(n)


def int_string(n, length):
    s = str(n)
    while len(s) < length:
        s = "0" + s
    return s


def insert_users(n):
    now = datetime.datetime.now()
    
    split_len = math.ceil(n / SPLITS)
    for split in range(SPLITS):
        cedula_prefix = int_string(random.randint(1, 99999999), 10)
        for i in range(split_len):
            cur.execute(
                """
                INSERT INTO users_user (
                    password, 
                    last_login,
                    first_name,
                    last_name,
                    email,
                    has_provided_billing_data,
                    has_provided_password,
                    is_active,
                    is_admin,
                    is_superuser,
                    phone_number,
                    cedula,
                    is_gas_station_admin,
                    city,
                    address,
                    created_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                (
                    str(uuid.uuid4()),
                    now,
                    fake.name(),
                    fake.name(),
                    f"{fake.user_name()}{fake.user_name()}{str(i)}@{fake.domain_name(levels=1)}",
                    False,
                    False,
                    False,
                    False,
                    False,
                    cedula_prefix + cedula_prefix,
                    cedula_prefix + int_string((i + 1) * (split + 1), 5),
                    False,
                    "gye",
                    fake.address(),
                    now,
                ),
            )
        conn.commit()
        print(f"inserted USERS split: {split} total: {split_len}")


def insert_companies(n):
    now = datetime.datetime.now()
    ruc_prefix = int_string(random.randint(1, 99999), 5)
    for i in range(n):
        cur.execute(
            """
            INSERT INTO company_company (
                ruc,
                trade_name,
                business_name,
                img_path,
                email,
                company_logo_path,
                address
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)""",
            (
                ruc_prefix + int_string((i + 1), 8),
                fake.company(),
                fake.company(),
                fake.image_url(),
                f"{fake.user_name()}{fake.user_name()}{str(i)}@{fake.domain_name(levels=1)}",
                fake.image_url(),
                fake.address(),
            ),
        )
    conn.commit()
    print(f"inserted COMPANIES total: {n}")


def insert_stations(n):
    now = datetime.datetime.now()
    cur.execute("SELECT id FROM company_company")
    rs = cur.fetchall()
    ids = [row[0] for row in rs]
    n = math.ceil(n / SPLITS)
    for company_id in ids:
        ruc_prefix = int_string(random.randint(1, 9999999999), 10)
        for i in range(n):
            cur.execute(
                """
                INSERT INTO company_gasstation (
                    company_id,
                    ruc,
                    name,
                    latitude,
                    longitude,
                    address,
                    is_pilot,
                    global_purchase_rating
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
                (
                    company_id,
                    ruc_prefix + int_string((i + 1), 5),
                    fake.company(),
                    random.uniform(-2.157136, -2.156450),
                    random.uniform(-79.898737, -79.898633),
                    fake.address(),
                    False,
                    4.8,
                ),
            )
        conn.commit()
        print(f"inserted STATIONS company_id: {company_id} total: {n}")


if __name__ == "__main__":
    model, n = get_params()

    if model == "users":
        insert_users(n)
    elif model == "company":
        insert_companies(n)
    elif model == "station":
        insert_stations(n)
    elif model == "all":
        insert_users(n)
        insert_companies(6)
        insert_stations(n)

    cur.close()
    conn.close()

