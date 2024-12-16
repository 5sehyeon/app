from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit
from datetime import datetime
import time
import pymysql

message=['a']
app = Flask(__name__)
socketio = SocketIO(app) ## 특정 이벤트가 발생하였을 때, 앱으로 신호를 보내는 객체

AWS_RDS_INSTANCE_LOGIN = {
    'host' : 'test-database.cj40aism4clv.ap-southeast-2.rds.amazonaws.com',
    'user' : 'admin',
    'password' : 'nx12131213!',
    'port' : 3306
}

def connect_to_database(db_name):
    try:
        connection = pymysql.connect(
            host=AWS_RDS_INSTANCE_LOGIN['host'],
            user=AWS_RDS_INSTANCE_LOGIN['user'],
            password=AWS_RDS_INSTANCE_LOGIN['password'],
            port=AWS_RDS_INSTANCE_LOGIN['port'],
            database=db_name
        )
        #print(f"{db_name} 데이터 베이스에 연결 성공 하였습니다.")
        return connection
    except Exception as e:
        #print(f'{e} 이러한 오류 때문에, 데이터 베이스 연결에 실패 하였습니다.')
        return None


def query_DATE(db_name):
    c = []
    connection = connect_to_database(db_name)
    if connection:
        try:
            with connection.cursor() as cursor:
                sql = f"""
                SELECT mou_time, lun_time, din_time FROM fixed_suppli
                """
                cursor.execute(sql)
                result = cursor.fetchall()
                for row in result:
                    formatted_times = [str(t) if t is not None else "NULL" for t in row]
                    c.append(formatted_times[0])
                    c.append(formatted_times[1])
                    c.append(formatted_times[2])
                c = set(c)
                c = list(c)
                if "NULL" in c:
                    c.remove("NULL")
                sorted_times = sorted(c, key=lambda t: datetime.strptime(t, '%H:%M:%S').time())
                return sorted_times
            
        except Exception as e:
            print(f'{e} 이러한 오류 때문에, row 추출에 실패하였습니다.')
        finally:
            connection.close()
    else:
        print(f"{db_name} 데이터 베이스 연결에 실패하였습니다.")

def query_date_values(db_name,column,alarm):
    connection = connect_to_database(db_name)
    if connection:
        try:
            with connection.cursor() as cursor:
                sql = f"""
                SELECT *
                FROM fixed_suppli
                WHERE {column} = %s
                """
                cursor.execute(sql, (alarm,))
                row = cursor.fetchall()
                ## 이부분을 수정
                return row
        except Exception as e:
            print(f'{e} 이러한 오류 때문에, row 삽입에 실패하였습니다.')
        finally:
            connection.close()
    else:
        print(f"{db_name} 데이터 베이스 연결에 실패하였습니다.")


"""
@app.route('/button_click', methods=['POST'])
def button_click():
    data = request.json
    username = data.get('username')  # 아이디 추출
    password = data.get('password')  # 비밀번호 추출
    
    print('Received data:', data)  # 전체 요청 데이터 출력
    print('User ID:', username)  # 아이디 출력
    print('User Password:', password)  # 비밀번호 출력
    
    return jsonify({'message': 'Button click received!', 'status': 'success'})
    """


@socketio.on('connect')
def handle_connect():
    print("Kivy 앱이 연결되었습니다.")

@app.route('/update_alarm', methods=['POST'])
def update_alarm():
    data = request.json
    global check
    check = data.get("alarm_time")
    return jsonify({"check" : check})

