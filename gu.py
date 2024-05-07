from flask import Flask, jsonify, request
import pandas as pd
import numpy as np
from datasets import load_dataset

app = Flask(__name__)


@app.route('/gu')
def top_places():
    gu_name = request.args.get('gu')  # 요청에서 구 이름을 받아옴
    if not gu_name:
        return jsonify({"error": "구 이름이 제공되지 않았습니다"}), 400

    # 데이터셋 로드
    dataset = load_dataset("LemonMul/userTable")
    df = pd.DataFrame(dataset['train'])

    placeTable = load_dataset("LemonMul/placeTable")
    place_df = pd.DataFrame(placeTable['train'])

    # 데이터 처리
    # 장소 ID별 평점 수 계산
    rating_count_df = df.groupby('placeID')['rating'].count().reset_index(name='count')
    # 장소 ID별 평균 평점 계산, 소수점 첫째 자리에서 반올림
    rating_mean_df = df.groupby('placeID')['rating'].mean().round(1).reset_index(name='rating')

    # 데이터프레임 병합
    merged_df = pd.merge(place_df, rating_count_df, on='placeID')
    merged_df = pd.merge(merged_df, rating_mean_df, on='placeID')
    merged_df = merged_df.sort_values(by='count', ascending=False)
    merged_df = merged_df[merged_df['guName'] == gu_name]

    # 키워드 처리: 키워드가 빈 문자열이거나 결측치인 경우 구 이름 사용
    merged_df['Keyword'] = np.where((merged_df['Keyword'].isna()) | (merged_df['Keyword'].str.strip() == ''), gu_name, merged_df['Keyword'].str.split().str[0])

    # 최종 결과 추출(상위 10개 반환)
    result = merged_df[['Keyword', 'placeName', 'count', 'rating']].head(10).to_dict('records')

    # 결과를 JSON 형태로 반환
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5003)
