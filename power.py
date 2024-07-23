import time
import smbus

# 初始化I2C总线
ADC = smbus.SMBus(1)  # 使用I2C总线1
ADDRESS = 0x24  # ADC的I2C地址
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
    adc_voltage = (raw_value / MAX_ADC_VALUE) * VREF
    return adc_voltage

def convert_to_ac_voltage(adc_voltage):
    ac_voltage = adc_voltage * VOLTAGE_TRANSFORM_RATIO
    return ac_voltage

def convert_to_ac_current(adc_voltage):
    # 将信号转换模块的输出电压（0.2V到2.8V）转换为实际电流值，假设量程为0-5A
    if adc_voltage < 0.2:
        return 0  # 如果电压低于0.2V，电流为0
    elif adc_voltage > 2.8:
        adc_voltage = 2.8  # 限制最大电压为2.8V
    ac_current = ((adc_voltage/2 - 0.2) / (2.8 - 0.2)) * CURRENT_SENSOR_RANGE
    return ac_current

while True:
    # 读取电压和电流的原始数据
    raw_voltage_value = read_raw_value(0x10)  # 假设电压传感器的寄存器地址为0x10
    raw_current_value = read_raw_value(0x11)  # 假设电流传感器的寄存器地址为0x11
    
    if raw_voltage_value is not None and raw_current_value is not None:
        # 将原始数据转换为电压和电流
        adc_voltage = convert_to_voltage(raw_voltage_value)
        ac_voltage = convert_to_ac_voltage(adc_voltage)
        adc_current_voltage = convert_to_voltage(raw_current_value)
        ac_current = convert_to_ac_current(adc_current_voltage)
        
        # 计算瞬时功率
        instantaneous_power = ac_voltage * ac_current
        
        print(f"AC Voltage: {ac_voltage:.2f} V, AC Current: {ac_current:.2f} A, Instantaneous Power: {instantaneous_power:.2f} W")
    else:
        print("Failed to read data.")
    
    time.sleep(0.01)  # 调整采样频率
