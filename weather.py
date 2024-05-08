from flask import Flask, jsonify, request
import requests
import pandas as pd
import numpy as np
from datetime import datetime
from lxml import etree
from haversine import haversine
from datasets import load_dataset

app = Flask(__name__)

@app.route('/weather',methods=['GET'])
def get_weather():

    # 오늘 날짜와 시간 불러오기
    what_date = datetime.now().strftime("%Y%m%d")
    what_time = datetime.now().strftime("%H%M")

    # 기상청 좌표 데이터 로드
    dataset = load_dataset("hscrown/weather_api_info")
    kor_loc = pd.DataFrame(dataset['train'])
    kor_loc = kor_loc.iloc[:,:15].dropna()

    mylat = request.args.get('lat', type=str)
    mylong = request.args.get('long', type=str)

    if not mylat:
        print("response error:not valid user lat")
        mylat = '37.51490409227562'
    if not mylong:
        print("response error:not valid user long")
        mylong = '126.84135103588255'
    

    # 내 좌표 설정
    my_loc = (float(mylat), float(mylong))

    # 가장 가까운 기상청 x, y 좌표 찾기
    min_distance = float('inf')
    nx, ny = None, None
    for index, row in kor_loc.iterrows():
        grid_point = (row['위도(초/100)'], row['경도(초/100)'])
        distance = haversine(my_loc, grid_point)
        if distance < min_distance:
            min_distance = distance
            guName, dongName = row['2단계'], row['3단계']
            nx, ny = row['격자 X'], row['격자 Y']

    # 기상 정보 가져오기
    url = 'http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getUltraSrtNcst'
    params = {
        'serviceKey': 'sX3JWddMWHJxC43fx9mqgcqSsbmAlTpoFTUPbnrE1Db5uVnEAs7gJIL4Z3tzW1u2S6UC+8/go3xYCnG2wDctAQ==',
        'pageNo': '1',
        'numOfRows': '1000',
        'dataType': 'XML',
        'base_date': what_date,
        'base_time': what_time,
        'nx': nx,
        'ny': ny
    }
    response = requests.get(url, params=params)
    root = etree.fromstring(response.content)
    try:
        rain = root.xpath('//obsrValue/text()')[0]
    except (KeyError, IndexError):
        rain = "강수없음"

    try:
        temp = root.xpath('//obsrValue/text()')[3]
    except (KeyError, IndexError):
        temp = 14

    rain_mapping = {
        '0': "강수없음",
        '1': "비",
        '2': "비 또는 눈",
        '3': "눈",
        '4': "소나기",
        '5': "빗방울",
        '6': "빗방울 또는 눈날림",
        '7': "눈날림"
    }
    rain = rain_mapping.get(rain, "기상 정보 없음")

    # 초단기예보데이터
    url2 = 'http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getUltraSrtFcst'


    response2 = requests.get(url2, params=params)
    root2 = etree.fromstring(response2.content)

    # 엘리먼트 선택
    items = root2.xpath('//item')

    # 딕셔너리로 만들기
    data = [{
        "baseDate": item.findtext("baseDate"),
        "baseTime": item.findtext("baseTime"),
        "category": item.findtext("category"),
        "fcstDate": item.findtext("fcstDate"),
        "fcstTime": item.findtext("fcstTime"),
        "fcstValue": item.findtext("fcstValue"),
        "nx": item.findtext("nx"),
        "ny": item.findtext("ny")
    } for item in items]


    # 데이터프레임으로 만들기
    df = pd.DataFrame(data)

    sky_dict = {
        '1': "맑음",
        '2': "구름조금",
        '3': "구름많음",
        '4': "흐림"
    }
    try:
        sky = df.loc[df['category'] == 'SKY', 'fcstValue'].map(sky_dict).values[0]
    except (KeyError, IndexError):
        sky = "흐림"

    # 날씨 정보에 따른 장소 추천 로직
    park_name, lib_name, muse_name = None, None, None
    park_lat, lib_lat, muse_lat = None, None, None
    park_long, lib_long, muse_long = None, None, None
    park_adres, lib_adres, muse_adres = None, None, None
    if (sky in ['맑음', '흐림']) and (rain == ' ') and (15 <= float(temp) <= 29):
        # 공원 정보 불러오기 및 추천 로직
        park_url = 'http://openAPI.seoul.go.kr:8088/57524f76506d656e3732636a52457a/json/SearchParkInfoService/1/1000/'
        park_response = requests.get(park_url)
        park_data = park_response.json()['SearchParkInfoService']['row']
        park = pd.DataFrame(park_data)
        park.rename(columns={'P_PARK': "NAME", 'P_ADDR': "ADRES", 'XCNTS': 'LATITUDE', 'YDNTS': "LONGITUDE"}, inplace=True)
        park['LATITUDE'].replace('', np.nan, inplace=True)
        park['LONGITUDE'].replace('', np.nan, inplace=True)
        park = park.dropna()
        park['LATITUDE'] = park['LATITUDE'].astype(float)
        park['LONGITUDE'] = park['LONGITUDE'].astype(float)
        # 가장 가까운 위치 찾기
        min_distance = float('inf')
        for index, row in park.iterrows():
            point = (row['LATITUDE'], row['LONGITUDE'])
            distance = haversine(my_loc, point)
            if distance < min_distance:
                min_distance = distance
                park_name, park_lat, park_long, park_adres = row['NAME'], row['LATITUDE'], row['LONGITUDE'], row['ADRES']
    elif rain != '비가 오고 있지 않습니다.':
        # 도서관 정보 불러오기 및 추천 로직
        lib_url = 'http://openAPI.seoul.go.kr:8088/57524f76506d656e3732636a52457a/json/SeoulLibraryTimeInfo/1/1000/'
        lib_response = requests.get(lib_url)
        lib_data = lib_response.json()['SeoulLibraryTimeInfo']['row']
        lib = pd.DataFrame(lib_data)
        lib_url2 = 'http://openAPI.seoul.go.kr:8088/57524f76506d656e3732636a52457a/json/SeoulLibraryTimeInfo/1001/2000/'
        lib_response2 = requests.get(lib_url2)
        lib_data2 = lib_response2.json()['SeoulLibraryTimeInfo']['row']
        lib2 = pd.DataFrame(lib_data2)
        lib = pd.concat([lib,lib2])
        lib.rename(columns={'LBRRY_NAME': "NAME", 'ADRES': "ADRES", 'XCNTS': 'LATITUDE', 'YDNTS': "LONGITUDE"}, inplace=True)
        lib['LATITUDE'] = lib['LATITUDE'].astype(float)
        lib['LONGITUDE'] = lib['LONGITUDE'].astype(float)
        # 가장 가까운 위치 찾기
        min_distance = float('inf')
        for index, row in lib.iterrows():
            point = (row['LATITUDE'], row['LONGITUDE'])
            distance = haversine(my_loc, point)
            if distance < min_distance:
                min_distance = distance
                lib_name, lib_lat, lib_long, lib_adres = row['NAME'], row['LATITUDE'], row['LONGITUDE'], row['ADRES']
    else:
        # 박물관 정보 불러오기 및 추천 로직
        muse_url = 'http://openAPI.seoul.go.kr:8088/57524f76506d656e3732636a52457a/json/SeoulMuseumInfo/1/1000/'
        muse_response = requests.get(muse_url)
        muse_data = muse_response.json()['SeoulMuseumInfo']['row']
        muse = pd.DataFrame(muse_data)
        muse.rename(columns={'MUSEUM_NAME': "NAME", 'ADDR': "ADRES", 'XCNTS': 'LATITUDE', 'YDNTS': "LONGITUDE"}, inplace=True)
        muse['LATITUDE'] = muse['LATITUDE'].astype(float)
        muse['LONGITUDE'] = muse['LONGITUDE'].astype(float)
        # 가장 가까운 위치 찾기
        min_distance = float('inf')
        for index, row in muse.iterrows():
            point = (row['LATITUDE'], row['LONGITUDE'])
            distance = haversine(my_loc, point)
            if distance < min_distance:
                min_distance = distance
                muse_name, muse_lat, muse_long, muse_adres = row['NAME'], row['LATITUDE'], row['LONGITUDE'], row['ADRES']

    # 결과 출력
    result = {
        "sky": sky,
        "rain": rain,
        "temp": temp,
        "name": park_name or lib_name or muse_name,
        "latitude": park_lat or lib_lat or muse_lat,
        "longitude": park_long or lib_long or muse_long,
        "address": park_adres or lib_adres or muse_adres,
        "place_type": "공원" if park_name else "도서관" if lib_name else "박물관",
        "guName" : guName,
        "dongName": dongName        
    }
    response = jsonify(result)
    response.headers.add('Content-Type', 'application/json; charset=ASCII') #인코딩 문제 해결
    return response
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
