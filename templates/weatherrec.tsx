import React, { useState, useEffect } from 'react';
import { StyleSheet, Text, View } from 'react-native';

const WeatherDashboard = () => {
  const [weatherData, setWeatherData] = useState({});
  const lat = 37.5665;
  const long = 126.978;

  useEffect(() => {
    console.log('Component mounted, starting to fetch weather data...');
    loadWeatherPlaces(lat, long);
  }, []);

  const loadWeatherPlaces = (lat, long) => {
    console.log(`Fetching weather data for latitude: ${lat}, longitude: ${long}`);
    fetch(`http://192.168.35.247:5001/weather?latitude=${lat}&longitude=${long}`)
      .then(response => {
        console.log('Received response from server...');
        if (!response.ok) {
          throw new Error(`HTTP status ${response.status}`);
        }
        return response.json();
      })
      .then(data => {
        console.log('Processing data...', data);
        if (data.error) {
          throw new Error(data.error);
        }
        setWeatherData(data);
      })
      .catch(error => {
        console.error('Error fetching weather data:', error);
        // Assume error handling that does not involve user interface
      });
  };

  return (
    <View style={styles.container}>
      <Text style={styles.text}>Sky: {weatherData.sky}</Text>
      <Text style={styles.text}>Temp: {weatherData.temp}</Text>
      <Text style={styles.text}>Rain: {weatherData.rain}</Text>
      <Text style={styles.text}>Recommendation: {weatherData.name}, Type: {weatherData.place_type}, Address: {weatherData.address}</Text>
      <Text style={styles.text}>위도: {weatherData.latitude}, 경도: {weatherData.longitude}</Text>
    </View>
  );
};

export default WeatherDashboard;

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
  }
});
