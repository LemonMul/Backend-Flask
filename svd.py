from flask import Flask, request, jsonify
import pandas as pd
import numpy as np
from sklearn.decomposition import TruncatedSVD
from sklearn.model_selection import train_test_split
from datasets import load_dataset
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/svd', methods=['GET','POST'])
def get_svd_recom():

    
    user_id = request.args.get('userid', type=int)
    if user_id is None:
        return jsonify({"error": "No user ID provided"}), 400
    
    # 데이터셋 로드
    dataset = load_dataset("LemonMul/userTable")
    df = pd.DataFrame(dataset['train'])

    placeTable = load_dataset("LemonMul/placeTable")
    place_df = pd.DataFrame(placeTable['train'])

    # 피벗테이블 생성
    pivot_table = df.pivot(index='userID', columns='placeID', values='rating')

    # 결측치 처리
    pivot_table_filled = pivot_table.apply(lambda x: x.fillna(x.mean()), axis=1)

    # 데이터 배열로 변환
    ratings_matrix = pivot_table_filled.values

    # 훈련 데이터와 테스트 데이터로 나누기
    train_data, test_data = train_test_split(ratings_matrix, test_size=0.2, random_state=42)

    # SVD 사용
    svd_optimal = TruncatedSVD(n_components=14, random_state=42)
    svd_optimal.fit(train_data)

    # 전체 데이터에 대한 예측 평점 계산
    all_predictions = svd_optimal.inverse_transform(svd_optimal.transform(ratings_matrix))

    user_index = pivot_table.index.get_loc(user_id)
    predicted_ratings = pd.Series(all_predictions[user_index], index=pivot_table.columns)
    predicted_ratings = predicted_ratings.clip(lower=1, upper=5)

    # 예측평점이 높은 순서대로 출력 (상위 3개 출력)
    top_places = predicted_ratings.sort_values(ascending=False)[:4]

    # Place ID를 이용하여 Place Name과 첫 번째 Keyword 찾기
    results = []
    for place_id in top_places.index:
        place_info = place_df.loc[place_df['placeID'] == place_id]
        if not place_info.empty:
            place_name = place_info['placeName'].iloc[0]
            keywords = place_info['Keyword'].iloc[0].split() if 'Keyword' in place_info.columns and place_info['Keyword'].iloc[0] else []
            keyword = keywords if keywords else None
            if place_name and keyword:  # place name 과 keyword null 이 아닌것만 리스트에 담음.
                results.append({
                    "placeId": place_id, 
                    "placeName": place_name, 
                    "keyword": keyword
                })

    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5002)
