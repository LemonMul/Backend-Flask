import React, { useState, useEffect } from 'react';
import { StyleSheet, Text, View } from 'react-native';

const SvdRec = () => {
  const [svdData, setSvdData] = useState([]);
  const [errorMessage, setErrorMessage] = useState('');
  const userid = 17; // 여기 userid 셋팅!

  useEffect(() => {
    console.log('Component mounted, starting to fetch SVD data...');
    loadSvdPlaces(userid);
  }, [userid]);

  const loadSvdPlaces = (userid) => {
    console.log(`Fetching SVD data for user id: ${userid}`);
    fetch(`http://192.168.35.247:5002/svd?userid=${userid}`, {
      method: 'GET',
      headers: {
        'Accept': 'application/json'
      }
    })
    .then(response => {
      console.log('Received response from server');
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return response.json();
    })
    .then(data => {
      console.log('Data successfully parsed as JSON', data);
      if (data.error) {
        setErrorMessage(data.error);
        setSvdData([]);
      } else {
        setSvdData(data);
        setErrorMessage('');
      }
    })
    .catch(error => {
      console.error('Error fetching svd data:', error);
      setErrorMessage('Failed to fetch data.');
    });
  };

  return (
    <View style={styles.container}>
      {svdData.map((item, index) => (
        <View key={index}>
  <Text style={styles.text}>장소이름: {item.placeName}</Text>
  <Text style={styles.text}>키워드: {item.keyword.join(' ')}</Text>
</View>
      ))}
      {errorMessage !== '' && <Text style={styles.error}>{errorMessage}</Text>}
    </View>
  );
};

export default SvdRec;

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  text: {
    fontSize: 16,
    marginVertical: 5,
  },
  error: {
    fontSize: 16,
    color: 'red',
    marginVertical: 5,
  }
});
