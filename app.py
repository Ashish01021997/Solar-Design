from flask import Flask, request, jsonify, render_template
import solar_test as solar_test
import pandas as pd

app = Flask(__name__)

# Load historical solar data (latitude, longitude, GHI)
historical_dataset = pd.read_excel('historical_data.xlsx', sheet_name= 'combined_historical_data')

# Train regression model
model, train_rmse, test_rmse = solar_test.Solar_GHI.train_regression_model(historical_data=historical_dataset)
print(f"Train RMSE: {train_rmse}, Test RMSE: {test_rmse}")  

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/calculate', methods=['POST'])

def calculate():
    # Receive input data from the frontend
    data = request.json

    # Extracting input values
    latitude = data['latitude']
    longitude = data['longitude']
    temperature = data['temperature']
    relative_humidity = data['relative_humidity']
    month = data['month']
    date = data['date']
    Load = data['Load']
    Energy_Demand = data['Energy_Demand']
    eta_inv = data['eta_inv']
    eta_bat = data['eta_bat']
    system_voltage = data['system_voltage']
    days_of_autonomy = data['days_of_autonomy']
    pv_panel_rating = data['pv_panel_rating']
    voc = data['voc']
    isc = data['isc']
    shading_loss_factor = data['shading_loss_factor']
    area_of_pv_panel = data['area_of_pv_panel']
    eta_generator = data['eta_generator']

    # Calculations
    ghi = solar_test.Solar_GHI.get_solar_irradiance(latitude, longitude, temperature, relative_humidity, month, pd.date_range(start=str(date), periods=1),model)
    inverter_size = Load * 1.3 / eta_inv
    battery_size = Energy_Demand / (eta_inv * eta_bat)
    battery_Ah_capacity = (Energy_Demand / (eta_inv * eta_bat)) / system_voltage * days_of_autonomy
    number_of_panels = Load / (eta_inv * eta_bat) / pv_panel_rating
    number_of_series_panels = system_voltage / voc # 22.32 V
    number_of_parallel_panels =  Load/ system_voltage / isc # 18 Amps
    pv_panel_efficiency = (pv_panel_rating * (1 - shading_loss_factor)) /1000 * 100
    system_efficiency = (pv_panel_rating  * (1 - shading_loss_factor)) / float(ghi * area_of_pv_panel) * 100
    generator_capacity = (Energy_Demand - Energy_Demand / (eta_inv * eta_bat)) / eta_generator
    

    # Returning the results
    result = {'ghi': ghi, 'inverter_size': inverter_size,
        'battery_size': battery_size,
        'battery_Ah_capacity': battery_Ah_capacity,
        'number_of_panels': number_of_panels,
        'number_of_series_panels': number_of_series_panels,
        'number_of_parallel_panels': number_of_parallel_panels,
        'pv_panel_efficiency': pv_panel_efficiency,
        'system_efficiency': system_efficiency,
        'generator_capacity': generator_capacity }

    return jsonify({'result': result})

if __name__ == '__main__':
    app.run(debug=True)