alarm_time = query_DATE("TMTMTM_DB")
check = 0
def check_alarm():
    global check
    global alarm_time
    #print("check = ", check)
    while True:
        print("다시시작")
        print("check = ", check)
        a = 0
        if check == 1:
            alarm_time = query_DATE("TMTMTM_DB")
            check = 0
            for alarm in alarm_time:
                alarm_time_obj = datetime.strptime(alarm, '%H:%M:%S').time()
                print("집중 !",alarm_time_obj)
                print("check = ", check)
                if check == 1:
                    print("빠져나옴 2")
                    break
                if a == 1:
                    break
                    
                while True:
                    current_time_obj = datetime.now().time().replace(microsecond=0)
                    print(alarm_time_obj)
                    print(f"Current Time: {current_time_obj}, Alarm: {alarm_time_obj}")
                    if check == 1:
                        print("빠져나옴 1")
                        a = 1
                        break
                    
                    if current_time_obj == alarm_time_obj:
                        print("알림 메시지 창이 떴다 !!")
                        if (alarm_time_obj == datetime.strptime("07:59:30", '%H:%M:%S').time() or alarm_time_obj == datetime.strptime("11:59:30", '%H:%M:%S').time() or alarm_time_obj == datetime.strptime("23:59:59", '%H:%M:%S').time() or alarm_time_obj == datetime.strptime("00:00:30", '%H:%M:%S').time()):
                            break
                    
                    
                    current_time_full = datetime.combine(datetime.today(), current_time_obj)
                    alarm_time_full = datetime.combine(datetime.today(), alarm_time_obj)
                    time_difference = abs((current_time_full - alarm_time_full).total_seconds())
                    if (time_difference <= 2 and (str(alarm_time_obj)[6] != '3' or str(alarm_time_obj)[6] != '5')):
                        print("알림 메시지 창이 떴다 !!")
                        socketio.emit('alarm', {'message': '알람 시간입니다!', 'time': str(alarm_time_obj)})  # 알람 시간 포함
                        break
                    if current_time_obj > alarm_time_obj:
                        break
                    if(str(current_time_obj) == "23:59:58"):
                        time.sleep(5)
                    else:
                        time.sleep(1)
            
        elif check == 0:
            for alarm in alarm_time:
                alarm_time_obj = datetime.strptime(alarm, '%H:%M:%S').time()
                print("집중 !",alarm_time_obj)
                if check == 1:
                    print("빠져나옴 2")
                    break
                if a == 1:
                    break
                
                while True:
                    current_time_obj = datetime.now().time().replace(microsecond=0)
                    print(f"Current Time: {current_time_obj}, Alarm: {alarm_time_obj}")
                    if check == 1:
                        print("빠져나옴 1")
                        a = 1
                        break
                    
                    if current_time_obj == alarm_time_obj:
                        print("알림 메시지 창이 떴다 !!")
                        if (alarm_time_obj == datetime.strptime("07:59:30", '%H:%M:%S').time() or alarm_time_obj == datetime.strptime("11:59:30", '%H:%M:%S').time() or alarm_time_obj == datetime.strptime("23:59:59", '%H:%M:%S').time() or alarm_time_obj == datetime.strptime("00:00:30", '%H:%M:%S').time()):
                            break
                
                        
                    current_time_full = datetime.combine(datetime.today(), current_time_obj)
                    alarm_time_full = datetime.combine(datetime.today(), alarm_time_obj)
                    time_difference = abs((current_time_full - alarm_time_full).total_seconds())
                    
                    if (time_difference <= 2 and (str(alarm_time_obj)[6] != '3' or str(alarm_time_obj)[6] != '5')):
                        print("알림 메시지 창이 떴다 !!")
                        socketio.emit('alarm', {'message': '알람 시간입니다!', 'time': str(alarm_time_obj)})  # 알람 시간 포함
                        break
                    if current_time_obj > alarm_time_obj:
                        break
                    if(str(current_time_obj) == "23:59:58"):
                        time.sleep(5)
                    else:
                        time.sleep(1)

                    
            
            
# @app.route('/data_process', methods=['POST'])
# def data_process():
#     data = request.json
#     alarm = data.get("alarm_time")
#     alarm_time = datetime.strptime(alarm, "%H:%M:%S").time()
#     column = "din_time"
#     if alarm_time < datetime.strptime("10:00:00", "%H:%M:%S").time():
#         column = "mou_time"
#     elif alarm_time > datetime.strptime("10:00:00", "%H:%M:%S").time() and alarm_time < datetime.strptime("14:00:00", "%H:%M:%S").time():
#         column = "lun_time"
#     elif alarm_time > datetime.strptime("16:00:00", "%H:%M:%S").time():
#         column = "din_time"
        
#     b = query_date_values("TMTMTM_DB", column, alarm) #약의 정보가 들어있음
#     global message 
#     for i in b:
#         message.append(f"{str(i[1])}:{str(i[8])}:{str(i[3])}")
    
#     return jsonify({'column': column, 'alarm' : alarm})
@app.route('/data_process', methods=['POST'])
def data_process():
    # 데이터 수신 및 확인
    data = request.json
    print(f"Received data: {data}")  # **서버에 요청 도달 여부 확인**
    
    # alarm_time 확인
    if data is None or "alarm_time" not in data:
        print("Error: alarm_time is missing from the request data.")
        return jsonify({'error': 'Invalid data received'}), 400

    alarm = data.get("alarm_time")
    try:
        alarm_time = datetime.strptime(alarm, "%H:%M:%S").time()
    except ValueError:
        print(f"Error: Incorrect alarm_time format: {alarm}")
        return jsonify({'error': 'Invalid time format. Expected HH:MM:SS'}), 400

    # 컬럼 결정 로직
    column = "din_time"
    if alarm_time < datetime.strptime("10:00:00", "%H:%M:%S").time():
        column = "mou_time"
    elif datetime.strptime("10:00:00", "%H:%M:%S").time() <= alarm_time <= datetime.strptime("16:00:00", "%H:%M:%S").time():
        column = "lun_time"
    elif alarm_time > datetime.strptime("16:00:00", "%H:%M:%S").time():
        column = "din_time"
    
    print(f"Selected column: {column}")  # **선택된 컬럼 확인**

    # 데이터베이스 쿼리 실행 및 결과 확인
    b = query_date_values("TMTMTM_DB", column, alarm)
    print(f"Query result: {b}")  # **쿼리 결과 확인**

    # message 리스트에 데이터 추가
    global message
    message.clear()  # 기존 데이터를 초기화하여 중복 방지
    for i in b:
        try:
            # 각 요소를 추가하기 전에 인덱스와 데이터를 확인
            print(f"Appending to message: {i}")  # **추가할 데이터 확인**
            message.append(f"{str(i[1])}:{str(i[8])}:{str(i[3])}")
        except IndexError as e:
            print(f"Error accessing index in result: {e}")
            return jsonify({'error': f'Index error: {str(e)}'}), 500

    print(f"Updated message list: {message}")  # **업데이트된 message 리스트 확인**

    # 처리 결과 반환
    return jsonify({'column': column, 'alarm': alarm, 'message': message})




if __name__ == '__main__':
    socketio.start_background_task(target=check_alarm)  # 시간 체크를 백그라운드에서 실행
    socketio.run(app, debug=True, port=5000)  # Flask와 SocketIO를 함께 실행


