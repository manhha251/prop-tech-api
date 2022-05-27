from flask import Blueprint, request, jsonify
import json
# import concurrent.futures

from database import connectionDB
from utils.geocoding import geocode
# from utils.multiprocessing import list_multiprocess

environments = Blueprint('environments', __name__, url_prefix='/environments')

db_name = 'PropTech'
coll_name = 'environments'

db = connectionDB.connect_database(db_name)


@environments.errorhandler(404)
def page_not_found():
    data = {
        "statusCode": 404,
        "error": "Not Found",
        "message": "The resource could not be found."
    }
    return json.dumps(data), 404


@environments.errorhandler(500)
def internal_server_error():
    data = {
        "statusCode": 500,
        "error": "Internal Server Error",
        "message": "The server has encountered a situation it doesn't know how to handle."
    }
    return json.dumps(data), 500


# @environments.route('/<string:province_code>/<string:district_code>/<string:village_code>', methods=['GET'])
# @environments.route('/<string:province_code>/<string:district_code>', methods=['GET'])
# @environments.route('/<string:province_code>', methods=['GET'])
@environments.route('/', methods=['GET'])
# def get_environment_areas_list(province_code=None, district_code=None, village_code=None):
def get_environment_areas_list():
    """
    Return list of most frequent locations within an area with given environments type
    TODO: Add village code
    ---
    parameters:
        - name: province_code
          in: query
          type: string
          required: false
          description: formatted code for province level (Ex. (Thành phố) Hồ Chí Minh -> ho-chi-minh)
        - name: district_code
          in: query
          type: string
          required: false
          description: formatted code for district level (Ex. Quận 1 -> quan-1)
        - name: village_code
          in: query
          type: string
          required: false
          description: formatted code for village level (Ex. phường Trung Dũng -> phuong-trung-dung)
        - name: type
          in: query
          type: string
          enum: [ngập]
          required: true
          description: Environment types query
        - name: limit
          in: query
          type: int
          required: false
          description: number of maximum records return
          default: all
    responses:
        500:
            description: Internal Server Error
        404:
            description: Resource not found
        200:
            description: List of most frequent reported locations within an area fit given environments type
            schema:
                type: array
                items:
                    type: object
                    properties:
                        fullAddress:
                            type: string
                        provinceCode:
                            type: string
                        districtCode:
                            type: string
                        villageCode:
                            type: string
                        streetCode:
                            type: string
                        lat:
                            type: float
                        long:
                            type: float
                        count:
                            type: integer
                            description: frequency of report
                        type:
                            type: string
                            description: environment types
                    example:
                        fullAddress: Đường Nguyễn Văn Quá, Quận 12, Hồ Chí Minh
                        provinceCode: ho-chi-minh
                        districtCode: quan-12
                        villageCode: ''
                        streetCode: duong-nguyen-van-qua
                        count: 23
                        type: ngập

    """

    collection = db[coll_name]

    params = request.args
    province_code = params.get('province_code')
    district_code = params.get('district_code')
    village_code = params.get('village_code', default="")
    env_type = params.get('type')
    limit = params.get('limit', default='all')

    query = {"type": env_type.lower(), 'lat': {'$exists': True}}
    projection = {"_id": 0}

    if province_code and province_code != "":
        query.update({"provinceCode": province_code})
    if district_code and district_code != "":
        query.update({"districtCode": district_code})
    if village_code and village_code != "":
        return json_response([])

    if limit == 'all':
        results = list(collection.find(query, projection)
                       .sort([('count', -1), ('fullAddress', 1)]))
    else:
        if not limit.isnumeric():
            return 'Argument limit must be \'all\' or a positive integer.', 400
        results = list(collection.find(query, projection)
                       .sort([('count', -1), ('fullAddress', 1)])
                       .limit(int(limit)))

    # results = list_multiprocess(add_geocode, results)
    # print(results)
    return json_response(results)


@environments.route('/all', methods=['GET'])
def get_all():
    """
    Get all environments records
    :return: size
            all records in environments
    """

    collection = db[coll_name]

    results = list(collection.find({'lat': {'$exists': True}}, {'_id': 0}))
    # results = list_multiprocess(add_geocode, results)

    return json_response(results)


def add_geocode(document):

    address = document['fullAddress'].split(' ')
    lat, long = geocode(' '.join(address[1:]))
    if lat is not None:
        document.update({'lat': lat, 'long': long})


def add_geocode_list(address_list):

    removed_index = []
    for index, document in enumerate(address_list):
        address = document['fullAddress'].split(' ')
        lat, long = geocode(' '.join(address[1:]))
        if lat is not None:
            document.update({'lat': lat, 'long': long})
        else:
            removed_index.append(index)

    return [item for idx, item in enumerate(address_list) if idx not in removed_index]


def json_response(payload, status=200):
    return json.dumps(payload, ensure_ascii=False, indent=2), status, {'content-type': 'application/json'}
