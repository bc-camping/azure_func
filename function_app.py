import azure.functions as func
import requests
import datetime
import math
import json

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

# load precalced location data
def get_location_data(city):
    with open("location_data.json") as f:
        return json.load(f)[city]


@app.route(route="get_campsites")
def get_campsites(req: func.HttpRequest) -> func.HttpResponse:
    name = req.params.get('name')
    start_date = req.params.get('start_date')
    end_date = req.params.get('end_date')
    city = req.params.get('city')
    with open("park_data.json", "r", encoding="utf-8") as f:
        park_data = json.load(f)
    location_data = get_location_data(city)

    current_time = datetime.datetime.utcnow().isoformat() + 'Z'
    cart_response = requests.get('https://camping.bcparks.ca/api/cart')
    cart_data = json.loads(cart_response.text)
    cart_uid = cart_data["cartUid"]
    cart_transaction_uid = cart_data["createTransactionUid"]

    northern_url = f'https://camping.bcparks.ca/api/availability/map?mapId=-2147483550&bookingCategoryId=0&equipmentCategoryId=-32768&subEquipmentCategoryId=-32768&cartUid={cart_uid}&cart_transaction_uid={cart_transaction_uid}&bookingUid=9b7d0ec4-7f50-43cc-b7b9-a223958b49c1&startDate={start_date}&endDate={end_date}&getDailyAvailability=false&isReserving=true&filterData=[]&boatLength=null&boatDraft=null&boatWidth=null&partySize=1&numEquipment=1&seed={current_time}'
    costal_url = f'https://camping.bcparks.ca/api/availability/map?mapId=-2147483549&bookingCategoryId=0&equipmentCategoryId=-32768&subEquipmentCategoryId=-32768&cartUid={cart_uid}&cart_transaction_uid={cart_transaction_uid}&bookingUid=9b7d0ec4-7f50-43cc-b7b9-a223958b49c1&startDate={start_date}&endDate={end_date}&getDailyAvailability=false&isReserving=true&filterData=[]&boatLength=null&boatDraft=null&boatWidth=null&partySize=1&numEquipment=1&seed={current_time}'
    island_url = f'https://camping.bcparks.ca/api/availability/map?mapId=-2147483552&bookingCategoryId=0&equipmentCategoryId=-32768&subEquipmentCategoryId=-32768&cartUid={cart_uid}&cart_transaction_uid={cart_transaction_uid}&bookingUid=9b7d0ec4-7f50-43cc-b7b9-a223958b49c1&startDate={start_date}&endDate={end_date}&getDailyAvailability=false&isReserving=true&filterData=[]&boatLength=null&boatDraft=null&boatWidth=null&partySize=1&numEquipment=1&seed={current_time}'
    interior_url = f'https://camping.bcparks.ca/api/availability/map?mapId=-2147483551&bookingCategoryId=0&equipmentCategoryId=-32768&subEquipmentCategoryId=-32768&cartUid=f{cart_uid}&cart_transaction_uid={cart_transaction_uid}&bookingUid=9b7d0ec4-7f50-43cc-b7b9-a223958b49c1&startDate={start_date}&endDate={end_date}&getDailyAvailability=false&isReserving=true&filterData=[]&boatLength=null&boatDraft=null&boatWidth=null&partySize=1&numEquipment=1&seed={current_time}'

    regions = []
    northern_text = requests.get(northern_url).text
    northern_data = json.loads(northern_text)
    regions.append(northern_data)

    costal_text = requests.get(costal_url).text
    costal_data = json.loads(costal_text)
    regions.append(costal_data)

    island_text = requests.get(island_url).text
    island_data = json.loads(island_text)
    regions.append(island_data)

    interior_text = requests.get(interior_url).text
    interior_data = json.loads(interior_text)
    regions.append(interior_data)

    seen_set = set()
    output_list = []
    for regional_list in regions:
        park_statuses = regional_list['mapLinkAvailabilities']
        for park, status in park_statuses.items():
            if status != [0]:
                continue
            if park in seen_set or park in [
                "-2147483551", # southern interior
                "-2147483550", # northern
                "-2147483549", # Coastal Mainland
                "-2147483325", # Islands
                "-2147483308", # Stone Mountain Overview -> not reservable
                "-2147483415", # Shannon Falls -> picinic site]
            ]:
                continue

            park_info = park_data[park]
            name = park_info["name"]

            try:
                drive_length = location_data[name]
            except:
                print("'"+name+"'")
                drive_length = None

            output_list.append([name, drive_length])

    output_list = sorted(output_list, key=lambda x: x[1] if x[1] is not None else math.inf)
    return func.HttpResponse(
        json.dumps(output_list),
        mimetype="application/json",
    )