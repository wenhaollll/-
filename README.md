# -
基于树莓派的双轴追光系统
一、执行环境
硬件环境
主控设备：树莓派（推荐 3B+/4B）
外设配件：PIR 人体红外传感器、两相步进电机 ×2、串口通信模块
网络要求：设备联网，可正常访问远程 MySQL 服务器
软件环境
操作系统：Raspberry Pi OS（Raspbian）
Python 版本：Python 3.7 及以上
依赖库安装命令
bash
运行
pip install RPi.GPIO pyserial pymysql
二、整体功能说明
本项目为树莓派端智能太阳能路灯整套程序，整合人体红外感应、串口通信、太阳方位计算、步进电机太阳追踪、设备运行数据定时上传 MySQL 数据库五大功能，实现路灯自动化、太阳能自动追光、设备状态云端上报。
三、各文件功能与说明
1. light.py 人体红外检测 + 串口通信程序
功能介绍
实时检测人体活动，有人靠近时通过硬件串口向上位机发送提示信息；做状态防抖与防重复发送处理，按下 Ctrl+C 可安全退出，自动释放 GPIO、串口资源。
核心配置字段
IR_DETECT_PIN：红外传感器接入树莓派 GPIO 引脚
SERIAL_PORT：树莓派硬件串口路径
BAUD_RATE：串口通信波特率
SEND_MSG：串口向外发送的提示文本
运行指令
bash
运行
python light.py
2. solar_calc.py 太阳位置计算程序
功能介绍
基于天文算法，根据设备所在经纬度、当前 UTC 时间，实时计算太阳高度角与方位角，为追光程序、数据上报程序提供原始太阳位置数据。
核心配置字段
LAT：设备所在地纬度
LON：设备所在地经度
对外函数
calculate_sun_position：通用太阳位置计算函数
get_current_sun_position：获取当前时刻太阳高度角、方位角（外部程序直接调用）
3. catch_sun.py 步进电机太阳追踪程序
功能介绍
驱动两路步进电机，分别控制方位角（Yaw 轴 / X 轴）、俯仰角（Pitch 轴 / Y 轴），实现开环太阳角度追踪；支持角度容错、自动判断最短转向，程序退出时复位所有电机引脚。
核心配置字段
STEP_PER_DEGREE：每转动 1 度对应的电机步数
DELAY_MS：电机单步运行延时
ANGLE_TOLERANCE：角度偏差容错值
MAX_PITCH、MIN_PITCH：俯仰轴最大、最小限制角度
MAX_YAW、MIN_YAW：方位轴最大、最小限制角度
TARGET_YAW：目标追踪方位角
TARGET_PITCH：目标追踪俯仰角
x_IN1、x_IN2、x_IN3、x_IN4：方位轴步进电机 GPIO 引脚
y_IN1、y_IN2、y_IN3、y_IN4：俯仰轴步进电机 GPIO 引脚
运行指令
bash
运行
python catch_sun.py
4. datahouse.py/light_data.py 设备数据上报程序
两个文件功能一致，light_data.py 为数据库字段修正版本，推荐使用。
功能介绍
自动校验数据库设备信息，不存在则新建设备记录；定时调用太阳计算接口获取太阳角度，模拟电池电量，周期性将设备状态、太阳位置、电量等数据上传至远程 MySQL 数据库。
核心配置字段
DB_CONFIG：MySQL 数据库连接配置，包含主机地址、端口、账号、密码、数据库名、字符集
DEVICE_ID：设备唯一编号
DEVICE_NAME：设备名称
DEVICE_AREA：设备所属区域
LONGITUDE：设备经度
LATITUDE：设备纬度
运行指令
bash
运行
python light_data.py
四、MySQL 数据库字段说明
数据库名：solor
数据表名：lamps
数据表全部字段说明：
light_id：设备唯一编号，主键标识
byname：设备名称
area：设备所在区域
x：设备安装经度
y：设备安装纬度
status：设备在线状态
lamp_status：路灯工作状态
mode：设备运行模式
battrayPackOneCharge /battray_pack_one_charge：电池剩余电量
current_high_angel：实时太阳高度角
current_direction_angel：实时太阳方位角
location_time：数据最后更新时间
duration：运行时长标识
deleted：数据软删除标记
五、运行注意事项
运行硬件相关程序前，确认树莓派 GPIO 接线无误，避免引脚短路。
确保树莓派网络正常，可连通远程 MySQL 服务器地址与端口。
太阳追踪程序运行期间，请勿外力干预电机转动，防止硬件损坏。
所有程序均可使用 Ctrl+C 终止，程序会自动释放硬件资源。
如需修改追光角度、上报周期、串口参数，直接修改对应脚本内配置字段即可。
