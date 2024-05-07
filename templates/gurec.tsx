import React, { useState } from 'react';
import { StyleSheet, Text, View, Button, FlatList } from 'react-native';

const Page = () => {
  const [places, setPlaces] = useState([]);
  const [errorMessage, setErrorMessage] = useState('');

  const loadTopPlaces = (guName) => {
    fetch(`http://192.168.35.247:5003/gu?gu=${guName}`)
      .then(response => response.json())
      .then(data => {
        if (data.error) {
          setErrorMessage(data.error);
          setPlaces([]);
        } else {
          setPlaces(data);
          setErrorMessage('');
        }
      })
      .catch(error => {
        console.error('인기 장소를 불러오는 데 실패했습니다:', error);
        setErrorMessage('인기 장소를 불러오는 데 실패했습니다.');
        setPlaces([]);
      });
  };

  return (
    <View style={styles.container}>
      <View style={styles.buttonsContainer}>
        {['강남구', '강동구', '강북구', '강서구', '관악구', '광진구', '구로구', '금천구', '노원구', '도봉구', '동대문구', '동작구', '마포구', '서대문구', '서초구', '성동구', '성북구', '송파구', '양천구', '영등포구', '용산구', '은평구', '종로구', '중구', '중랑구'].map((gu, index) => (
          <Button key={index} title={gu} onPress={() => loadTopPlaces(gu)} />
        ))}
      </View>
      <FlatList
        data={places}
        keyExtractor={item => item.placeName}
        renderItem={({ item }) => (
          <Text style={styles.item}>{`${item.placeName} - 키워드: #${item.Keyword}, 평점 수: ${item.count}, 평균 평점: ${item.rating}`}</Text>
        )}
        ListEmptyComponent={<Text style={styles.error}>{errorMessage}</Text>}
      />
    </View>
  );
};

export default Page;

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 10
  },
  buttonsContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'center',
    marginBottom: 10
  },
  item: {
    padding: 5,
  },
  error: {
    color: 'red'
  }
});
