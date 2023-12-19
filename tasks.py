from pathlib import Path

from robocorp import workitems
from robocorp.tasks import get_output_dir, task, setup
from RPA.Excel.Files import Files as Excel
from RPA.Crypto import Crypto
import base64

ENC_KEY = None


@setup
def get_going(task):
    global ENC_KEY
    ENC_KEY = Crypto("AES256")
    ENC_KEY.use_encryption_key_from_vault("aes")


@task
def producer():
    # Split Excel rows into multiple output Work Items for the next step.
    output = get_output_dir() or Path("output")
    filename = "orders.xlsx"
    excel = Excel()

    for item in workitems.inputs:
        path = item.get_file(filename, output / filename)

        excel.open_workbook(path)
        rows = excel.read_worksheet_as_table(header=True)
        customers = rows.group_by_column("Name")
        for customer in customers:
            payload = {
                "Name": customer.get_column("Name")[0],
                "Zip": customer.get_column("Zip")[0],
                "Product": [],
            }
            for row in customer:
                payload["Product"].append(row["Item"])

            payload = encrypt_workitem(payload)
            workitems.outputs.create(payload)


@task
def consumer():
    # Process all the produced input Work Items from the previous step.
    for item in workitems.inputs:
        try:
            name, zipcode, product = decrypt_workitem(item.payload)
            print(f"Processing order: {name}, {zipcode}, {product}")
            assert 1000 <= zipcode <= 9999, "Invalid ZIP code"
            item.done()
        except AssertionError as err:
            item.fail("BUSINESS", code="INVALID_ORDER", message=str(err))
        except KeyError as err:
            item.fail("APPLICATION", code="MISSING_FIELD", message=str(err))


def encrypt_workitem(payload):
    items = string_items = ",".join(payload["Product"])

    encrypted_payload = {
        "Name": base64.b64encode(ENC_KEY.encrypt_string(payload["Name"])).decode(
            "utf-8"
        ),
        "Zip": base64.b64encode(ENC_KEY.encrypt_string(str(payload["Zip"]))).decode(
            "utf-8"
        ),
        "Product": base64.b64encode(ENC_KEY.encrypt_string(items)).decode("utf-8"),
    }
    return encrypted_payload


def decrypt_workitem(payload):
    name = ENC_KEY.decrypt_string(base64.b64decode(payload["Name"]))
    zipcode = int(ENC_KEY.decrypt_string(base64.b64decode(payload["Zip"])))
    product = ENC_KEY.decrypt_string(base64.b64decode(payload["Product"]))
    return name, zipcode, product
