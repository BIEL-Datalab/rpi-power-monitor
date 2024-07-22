import time
import smbus

# 初始化I2C总线
ADC = smbus.SMBus(1)  # 使用I2C总线1
ADDRESS = 0x24  # ADC的I2C地址
REGISTER = 0x10  # 要读取的寄存器地址
VREF = 5.0  # ADC参考电压
MAX_ADC_VALUE = 1023  # ADC的最大值（12位ADC）
VOLTAGE_TRANSFORM_RATIO = 250 / 5  # 变压器的电压转换比

def read_raw_value():
    try:
        raw_value = ADC.read_word_data(ADDRESS, REGISTER) & 0x03FF  # 只保留低12位数据
        return raw_value
    except Exception as e:
        print(f"Error reading data: {e}")
        return None

def convert_to_voltage(raw_value):
    adc_voltage = (raw_value / MAX_ADC_VALUE) * VREF
    return adc_voltage

def convert_to_ac_voltage(adc_voltage):
    # 限制ADC电压在0到VREF范围内
    if adc_voltage < 0:
        adc_voltage = 0
    elif adc_voltage > VREF:
        adc_voltage = VREF

    ac_voltage = adc_voltage * VOLTAGE_TRANSFORM_RATIO
    return ac_voltage

while True:
    raw_value = read_raw_value()
    if raw_value is not None:
        adc_voltage = convert_to_voltage(raw_value)
        ac_voltage = convert_to_ac_voltage(adc_voltage)
        print(f"Raw value: {raw_value}, ADC Voltage: {adc_voltage:.2f} V, AC Voltage: {ac_voltage:.2f} V")
    else:
        print("Failed to read data.")
    time.sleep(0.01)  # 调整采样频率
