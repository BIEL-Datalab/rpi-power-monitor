import time
import smbus
import pandas as pd

# 初始化I2C总线
ADC = smbus.SMBus(1)  # 使用I2C总线1
ADDRESS = 0x24  # ADC的I2C地址
REGISTER_VOLTAGE = 0x10  # 电压传感器的寄存器地址
REGISTER_CURRENT = 0x11  # 电流传感器的寄存器地址
VREF = 5.0  # ADC参考电压
MAX_ADC_VALUE = 1023  # ADC的最大值（10位ADC）
VOLTAGE_TRANSFORM_RATIO = 250 / 5  # 电压变压器的电压转换比
CURRENT_SENSOR_RANGE = 5  # 替换为相应的电流传感器量程，如5A, 10A, 20A

def read_raw_value(register):
    try:
        raw_value = ADC.read_word_data(ADDRESS, register) & 0x03FF  # 只保留低10位数据
        return raw_value
    except Exception as e:
        print(f"Error reading data: {e}")
        return None

def convert_to_voltage(raw_value):
    return (raw_value / MAX_ADC_VALUE) * VREF

def convert_to_ac_voltage(adc_voltage):
    return adc_voltage * VOLTAGE_TRANSFORM_RATIO

def convert_to_ac_current(adc_voltage):
    if adc_voltage < 0.2:
        return 0
    elif adc_voltage > 2.8:
        adc_voltage = 2.8
    return ((adc_voltage - 0.2) / (2.8 - 0.2)) * CURRENT_SENSOR_RANGE

# 数据采集循环
sampling_duration = 10  # 采样时间（秒）
sampling_interval = 0.01  # 采样间隔（秒）
start_time = time.time()

# 使用列表预存储数据
data = []

while time.time() - start_time < sampling_duration:
    loop_start_time = time.perf_counter()  # 使用更精确的时间函数
    
    raw_voltage_value = read_raw_value(REGISTER_VOLTAGE)
    raw_current_value = read_raw_value(REGISTER_CURRENT)
    
    if raw_voltage_value is not None and raw_current_value is not None:
        adc_voltage = convert_to_voltage(raw_voltage_value)
        ac_voltage = convert_to_ac_voltage(adc_voltage)
        adc_current_voltage = convert_to_voltage(raw_current_value)
        ac_current = convert_to_ac_current(adc_current_voltage)
        instantaneous_power = ac_voltage * ac_current
        
        # 将数据存储到列表中
        data.append({
            'Timestamp': time.strftime("%Y-%m-%d %H:%M:%S.%f"),
            'AC Voltage': ac_voltage,
            'AC Current': ac_current,
            'Instantaneous Power': instantaneous_power
        })
        
    loop_end_time = time.perf_counter()  # 使用更精确的时间函数
    loop_duration = loop_end_time - loop_start_time
    sleep_time = max(sampling_interval - loop_duration, 0)
    if sleep_time > 0:
        time.sleep(sleep_time)

# 将列表转换为DataFrame
df = pd.DataFrame(data)

# 计算平均功率
average_power = df['Instantaneous Power'].mean()
print(f"Average Power: {average_power:.2f} W")

# 计算总耗电量（千瓦特小时，kWh）
total_energy_consumed = average_power * (sampling_duration / 3600) / 1000  # 转换为千瓦特小时
print(f"Total Energy Consumed: {total_energy_consumed:.6f} kWh")

# 为每一行添加总耗电量列
df['Total Energy Consumed (kWh)'] = total_energy_consumed

# 保存更新后的DataFrame到Excel文件
output_file = '/home/pi/Desktop/System Data/sensor_data_with_energy.xlsx'
df.to_excel(output_file, index=False)
print(f"Data saved to '{output_file}'")
