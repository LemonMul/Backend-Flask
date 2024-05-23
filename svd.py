from flask import Flask, request, jsonify
from datasets import load_dataset
import pandas as pd
import pickle
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# 모델 및 데이터 로드
with open('svd_model.pkl', 'rb') as f:
    svd_model = pickle.load(f)
with open('pivot_table.pkl', 'rb') as f:
    pivot_table = pickle.load(f)
with open('predictions.pkl', 'rb') as f:
    all_predictions = pickle.load(f)

@app.route('/svd', methods=['GET', 'POST'])
def get_svd_recom():
    user_id = request.args.get('userid', type=int)
    if user_id is None:
        return jsonify({"error": "No user ID provided"}), 400
    
    try:
        user_index = pivot_table.index.get_loc(user_id)
    except KeyError:
        return jsonify({"error": "User ID not found"}), 404

    # 예측 평점 추출
    predicted_ratings = pd.Series(all_predictions[user_index], index=pivot_table.columns)
    predicted_ratings = predicted_ratings.clip(lower=1, upper=5)

    # 예측평점이 높은 순서대로 출력 (상위 1개 출력)
    top_places = predicted_ratings.sort_values(ascending=False)[:1]


    # Place ID를 이용하여 Place Name과 첫 번째 Keyword 찾기
    placeTable = load_dataset("LemonMul/placeTable")
    place_df = pd.DataFrame(placeTable['train'])
    results = []
    for place_id in top_places.index:
        place_info = place_df.loc[place_df['placeID'] == place_id]
        print(f"{place_id}번 장소의 키워드 추출중...")    
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
    print("평점 및 키워드 추출 완료")
    return jsonify(results)
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5002)
