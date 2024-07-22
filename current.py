import time
import smbus

# 初始化I2C总线
ADC = smbus.SMBus(1)  # 使用I2C总线1
ADDRESS = 0x24  # ADC的I2C地址
REGISTER = 0x11  # 要读取的寄存器地址
VREF = 5.0  # ADC参考电压
MAX_ADC_VALUE = 1023  # ADC的最大值（10位ADC）
CURRENT_SENSOR_RANGE = 5  # 替换为相应的电流传感器量程，如5A, 10A, 20A

def read_raw_value():
    try:
        raw_value = ADC.read_word_data(ADDRESS, REGISTER) & 0x03FF  # 只保留低10位数据
        return raw_value
    except Exception as e:
        print(f"Error reading data: {e}")
        return None

def convert_to_voltage(raw_value):
    adc_voltage = (raw_value / MAX_ADC_VALUE) * VREF
    return adc_voltage

def convert_to_current(adc_voltage):
    # 将信号转换模块的输出电压（0.2V到2.8V）转换为实际电流值
    if adc_voltage < 0.2:
        return 0  # 如果电压低于0.2V，电流为0
    elif adc_voltage > 2.8:
        adc_voltage = 2.8  # 限制最大电压为2.8V
    # 计算对应的电流值，信号转换模块的输出电压范围为0.2V到2.8V
    ac_current = ((adc_voltage - 0.2) / (2.8 - 0.2)) * CURRENT_SENSOR_RANGE
    return ac_current

while True:
    raw_value = read_raw_value()
    if raw_value is not None:
        adc_voltage = convert_to_voltage(raw_value)
        ac_current = convert_to_current(adc_voltage)
        print(f"Raw value: {raw_value}, ADC Voltage: {adc_voltage:.2f} V, AC Current: {ac_current:.2f} A")
    else:
        print("Failed to read data.")
    time.sleep(0.01)