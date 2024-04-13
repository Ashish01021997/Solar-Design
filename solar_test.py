import pvlib
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error

class Solar_GHI:
    @staticmethod
    def train_regression_model(historical_data):
        # Prepare features and target
        X = historical_data[['Latitude', 'Longitude', 'Month', 'Relative Humidity', 'Temperature']]
        print(X)
        y = historical_data['GHI']
        print(y)

        # Split data into training and testing sets
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        # Train linear regression model
        model = LinearRegression()
        model.fit(X_train, y_train)

        # Evaluate model
        train_rmse = mean_squared_error(y_train, model.predict(X_train), squared=False)
        test_rmse = mean_squared_error(y_test, model.predict(X_test), squared=False)

        return model, train_rmse, test_rmse

    @staticmethod
    def get_solar_irradiance(latitude, longitude, temperature, relative_humidity, month, date, model):
        if model:
            # Predict solar irradiance using the trained model
            return model.predict([[latitude, longitude, month, relative_humidity, temperature]])[0]
        else:
            # Location
            location = pvlib.location.Location(latitude, longitude, tz='UTC', altitude=0)

            # Solar position
            solar_position = location.get_solarposition(date)

            # Clear sky model (using Ineichen)
            clearsky = location.get_clearsky(date, model='ineichen')

            # Extracting Global Horizontal Irradiance (GHI)
            ghi = clearsky['ghi']

            return ghi
