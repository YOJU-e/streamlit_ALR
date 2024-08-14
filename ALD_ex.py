from datetime import datetime, date
import sqlite3
import pandas as pd
import numpy as np
import os
import sys
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup   # need it!
import streamlit as st
import pandas as pd
import time
import sqlite3
import shutil


def is_leap_year(year):
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)

def get_last_day_of_month(year, month):
    if month in [1, 3, 5, 7, 8, 10, 12]:
        return 31
    elif month in [4, 6, 9, 11]:
        return 30
    elif month == 2:
        return 29 if is_leap_year(year) else 28
#chrome_driver_path를 변수로 설정하는 곳: crawling, get_data, ini_setup, update_record
def crawling (selected_option,tempt_from, tempt_to, download_dir):
    # # ChromeDriver 경로를 지정; Chrome최신버전: 126.0.6478.127 (64비트)
    # chrome_driver_path = "./chromedriver-win64/chromedriver.exe"    #파이썬 파일 설치시 같이 설치 가능하게 못하나
    # driver = webdriver.Chrome(ChromeDriverManager().install())
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)

    # chrome_options = Options()  # ChromeOptions 객체 생성
    # service = Service(chrome_driver_path)
    # driver = webdriver.Chrome(service=service, options=chrome_options)

    driver.get("https://apps.ucsiuniversity.edu.my/enquiry/resultLogin.aspx")
    time.sleep(5)
    try:
        # Enter ID, PW(!!!!환경변수로?!!!)
        user_id = "dm"
        password = "dm123"
        # ID 입력란을 찾아서 입력합니다.
        id_input = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.ID, "txtUser"))
        )
        id_input.send_keys(user_id)
        # PW 입력란을 찾아서 입력합니다.
        pw_input = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.ID, "txtPwd"))
        )
        pw_input.send_keys(password)
        # 로그인 버튼을 클릭합니다.
        login_button = WebDriverWait(driver, 3).until(
            EC.element_to_be_clickable((By.ID, "cmdLogin"))
        )
        login_button.click()
        time.sleep(5)
        print("로그인 성공!")

    except Exception as e:
        print(f"로그인 실패: {e}")
        time.sleep(5)

    try:
        time.sleep(3)
        # subsiciaries선택 후 campaign선택
        # Select Subsiciaries
        subsiciaries_dropdown = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.ID, "ddlSubsidiary"))
        )
        subsiciaries_dropdown.click()
        # Select Subsidiaries!!! (ex: "SEC")
        option_sec = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, "//option[@value='SEC']"))
        )
        option_sec.click()
        campaign_dropdown = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.ID, "ddlPage"))
        )
        campaign_dropdown.click()
        # 원하는 옵션 선택!!! (ex: "1. Faculty Programme Page Enquiry Form")
        option_enquiry = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, f"//option[text()='{selected_option}']"))
        )
        option_enquiry.click()
        # from
        from_input = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.ID, "txtDateF"))
        )
        from_input.send_keys(tempt_from)
        # to
        to_input = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.ID, "txtDateT"))
        )
        to_input.send_keys(tempt_to)
        # submit 버튼 클릭
        submit_button = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.ID, "btnSubmit"))
        )
        submit_button.click()
        print("Submit 버튼을 클릭했습니다.")
        # export_to_excel 버튼 클릭
        export_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.ID, "btnExport"))
        )
        export_button.click()
        print("Export to Excel 버튼을 클릭했습니다.")
        # 페이지 로딩을 기다림
        WebDriverWait(driver, 7).until(
            EC.presence_of_element_located((By.ID, "your_result_element_id"))  # 결과가 나타나는 요소의 ID를 사용
        )
        print(driver.page_source)

    except Exception as e:
        print(f"저장 실패: {e}")
        time.sleep(5)

    html_content = None
    crawled_data = None
    # download_dir = ".\data"
    try:
        downloaded_files = os.listdir(download_dir)
        downloaded_file = max(
            [os.path.join(download_dir, f) for f in downloaded_files if f.endswith('.xls')],
            key=os.path.getctime
        )
        xls_file = downloaded_file
        print('xls_file의 이름',xls_file)

        # Read as a HTML file
        with open(xls_file, 'r', encoding='utf-8') as file:
            html_content = file.read()
        # Parsing HTML using BeautifulSoup
        soup = BeautifulSoup(html_content, 'lxml')
        table = soup.find('table')

        # Change HTML table to DataFrame
        if table:
            crawled_data = pd.read_html(str(table))[0]
            print('crawled_data:',crawled_data)
        else:
            print("No table found in the HTML content.")
            return None

        try:
            os.remove(xls_file)
            print(f"{xls_file} is deleted.")

        except Exception as e:
            print(f"Fail to delete: {e}")

        return crawled_data

    except Exception as e:
        print(f"An error occurred: {e}")
        time.sleep(5)

    finally:
        driver.quit()

def get_data (o,t_year,t_month,download_dir):
    df = pd.DataFrame()
    for y in range(2022,t_year+1):
        # print(y)
        for m in range(1,10,4): #1,5,9
                from_date = str(m)+'/'+str(1)+'/'+ str(y)
                last_day = get_last_day_of_month(y,m+3)
                to_date = str(m+3)+'/'+str(last_day)+'/'+ str(y)
                df_data = crawling(o,from_date,to_date,download_dir)
                df = pd.concat([df,df_data],ignore_index=True)
    return df

def update_data (o,t_year,t_month,download_dir):
    from_date = str(t_month)+'/'+str(1)+'/'+ str(t_year)
    last_day = get_last_day_of_month(t_year,t_month)
    to_date = str(t_month)+'/'+str(last_day)+'/'+ str(t_year)
    df = crawling(o,from_date,to_date,download_dir)
    return df

def get_day_with_suffix(day):
    if day in [1, 21, 31]:
        return f"{day}st"
    elif day in [2, 22]:
        return f"{day}nd"
    elif day == 3:
        return f"{day}rd"
    else:
        return f"{day}th"

def number_to_month(month):
    months = {
        "January": 1, "February": 2, "March": 3, "April": 4,
        "May": 5, "June": 6, "July": 7, "August": 8,
        "September": 9, "October": 10, "November": 11, "December": 12
    }
    for key, value in months.items():
        if value == month:
            return key
    return "Invalid month name"

def month_to_number(month_name):
    month_dict = {
        'January': 1,
        'February': 2,
        'March': 3,
        'April': 4,
        'May': 5,
        'June': 6,
        'July': 7,
        'August': 8,
        'September': 9,
        'October': 10,
        'November': 11,
        'December': 12
    }
    if month_name in month_dict:
        return month_dict[month_name]
    else:
        raise ValueError("Invalid month name")

def unique_rows_p(df):
    if df is None:
        return None
    else:
        # 필요 행만 있는 df
        print(df.columns)
        df_selected = df[['Name', 'InputDate', 'Tel', 'Email', 'Programme', 'source']]
        # Delete rows which contains word 'test' in 'Name' col
        df_filtered = df_selected[~df_selected['Name'].str.contains('test', case=False, na=False)]
        # Delete rows if value of programme is None
        df_cleaned = df_filtered.dropna(subset=['Programme'])
        # only get source == google
        df_cleaned['source'] = df_cleaned['source'].astype(str)
        df_cleared = df_cleaned[df_cleaned['source'].str.contains('google', case=False)]
        # Add needed cols
        df_cleared['InputDate'] = pd.to_datetime(df_cleared['InputDate'])
        df_cleared['Year'] = df_cleared['InputDate'].dt.year
        df_cleared['Month'] = df_cleared['InputDate'].dt.month
        df_cleared['Month_e'] = df_cleared['InputDate'].dt.strftime('%B')
        df_cleared['Day'] = df_cleared['InputDate'].dt.day
        # Leave only num in Tel col
        df_cleared['Tel'] = df_cleared['Tel'].astype(str).str.replace(r'\D', '', regex=True)
        # print('tel에 번호만 남긴거',df_cleared[df_cleared['Day'] == 3][['Name','Day','Tel','Programme']])
        # Delete duplicates
        df_dropped = df_cleared.drop_duplicates()
        # print('중복 제거',df_dropped[df_dropped['Day'] == 3])
        # 만약 이름, 번호, 이메일 중 하나라도 값이 같고 programme이 같으면 둘 중 하나를 제거
        df_dropped_e = df_dropped.drop_duplicates(subset=['Email','Programme'],keep='last')
        print('이메일 같은거',df_dropped_e[df_dropped_e['Day'] == 3].head(50))
        df_dropped_t = df_dropped_e.drop_duplicates(subset=['Tel','Programme'],keep='last')
        print('번호 같은거',df_dropped_t[df_dropped_t['Day'] == 3].head(50))
        df_dropped_n = df_dropped_t.drop_duplicates(subset=['Name','Programme'],keep='last')
        # print('이름 같은거 ',df_dropped_n[df_dropped_n['Day'] == 3].head(50))
        return df_dropped_n

def unique_rows_(df):       # Use when option is 4. General Scholarship
    if df is None:
        return None
    else:
        df_selected = df[['Name', 'InputDate', 'Tel', 'Email', 'Programme', 'source']]
        df_filtered = df_selected[~df_selected['Name'].str.contains('test', case=False, na=False)]
        df_filtered['source'] = df_filtered['source'].astype(str)
        df_filtered = df_filtered[df_filtered['source'].str.contains('google', case=False)]
        df_filtered['InputDate'] = pd.to_datetime(df_filtered['InputDate'])
        df_filtered['Year'] = df_filtered['InputDate'].dt.year
        df_filtered['Month'] = df_filtered['InputDate'].dt.month
        df_filtered['Month_e'] = df_filtered['InputDate'].dt.strftime('%B')
        df_filtered['Day'] = df_filtered['InputDate'].dt.day
        df_filtered['Tel'] = df_filtered['Tel'].astype(str).str.replace(r'\D', '', regex=True)
        df_dropped = df_filtered.drop_duplicates()
        print(df_dropped)
        df_dropped_e = df_dropped.drop_duplicates(subset=['Email','Programme'],keep='last')
        df_dropped_t = df_dropped_e.drop_duplicates(subset=['Tel','Programme'],keep='last')
        df_dropped_n = df_dropped_t.drop_duplicates(subset=['Name','Programme'],keep='last')
        return df_dropped_n

def processing_to_dataframe1(ckCat_csv_path,Programs_csv_path,df_data,last_day,t_month):
            df_ckCat = pd.read_csv(ckCat_csv_path)  #Programme Code,category,Program
            df_Pgs = pd.read_csv(Programs_csv_path)
            programs_list = df_Pgs.iloc[:, 0].tolist() #첫번째 열의 모든 값을 리스트로
            con = pd.DataFrame()
            con['program'] = programs_list
            for i in range(1, last_day+1):
                matched_programs = []
                for j in range(len(df_data)):
                    date = df_data['Day'].iloc[j]
                    code = df_data['Programme'].iloc[j]
                    if date == i and code in df_ckCat['Programme Code'].values:
                        program_index = df_ckCat[df_ckCat['Programme Code'] == code].index[0]
                        matched_program = df_ckCat['Program'].iloc[program_index]
                        matched_programs.append(matched_program)
                count_list = [0] * len(con)

                for matched_program in matched_programs:
                    for idx, program in enumerate(con['program']):
                        if program == matched_program:
                            count_list[idx] += 1

                con[f'{t_month}{get_day_with_suffix(i)}'] = count_list
                # print(f'{t_month}{get_day_with_suffix(i)}',count_list)
            return con

def processing_to_dataframe2(no, df_data, last_day, t_month):
    con = pd.DataFrame()
    columns = [f'{t_month}{get_day_with_suffix(d)}' for d in range(1, last_day + 1)]
    con = pd.DataFrame([0]*len(columns)).T
    con.columns = columns
    con.iloc[0] = 0

    day_groups = df_data.groupby('Day')
    for day, day_df in day_groups:
        count = len(day_df)
        con[f'{t_month}{get_day_with_suffix(day)}'] = count

    if no == 3:
        con['program'] = 'Master & PhD Programme'
        con = con[['program'] + [col for col in con.columns if col != 'program']]
    elif no == 4:
        con['program'] = 'SEC-General Scholarship'
        con = con[['program'] + [col for col in con.columns if col != 'program']]
    elif no == 5:
        con['program'] = 'SEC-Foundation'
        con = con[['program'] + [col for col in con.columns if col != 'program']]
    elif no == 6:
        con['program'] = 'SEC-Diploma & Foundation'
        con = con[['program'] + [col for col in con.columns if col != 'program']]
    elif no == 7:
        con['program'] = 'SEC-MARA Scholarship'
        con = con[['program'] + [col for col in con.columns if col != 'program']]
    elif no == 8:
        con['program'] = 'SEC-Open Day/Enrolment Day/Info Day'
        con = con[['program'] + [col for col in con.columns if col != 'program']]
    elif no == 10:
        con['program'] = 'SEC-UEC'
        con = con[['program'] + [col for col in con.columns if col != 'program']]
    elif no == 11:   #no == 11
        con['program'] = 'SEC-Open Day/Enrolment Day/Info Day'
        con = con[['program'] + [col for col in con.columns if col != 'program']]

    return con

def create_database_if_not_exists(db_name):
    if not db_name.endswith('.db'):
        db_name += '.db'

    if not os.path.exists(db_name):
        try:
            conn = sqlite3.connect(db_name)
            conn.close()
            print(f"Database '{db_name}' created successfully.")
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
    else:
        print(f"Database '{db_name}' already exists. No action taken.")

def check_table_exists(db_name, table_name):
    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        #cursor.execute(f"DROP TABLE {table_name}")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
        result = cursor.fetchone()
        conn.close()

        if result:
            return 1
        else:
            return 0
    except sqlite3.Error as e:
        print(f"An error occurred in check: {e}")
        return 0

def create_table_if_not_exists(db_name, table_name):    #테이블 만들때 program_name 칼럼 만들자!
    if not db_name.endswith('.db'):
        db_name += '.db'
    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        #cursor.execute(f"DROP TABLE {table_name}") #삭제해야함
        conn.commit()
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS {table_name} (
                program TEXT PRIMARY KEY
            )
            ''')
        conn.commit()
        print(f"Table '{table_name}' created successfully.")
    except sqlite3.Error as e:
        print(f"An error occurred in creating a table: {e}")

def add_column(db_name, table_name, column_name):

    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    # 테이블에 열이 존재하는지 확인하고, 없으면 추가
    cursor.execute(f'PRAGMA table_info({table_name})')
    columns = [column[1] for column in cursor.fetchall()]

    if column_name not in columns:
        cursor.execute(f'ALTER TABLE {table_name} ADD COLUMN {column_name} INTEGER')
        conn.commit()

    conn.close()

def initialize_database(Programs_csv_path):
    # Get today's date
    today_date = datetime.now()
    today_str = today_date.strftime('%Y-%m-%d')
    t_month = today_date.month
    t_year = today_date.year

    #Program 카테고리 가져오기 -> 현재는 add column에 포함되어있음
    df_raw = pd.read_csv(Programs_csv_path)
    es_data1 = df_raw['Program'].tolist()

    #DB와 table 생성
    for y in range(2022,t_year+1):
        db_name = f'EXDB_{y}.db'
        create_database_if_not_exists(db_name)
        print(f'{db_name}가 생성되었습니다.')
        if y == t_year:
            for m in range(1,t_month+1):
                e_month = number_to_month(m)
                table_name = f'{e_month}_{y}'
                create_table_if_not_exists(db_name,table_name)
                #2열부터 날짜형태의 col만들기
                m_last_day = get_last_day_of_month(y,m)
                for d in range(1,m_last_day+1):
                    column_name = e_month + get_day_with_suffix(d)
                    add_column(db_name,table_name,column_name)

        else:
            for m in range(1,13):
                e_month = number_to_month(m)
                table_name = f'{e_month}_{y}'
                m_last_day = get_last_day_of_month(y,m) # m의 last day
                create_table_if_not_exists(db_name,table_name)  #1열 'program' 만듬
                #2열부터 날짜형태의 col만들기
                m_last_day = get_last_day_of_month(y,m)
                for d in range(1,m_last_day+1):
                    column_name = e_month + get_day_with_suffix(d)
                    add_column(db_name,table_name,column_name)

def insert_value_to_table(db_name, table_name, program_name, column_name, value):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    update_query = f'''
    UPDATE {table_name}
    SET {column_name} = ?
    WHERE program = ?
    '''
    cursor.execute(update_query, (value, program_name))
    conn.commit()
    conn.close()

def drop_table(db_name, table_name):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute(f'DROP TABLE IF EXISTS {table_name}')
    conn.commit()
    #tables = cursor.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()
    conn.close()

def daily_row_sum_dataframe(db_name,table_name):
    st.session_state.daily_row_displayed = True
    conn = sqlite3.connect(db_name)
    daily_df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
    conn.close()
    daily_df.set_index('program', inplace=True)
    row_sums = daily_df.sum(axis=1)
    row_sums_df = pd.DataFrame(row_sums, columns=['Total Leads'])
    return row_sums_df

def daily_col_sum_dataframe(db_name,table_name):
    st.session_state.daily_col_displayed = True
    conn = sqlite3.connect(db_name)
    daily_df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
    conn.close()
    daily_df.set_index('program', inplace=True)
    column_sums = daily_df.sum(axis=0)
    column_sums_df = pd.DataFrame(column_sums, columns=['Total Leads']).transpose()
    return column_sums_df

def daily_dataframe(db_name,table_name):
    st.session_state.daily_displayed = True
    conn = sqlite3.connect(db_name)
    daily_df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
    conn.close()
    daily_df.set_index('program', inplace=True)
    return daily_df

def display_dataframe(db_name,table_name):   #이거 다시 수정해야함.
    conn = sqlite3.connect(db_name)
    df_table = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
    conn.close()

    # 각 행의 합계 계산하여 'Row_Total' 열 추가
    numeric_cols = df_table.select_dtypes(include=['number']).columns # 열 선택
    df_table['Total'] = df_table[numeric_cols].sum(axis=1)

    # 각 열의 합계 계산하여 마지막 행 추가
    total_row = df_table[numeric_cols].sum()
    total_row['Total'] = total_row.sum()  # 'Total' 열의 총 합
    total_row['program'] = 'Total_Leads'
    total_row_df = pd.DataFrame(total_row).transpose()
    df_table = pd.concat([df_table, total_row_df], ignore_index=True)

    return df_table

def convert_to_date(date_str, i_year):
    # 예시: 'July1st' 같은 문자열을 '2024-07-01' 같은 형식으로 변환
    month_map = {
        'January': 1, 'February': 2, 'March': 3, 'April': 4,
        'May': 5, 'June': 6, 'July': 7, 'August': 8,
        'September': 9, 'October': 10, 'November': 11, 'December': 12
    }
    if date_str is None:
        return None

    if date_str == "Total":
        return None
    try:
        # 예를 들어 'July1st'에서 'July'와 '1'을 추출
        for month in month_map:
            if date_str.startswith(month):
                day_str = date_str[len(month):]
                day = ''.join(filter(str.isdigit, day_str))
                if day:
                    month_number = month_map[month]
                    return datetime(year= i_year, month=month_number, day=int(day))
                break
        return None
    except ValueError as e:
        print(f"Error converting {date_str}: {e}")
        return None

def display_weekly_df2(df,i_year):
    st.session_state.weekly_displayed = True
    def convert_to_date_wrapped(date_str):
        return convert_to_date(date_str, i_year)

    df_melted = df.melt(id_vars=['program'], var_name='Date', value_name='Value')
    df_melted['Date'] = df_melted['Date'].apply(convert_to_date_wrapped)

    # 날짜를 포함하는 주 식별 (각 날짜를 해당 주의 월요일로 변환)
    df_melted['Week'] = df_melted['Date'].dt.to_period('W').apply(lambda r: r.start_time)
    # 주별 데이터 집계 (예: 값의 합계)
    weekly_df = df_melted.groupby(['program', 'Week']).agg({'Value': 'sum'}).reset_index()
    # 주(week) 기반 데이터프레임으로 Pivot
    weekly_pivot_df = weekly_df.pivot(index='program', columns='Week', values='Value').fillna(0)
    # weekly_pivot_df.loc['Total'] = weekly_pivot_df.sum()    # 각 열의 값을 합
    # weekly_pivot_df['Total'] = weekly_pivot_df.sum(axis=1)  # 각 행의 값을 합

    return weekly_pivot_df

def display_weekly_dataframe(df,i_year):
    st.session_state.weekly_displayed = True
    def convert_to_date_wrapped(date_str):
        return convert_to_date(date_str, i_year)

    df = df.drop(columns=['Total'])
    df = df[df['program'] != 'Total_Leads']

    df_melted = df.melt(id_vars=['program'], var_name='Date', value_name='Value')
    df_melted['Date'] = df_melted['Date'].apply(convert_to_date_wrapped)

    # 날짜를 포함하는 주 식별 (각 날짜를 해당 주의 월요일로 변환)
    df_melted['Week'] = df_melted['Date'].dt.to_period('W').apply(lambda r: r.start_time)
    # 주별 데이터 집계 (예: 값의 합계)
    weekly_df = df_melted.groupby(['program', 'Week']).agg({'Value': 'sum'}).reset_index()
    # 주(week) 기반 데이터프레임으로 Pivot
    weekly_pivot_df = weekly_df.pivot(index='program', columns='Week', values='Value').fillna(0)
    weekly_pivot_df.loc['Total'] = weekly_pivot_df.sum()    # 각 열의 값을 합
    weekly_pivot_df['Total'] = weekly_pivot_df.sum(axis=1)  # 각 행의 값을 합

    return weekly_pivot_df

def initialize_setup(option_file_path,download_dir,ckCat_csv_path,Programs_csv_path):
        # option_file_path = 'C:/vscode/AutoLeadReturn/LeadDatas/option_list.xlsx'
        df_options = pd.read_excel(option_file_path, engine='openpyxl')
        options = df_options['Options'].tolist()

        # Get today's date
        today_date = datetime.now()
        today_str = today_date.strftime('%Y-%m-%d')
        t_month = today_date.month #숫자 달
        t_day = today_date.day
        t_year = today_date.year
        last_day = get_last_day_of_month(t_year,t_month)

        initialize_database(Programs_csv_path)

        #처음 세팅 함수로
        df_12 = pd.DataFrame()
        df_811 = pd.DataFrame()

        for o in options:
            if o == '1. Faculty Programme Page Enquiry Form':
                df_1 = get_data(o,t_year,t_month,download_dir)
                df_12 = pd.concat([df_12,df_1],ignore_index=True)
                print("")
            elif o == '2. Individual Programme Page Enquiry Form': # 2번 실행시 1~6이 용량이 만항서 실행이 안됌
                df_2 = get_data(o,t_year,t_month,download_dir)
                df_12 = pd.concat([df_12,df_2],ignore_index=True)
                df_12_cleared = unique_rows_p(df_12)
                year_groups = df_12_cleared.groupby('Year')
                for year, year_df in year_groups:
                    db_name = f'EXDB_{year}.db'
                    month_groups = year_df.groupby('Month_e')

                    for month, month_df in month_groups:    #ex. month: June
                        # if month == 'July':
                        #     month_df.to_excel('month_df_7_12_data.xlsx', index=False)
                        table_name = f"{month}_{year}"
                        n_month = month_to_number(month)
                        last_day = get_last_day_of_month(year,n_month)
                        p_df = processing_to_dataframe1(ckCat_csv_path,Programs_csv_path,month_df,last_day,month)    #리턴: 데이터프레임<--테이블의 열이름과 같은 col을 가진
                        # print(f'{month}_{year}에 저장될 df: \n', p_df)
                        conn = sqlite3.connect(db_name)
                        cursor = conn.cursor()
                        p_df.to_sql(table_name, conn, if_exists='append', index=False)
                        conn.close()

            elif o == '3. Masters & PhD Programme':
                df_3 = get_data(o,t_year,t_month,download_dir)
                df_3_cleared = unique_rows_p(df_3)

                year_groups = df_3_cleared.groupby('Year')
                for year, year_df in year_groups:
                    db_name = f'EXDB_{year}.db'
                    month_groups = year_df.groupby('Month_e')
                    for month, month_df in month_groups:    #ex. month: June
                        table_name = f"{month}_{year}"
                        n_month = month_to_number(month)
                        last_day = get_last_day_of_month(year,n_month)
                        p_df = processing_to_dataframe2(3, month_df, last_day, month)
                        print(f'{month}_{year}에 저장될 df: \n', p_df)
                        conn = sqlite3.connect(db_name)
                        cursor = conn.cursor()
                        p_df.to_sql(table_name, conn, if_exists='append', index=False)
                        conn.close()

            elif o == '4. General Scholarship':
                df_4 = get_data(o,t_year,t_month,download_dir)
                df_4_cleared = unique_rows_(df_4)  #Programme 없음 주의
                year_groups = df_4_cleared.groupby('Year')
                for year, year_df in year_groups:
                    db_name = f'EXDB_{year}.db'
                    month_groups = year_df.groupby('Month_e')
                    for month, month_df in month_groups:    #ex. month: June
                        table_name = f"{month}_{year}"
                        n_month = month_to_number(month)
                        last_day = get_last_day_of_month(year,n_month)
                        p_df = processing_to_dataframe2(4, month_df, last_day, month)
                        print(f'{month}_{year}에 저장될 df: \n', p_df)
                        conn = sqlite3.connect(db_name)
                        cursor = conn.cursor()
                        p_df.to_sql(table_name, conn, if_exists='append', index=False)
                        conn.close()

            elif o == '5. Foundation ONLY Landing Page':
                df_5 = get_data(o,t_year,t_month,download_dir)
                df_5_cleared = unique_rows_p(df_5)
                year_groups = df_5_cleared.groupby('Year')
                for year, year_df in year_groups:
                    db_name = f'EXDB_{year}.db'
                    month_groups = year_df.groupby('Month_e')
                    for month, month_df in month_groups:    #ex. month: June
                        table_name = f"{month}_{year}"
                        n_month = month_to_number(month)
                        last_day = get_last_day_of_month(year,n_month)
                        p_df = processing_to_dataframe2(5, month_df, last_day, month)
                        print(f'{month}_{year}에 저장될 df: \n', p_df)
                        conn = sqlite3.connect(db_name)
                        cursor = conn.cursor()
                        p_df.to_sql(table_name, conn, if_exists='append', index=False)
                        conn.close()

            elif o == '6. Foundation & Diploma Landing Page':
                df_6 = get_data(o,t_year,t_month,download_dir)
                df_6_cleared = unique_rows_p(df_6)
                year_groups = df_6_cleared.groupby('Year')
                for year, year_df in year_groups:
                    db_name = f'EXDB_{year}.db'
                    month_groups = year_df.groupby('Month_e')
                    for month, month_df in month_groups:    #ex. month: June
                        table_name = f"{month}_{year}"
                        n_month = month_to_number(month)
                        last_day = get_last_day_of_month(year,n_month)
                        p_df = processing_to_dataframe2(6, month_df, last_day, month)
                        print(f'{month}_{year}에 저장될 df: \n', p_df)
                        conn = sqlite3.connect(db_name)
                        cursor = conn.cursor()
                        p_df.to_sql(table_name, conn, if_exists='append', index=False)
                        conn.close()

            elif o == '7. MARA Scholar':
                df_7 = get_data(o,t_year,t_month,download_dir)
                df_7_cleared = unique_rows_p(df_7)
                year_groups = df_7_cleared.groupby('Year')
                for year, year_df in year_groups:
                    db_name = f'EXDB_{year}.db'
                    month_groups = year_df.groupby('Month_e')
                    for month, month_df in month_groups:    #ex. month: June
                        table_name = f"{month}_{year}"
                        n_month = month_to_number(month)
                        last_day = get_last_day_of_month(year,n_month)
                        p_df = processing_to_dataframe2(7, month_df, last_day, month)
                        print(f'{month}_{year}에 저장될 df: \n', p_df)
                        conn = sqlite3.connect(db_name)
                        cursor = conn.cursor()
                        p_df.to_sql(table_name, conn, if_exists='append', index=False)
                        conn.close()

            elif o == '8. Open Day':
                df_8 = get_data(o,t_year,t_month,download_dir)
                df_811 = pd.concat([df_811,df_8],ignore_index=True)
            elif o == '11. Info Day & Enrolment Day':
                df_11 = get_data(o,t_year,t_month,download_dir)
                df_811 = pd.concat([df_811,df_11],ignore_index=True)
                df_811_cleared = unique_rows_p(df_811)
                year_groups = df_811_cleared.groupby('Year')
                for year, year_df in year_groups:
                    db_name = f'EXDB_{year}.db'
                    month_groups = year_df.groupby('Month_e')
                    for month, month_df in month_groups:    #ex. month: June
                        table_name = f"{month}_{year}"
                        n_month = month_to_number(month)
                        last_day = get_last_day_of_month(year,n_month)
                        p_df = processing_to_dataframe2(11, month_df, last_day, month)
                        print(f'{month}_{year}에 저장될 df: \n', p_df)
                        conn = sqlite3.connect(db_name)
                        cursor = conn.cursor()
                        cursor.execute(f"DELETE FROM {table_name} WHERE program = 'SEC-Open Day/Enrolment Day/Info Day'")
                        p_df.to_sql(table_name, conn, if_exists='append', index=False)
                        conn.close()

            elif o == '10. UEC Study Grants (English Version)':
                df_10 = get_data(o,t_year,t_month,download_dir)
                df_10_cleared = unique_rows_p(df_10)
                year_groups = df_10_cleared.groupby('Year')
                for year, year_df in year_groups:
                    db_name = f'EXDB_{year}.db'
                    month_groups = year_df.groupby('Month_e')
                    for month, month_df in month_groups:    #ex. month: June
                        table_name = f"{month}_{year}"
                        n_month = month_to_number(month)
                        last_day = get_last_day_of_month(year,n_month)
                        p_df = processing_to_dataframe2(10, month_df, last_day, month)
                        print(f'{month}_{year}에 저장될 df: \n', p_df)
                        conn = sqlite3.connect(db_name)
                        cursor = conn.cursor()
                        p_df.to_sql(table_name, conn, if_exists='append', index=False)
                        conn.close()

#업데이트 함수
def update_records(option_file_path, t_year, t_month,download_dir,ckCat_csv_path,Programs_csv_path):
    st.session_state.updated = True

    df_options = pd.read_excel(option_file_path, engine='openpyxl')
    options = df_options['Options'].tolist()
    # print(options)

    e_month = number_to_month(t_month)
    last_day = get_last_day_of_month(t_year,t_month)

    df_12 = pd.DataFrame()
    df_811 = pd.DataFrame()

    for o in options:
        if o == '1. Faculty Programme Page Enquiry Form':
            df_1 = update_data(o,t_year,t_month,download_dir)
            print(df_1)
            df_12 = pd.concat([df_12,df_1],ignore_index=True)
            print(df_12)
        elif o == '2. Individual Programme Page Enquiry Form':
            df_2 = update_data(o,t_year,t_month,download_dir)
            print(df_2)
            df_12 = pd.concat([df_12,df_2],ignore_index=True)
            print(df_12)
            # df_12.to_excel('df_12.xlsx', index=False)
            df_12_cleared = unique_rows_p(df_12)
            # df_12_cleared.to_excel('df_12_cleared_data.xlsx', index=False)
            db_name = f'EXDB_{t_year}.db'
            create_database_if_not_exists(db_name)
            table_name = f"{e_month}_{t_year}"
            last_day = get_last_day_of_month(t_year,t_month)
            p_df = processing_to_dataframe1(ckCat_csv_path,Programs_csv_path,df_12_cleared,last_day,e_month) #month: 영어이름

            is_table_exists = check_table_exists(db_name, table_name)
            if is_table_exists == 1:
                drop_table(db_name, table_name)
                create_table_if_not_exists(db_name, table_name)
                for d in range(1,last_day+1):
                    column_name = e_month + get_day_with_suffix(d)
                    add_column(db_name,table_name,column_name)
            else:
                create_table_if_not_exists(db_name, table_name)
                for d in range(1,last_day+1):
                    column_name = e_month + get_day_with_suffix(d)
                    add_column(db_name,table_name,column_name)

            conn = sqlite3.connect(db_name)
            cursor = conn.cursor()
            p_df.to_sql(table_name, conn, if_exists='append', index=False)
            conn.close()

        elif o == '3. Masters & PhD Programme':
            df_3 = update_data(o,t_year,t_month, download_dir)
            df_3_cleared = unique_rows_p(df_3)
            print('df3: ',df_3_cleared)
            if df_3_cleared is None:
                continue
            else:
                db_name = f'EXDB_{t_year}.db'
                create_database_if_not_exists(db_name)    #금방 주석처리했음
                table_name = f"{e_month}_{t_year}"
                last_day = get_last_day_of_month(t_year,t_month)
                p_df = processing_to_dataframe2(3, df_3_cleared, last_day, e_month) #month: 영어이름

                conn = sqlite3.connect(db_name)
                cursor = conn.cursor()
                p_df.to_sql(table_name, conn, if_exists='append', index=False)  #이게 문제인듯
                conn.close()

        elif o == '4. General Scholarship':
            df_4 = update_data(o,t_year,t_month, download_dir)
            df_4_cleared = unique_rows_(df_4)
            print('df4: ',df_4_cleared)
            if df_4_cleared is None:
                continue
            else:
                db_name = f'EXDB_{t_year}.db'
                create_database_if_not_exists(db_name)
                table_name = f"{e_month}_{t_year}"
                last_day = get_last_day_of_month(t_year,t_month)
                p_df = processing_to_dataframe2(4, df_4_cleared, last_day, e_month) #month: 영어이름
                conn = sqlite3.connect(db_name)
                cursor = conn.cursor()
                p_df.to_sql(table_name, conn, if_exists='append', index=False)
                conn.close()

        elif o == '5. Foundation ONLY Landing Page':
            df_5 = update_data(o,t_year,t_month, download_dir)
            df_5_cleared = unique_rows_p(df_5)
            print('df5: ',df_5_cleared)
            if df_5_cleared is None:
                continue
            else:
                db_name = f'EXDB_{t_year}.db'
                create_database_if_not_exists(db_name)
                table_name = f"{e_month}_{t_year}"
                last_day = get_last_day_of_month(t_year,t_month)
                p_df = processing_to_dataframe2(5, df_5_cleared, last_day, e_month) #month: 영어이름
                conn = sqlite3.connect(db_name)
                cursor = conn.cursor()
                p_df.to_sql(table_name, conn, if_exists='append', index=False)
                conn.close()

        elif o == '6. Foundation & Diploma Landing Page':
            df_6 = update_data(o,t_year,t_month,download_dir)
            df_6_cleared = unique_rows_p(df_6)
            print('df6: ',df_6_cleared)
            if df_6_cleared is None:
                continue
            else:
                db_name = f'EXDB_{t_year}.db'
                create_database_if_not_exists(db_name)
                table_name = f"{e_month}_{t_year}"
                last_day = get_last_day_of_month(t_year,t_month)
                p_df = processing_to_dataframe2(6, df_6_cleared, last_day, e_month) #month: 영어이름
                conn = sqlite3.connect(db_name)
                cursor = conn.cursor()
                p_df.to_sql(table_name, conn, if_exists='append', index=False)
                conn.close()

        elif o == '7. MARA Scholar':
            df_7 = update_data(o,t_year,t_month,download_dir)
            df_7_cleared = unique_rows_p(df_7)
            print('df7: ',df_7_cleared)
            if df_7_cleared is None:
                continue
            else:
                db_name = f'EXDB_{t_year}.db'
                create_database_if_not_exists(db_name)
                table_name = f"{e_month}_{t_year}"
                last_day = get_last_day_of_month(t_year,t_month)
                p_df = processing_to_dataframe2(7, df_7_cleared, last_day, e_month) #month: 영어이름
                conn = sqlite3.connect(db_name)
                cursor = conn.cursor()
                p_df.to_sql(table_name, conn, if_exists='append', index=False)
                conn.close()

        elif o == '8. Open Day':
            df_8 = update_data(o,t_year,t_month,download_dir)
            df_811 = pd.concat([df_811,df_8],ignore_index=True)

        elif o == '10. UEC Study Grants (English Version)':
            df_10 = update_data(o,t_year,t_month,download_dir)
            df_10_cleared = unique_rows_p(df_10)
            print('df10: ',df_10_cleared)
            if df_10_cleared is None:
                continue
            else:
                db_name = f'EXDB_{t_year}.db'
                create_database_if_not_exists(db_name)
                table_name = f"{e_month}_{t_year}"
                last_day = get_last_day_of_month(t_year,t_month)
                p_df = processing_to_dataframe2(10, df_10_cleared, last_day, e_month) #month: 영어이름

                conn = sqlite3.connect(db_name)
                cursor = conn.cursor()
                p_df.to_sql(table_name, conn, if_exists='append', index=False)
                conn.close()
        elif o == '11. Info Day & Enrolment Day':
            df_11 = update_data(o,t_year,t_month,download_dir)
            df_811 = pd.concat([df_811,df_11],ignore_index=True)
            df_811_cleared = unique_rows_p(df_811)
            print('df811: ',df_811_cleared)
            if df_811_cleared is None:
                continue
            else:
                db_name = f'EXDB_{t_year}.db'
                create_database_if_not_exists(db_name)
                table_name = f"{e_month}_{t_year}"
                last_day = get_last_day_of_month(t_year,t_month)
                p_df = processing_to_dataframe2(11, df_811_cleared, last_day, e_month) #month: 영어이름

                conn = sqlite3.connect(db_name)
                cursor = conn.cursor()
                p_df.to_sql(table_name, conn, if_exists='append', index=False)
                conn.close()

    db_name = f'EXDB_{t_year}.db'   # t_year, t_month
    table_name = f"{e_month}_{t_year}"
    conn = sqlite3.connect(db_name)
    query = f"SELECT * FROM {table_name}"
    df = pd.read_sql_query(query, conn)
    conn.close()

    return df

def calculate_total_leads(t_year, t_month):
    df_total = pd.DataFrame()
    for y in range(2022,t_year+1):
        db_name = f'EXDB_{y}.db'
        if y == t_year:
            monthly_total = [0] * 12
            for m in range(1,t_month+1):
                e_month = number_to_month(m)
                table_name = f'{e_month}_{y}'
                conn = sqlite3.connect(db_name)
                cursor = conn.cursor()
                df_table = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
                conn.close()
                df_table = df_table.fillna(0)
                month_total = df_table.drop('program',axis=1).values.sum()
                monthly_total[m-1] = month_total
            df_total[f'{y}'] = monthly_total

        else:
            monthly_total = [0] * 12
            for m in range(1,13):
                e_month = number_to_month(m)
                table_name = f'{e_month}_{y}'
                conn = sqlite3.connect(db_name)
                cursor = conn.cursor()
                df_table = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
                conn.close()
                df_table = df_table.fillna(0)
                month_total = df_table.drop('program',axis=1).values.sum()
                monthly_total[m-1] = month_total
            df_total[f'{y}'] = monthly_total

    months = ['January', 'February', 'March', 'April','May','June','July','August','September', 'October', 'November', 'December']
    df_total.insert(0, 'month', months)
    sum_row = df_total.iloc[:, 1:].sum()
    sum_row['month'] = 'Total'
    df_total = pd.concat([df_total, pd.DataFrame(sum_row).T], ignore_index=True)

    return df_total

def concat_d_df(programs,f_year, f_month, t_year, t_month):
    st.session_state.w_cpl_df = True
    df = pd.DataFrame({'program':programs})
    df.set_index(df.columns[0], inplace=True)

    for y in range(f_year,t_year+1):
        db_name = f'EXDB_{y}.db'
        if t_year - f_year == 0:
            for m in range(f_month,t_month+1):
                e_month = number_to_month(m)
                table_name = f'{e_month}_{y}'
                conn = sqlite3.connect(db_name)
                df_table = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
                conn.close()
                df_table.rename(columns={df_table.columns[0]: 'program'}, inplace=True)
                df_table.set_index(df_table.columns[0], inplace=True)
                new_columns = [convert_to_date(col,y) for col in df_table.columns]
                df_table.columns = new_columns
                df = pd.concat([df, df_table], axis=1)
        else:
            if t_year - y == 0:
                for m in range(1,t_month+1):
                    e_month = number_to_month(m)
                    table_name = f'{e_month}_{y}'
                    conn = sqlite3.connect(db_name)
                    df_table = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
                    conn.close()
                    df_table.rename(columns={df_table.columns[0]: 'program'}, inplace=True)
                    df_table.set_index(df_table.columns[0], inplace=True)
                    new_columns = [convert_to_date(col,y) for col in df_table.columns]
                    df_table.columns = new_columns
                    df = pd.concat([df, df_table], axis=1)
            else:
                for m in range(1,13):
                    e_month = number_to_month(m)
                    table_name = f'{e_month}_{y}'
                    conn = sqlite3.connect(db_name)
                    df_table = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
                    conn.close()
                    df_table.rename(columns={df_table.columns[0]: 'program'}, inplace=True)
                    df_table.set_index(df_table.columns[0], inplace=True)
                    new_columns = [convert_to_date(col,y) for col in df_table.columns]
                    df_table.columns = new_columns
                    df = pd.concat([df, df_table], axis=1)
    # print(df)
    df = df.T
    df.index.name = 'Date'

    # 주별로 그룹화하여 합계를 구함
    weekly_df = df.resample('W').sum()

    # 다시 원래 형태로 전치
    weekly_df = weekly_df.T
    weekly_df.columns = pd.to_datetime(weekly_df.columns)
    weekly_df.columns = [col.date() for col in weekly_df.columns]

    return weekly_df

def resource_path(relative_path):
    try:
        # PyInstaller에서 실행 중인 경우
        base_path = sys._MEIPASS
    except Exception:
        # PyInstaller에서 실행 중이지 않은 경우
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def main():
    st.title('LeadDataAutoReturn')
    st.markdown('---')
    Goto_option_file_path = resource_path("data/option_list.xlsx") #'./data/option_list.xlsx'
    ckCat_csv_path = resource_path("data/ck_PC1.csv") #"./data/ck_PC1.csv" # to get name of programs
    Programs_csv_path = resource_path("data/Category_s1.csv") # "./data/Category_s1.csv" # to get Programme(unique value)
    programs_file_path = resource_path("data/program_list.xlsx")
    df_programs = pd.read_excel(programs_file_path, engine='openpyxl')

    # Goto_option_file_path = "./data/option_list.xlsx" #'./data/option_list.xlsx'
    # ckCat_csv_path = "./data/ck_PC1.csv" #"./data/ck_PC1.csv" # to get name of programs
    # Programs_csv_path = "./data/Category_s1.csv" # "./data/Category_s1.csv" # to get Programme(unique value)
    # programs_file_path = "./data/program_list.xlsx"
    # df_programs = pd.read_excel(programs_file_path, engine='openpyxl')
    programs = df_programs.iloc[:, 0].tolist()
    # chrome_driver_path = "chromedriver-win64/chromedriver.exe" # "./chromedriver-win64/chromedriver.exe"

    today_date = datetime.now()
    e_month = today_date.strftime('%B') #July
    t_month = today_date.month
    t_year = today_date.year

    # Session initialization
    if 'updated' not in st.session_state:
        st.session_state.updated = False
    # if 'daily_row_sum_df' not in st.session_state:
    #     st.session_state.daily_row_displayed = False
    if 'daily_col_sum_df' not in st.session_state:
        st.session_state.daily_col_displayed = False
    if 'daily_displayed' not in st.session_state:
        st.session_state.daily_displayed = False
    if 'weekly_displayed' not in st.session_state:
        st.session_state.weekly_displayed = False
    if 'w_cpl_df' not in st.session_state:
        st.session_state.w_cpl_df = False
    if 't_cpl_df' not in st.session_state:
        st.session_state.t_cpl_df = False

    # 옵션 파일 경로, 나머지 2개 파일 경로, 다운 디렉토리
    # 주소 입력 창
    if 'download_dir' not in st.session_state:
        st.session_state['download_dir'] = ''

    download_dir = st.text_input('Download Dir: ',"C:/Users/your_username/Downloads")
    if download_dir:
        st.session_state['download_dir'] = download_dir

    # 초기 설정 버튼!!!!!!!!!!!!!!!!!!!!!!!!!이거 처음 화면 열자마자 테이블 없으면 실행<- exe만들어본 이후에 한번 더 해보기
    if st.button('Initialization'):
        initialize_setup(Goto_option_file_path, download_dir,ckCat_csv_path,Programs_csv_path)

    # 업데이트 버튼
    years = list(range(2022, t_year + 1))  # From 2022 to now
    months = list(range(1, 13))  # From January to December

    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        selected_year = st.selectbox('Select Year', years, index=years.index(t_year), key='year_select_for_update')
    with col2:
        selected_month = st.selectbox('Select Month', months, index=t_month-1, key='month_select_for_update')
    st.markdown("""
    <style>
    .stButton button {
        margin-top: 28px;  
    }
    </style>
    """, unsafe_allow_html=True)
    with col3:
        update_btn = st.button('Update')

    if update_btn:
        # 선택된 값을 변수에 저장
        i_year = selected_year
        i_month = selected_month
        e_month = number_to_month(i_month)
        db_name = f'EXDB_{i_year}.db'   # t_year, t_month
        table_name = f"{e_month}_{i_year}"
        update_records(Goto_option_file_path,i_year,i_month,download_dir,ckCat_csv_path,Programs_csv_path)
        st.write('Updated!')

    st.markdown('---')

    #데일리 리트 체크 화면
    st.subheader('Leads')
    # st.markdown('---')
    years = list(range(2022, t_year + 1))
    months = list(range(1, 13))

    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        selected_year = st.selectbox('Select Year', years, index=years.index(t_year), key='year_select_for_d_check')
    with col2:
        selected_month = st.selectbox('Select Month', months, index=t_month-1, key='month_select_for_d_check')
    with col3:
        submit_btn = st.button('Submit')

    if submit_btn:
        i_year = selected_year
        i_month = selected_month
        e_month = number_to_month(i_month)
        db_name = f'EXDB_{i_year}.db'   # t_year, t_month
        table_name = f"{e_month}_{i_year}"
        print(i_month,i_year,e_month)
        daily_df = display_dataframe(db_name,table_name)
        # daily_row_sum_df = daily_row_sum_dataframe(db_name,table_name)
        daily_col_sum_df = daily_col_sum_dataframe(db_name,table_name)
        daily_df2 = daily_dataframe(db_name,table_name)
        # daily_df2.columns = pd.to_datetime(daily_df2.columns)
        # daily_df2.columns = [col.date() for col in daily_df2.columns]
        numeric_cols = daily_df2.select_dtypes(include=['number']).columns # 열 선택
        daily_df2['Total'] = daily_df2[numeric_cols].sum(axis=1)

        weekly_df = display_weekly_dataframe(daily_df,i_year)
        yearly_df = calculate_total_leads(t_year, t_month)
        yearly_df.set_index(yearly_df.columns[0], inplace=True)

        st.session_state.daily_df = daily_df
        st.session_state.daily_df2 = daily_df2
        st.session_state.daily_col_sum_df = daily_col_sum_df
        # st.session_state.daily_row_sum_df = daily_row_sum_df
        st.session_state.weekly_df = weekly_df
        st.session_state.yearly_df = yearly_df

    if st.session_state.weekly_displayed and 'daily_df2' in st.session_state:
        st.write(f'Daily Report')
        st.dataframe(st.session_state.daily_df2.style.set_sticky())
        st.dataframe(st.session_state.daily_col_sum_df)
        # st.dataframe(st.session_state.daily_row_sum_df)

        st.write("Weekly Report")
        st.dataframe(st.session_state.weekly_df)

        st.write('Yearly Report')
        st.dataframe(st.session_state.yearly_df)

    #CPL 체크 화면
    st.markdown('---')
    st.subheader('CPLs')    #Have 37 categories, default = 1
    # st.markdown('---')
    years = list(range(2022, t_year + 1))
    months = list(range(1, 13))

    col1, col2, col3, col4 = st.columns([1,2,2,1])
    with col1:
        st.write('From')
    with col2:
        selected_f_year = st.selectbox('Select Year', years, index=years.index(t_year), key='f_year_select_for_CPL')
    with col3:
        selected_f_month = st.selectbox('Select Month', months, index=t_month-1, key='f_month_select_for_CPL')
    with col4:
        cal_btn = st.button('Calculate')

    col1, col2, col3, col4 = st.columns([1,2,2,1])
    with col1:
        st.write('To')
    with col2:
        selected_t_year = st.selectbox('Select Year', years, index=years.index(t_year), key='t_year_select_for_CPL')
    with col3:
        selected_t_month = st.selectbox('Select Month', months, index=t_month-1, key='t_month_select_for_CPL')
    with col4:
        st.write(' ')

    program_list_df = pd.DataFrame([programs[i:i+6] for i in range(0, len(programs), 6)])
    if 'costs' not in st.session_state:
        st.session_state.costs = [''] * 37
    col1, col2, col3, col4, col5, col6 = st.columns([1, 1, 1, 1, 1, 1])
    with col1:
        cost_AcS_PG = st.text_input(f'{program_list_df.iloc[0,0]}', value='1', key=f'cost_{program_list_df.iloc[0,0]}')
        st.session_state.costs[0] = cost_AcS_PG
    with col2:
        cost_AcS_UG = st.text_input(f'{program_list_df.iloc[0,1]}', value='1', key=f'cost_{program_list_df.iloc[0,1]}')
        st.session_state.costs[1] = cost_AcS_UG
    with col3:
        cost_ApS_PG = st.text_input(f'{program_list_df.iloc[0,2]}', value='1', key=f'cost_{program_list_df.iloc[0,2]}')
        st.session_state.costs[2] = cost_ApS_PG
    with col4:
        cost_ApS_UG = st.text_input(f'{program_list_df.iloc[0,3]}', value='1', key=f'cost_{program_list_df.iloc[0,3]}')
        st.session_state.costs[3] = cost_ApS_UG
    with col5:
        cost_A_PG = st.text_input(f'{program_list_df.iloc[0,4]}', value='1', key=f'cost_{program_list_df.iloc[0,4]}')
        st.session_state.costs[4] = cost_A_PG
    with col6:
        cost_A_UG = st.text_input(f'{program_list_df.iloc[0,5]}', value='1', key=f'cost_{program_list_df.iloc[0,5]}')
        st.session_state.costs[5] = cost_A_UG

    col1, col2, col3, col4, col5, col6 = st.columns([1, 1, 1, 1, 1, 1])
    with col1:
        cost_B_PG = st.text_input(f'{program_list_df.iloc[1,0]}', value='1', key=f'cost_{program_list_df.iloc[1,0]}')
        st.session_state.costs[6] = cost_B_PG
    with col2:
        cost_B_UG = st.text_input(f'{program_list_df.iloc[1,1]}', value='1', key=f'cost_{program_list_df.iloc[1,1]}')
        st.session_state.costs[7] = cost_B_UG
    with col3:
        cost_E_PG = st.text_input(f'{program_list_df.iloc[1,2]}', value='1', key=f'cost_{program_list_df.iloc[1,2]}')
        st.session_state.costs[8] = cost_E_PG
    with col4:
        cost_E_UG = st.text_input(f'{program_list_df.iloc[1,3]}', value='1', key=f'cost_{program_list_df.iloc[1,3]}')
        st.session_state.costs[9] = cost_E_UG
    with col5:
        cost_FMHS_PG = st.text_input(f'{program_list_df.iloc[1,4]}', value='1', key=f'cost_{program_list_df.iloc[1,4]}')
        st.session_state.costs[10] = cost_FMHS_PG
    with col6:
        cost_FMHS_UG = st.text_input(f'{program_list_df.iloc[1,5]}', value='1', key=f'cost_{program_list_df.iloc[1,5]}')
        st.session_state.costs[11] = cost_FMHS_UG

    col1, col2, col3, col4, col5, col6 = st.columns([1, 1, 1, 1, 1, 1])
    with col1:
        cost_FMHS_UG_N = st.text_input(f'{program_list_df.iloc[2,0]}', value='1', key=f'cost_{program_list_df.iloc[2,0]}')
        st.session_state.costs[12] = cost_FMHS_UG_N
    with col2:
        cost_FOSSLA_PG = st.text_input(f'{program_list_df.iloc[2,1]}', value='1', key=f'cost_{program_list_df.iloc[2,1]}')
        st.session_state.costs[13] = cost_FOSSLA_PG
    with col3:
        cost_FOSSLA_UG = st.text_input(f'{program_list_df.iloc[2,2]}', value='1', key=f'cost_{program_list_df.iloc[2,2]}')
        st.session_state.costs[14] = cost_FOSSLA_UG
    with col4:
        cost_F_art = st.text_input(f'{program_list_df.iloc[2,3]}', value='1', key=f'cost_{program_list_df.iloc[2,3]}')
        st.session_state.costs[15] = cost_F_art
    with col5:
        cost_F_sci = st.text_input(f'{program_list_df.iloc[2,4]}', value='1', key=f'cost_{program_list_df.iloc[2,4]}')
        st.session_state.costs[16] = cost_F_sci
    with col6:
        cost_FPS_PG = st.text_input(f'{program_list_df.iloc[2,5]}', value='1', key=f'cost_{program_list_df.iloc[2,5]}')
        st.session_state.costs[17] = cost_FPS_PG

    col1, col2, col3, col4, col5, col6 = st.columns([1, 1, 1, 1, 1, 1])
    with col1:
        cost_FPS_UG = st.text_input(f'{program_list_df.iloc[3,0]}', value='1', key=f'cost_{program_list_df.iloc[3,0]}')
        st.session_state.costs[18] = cost_FPS_UG
    with col2:
        cost_GBS_PG = st.text_input(f'{program_list_df.iloc[3,1]}', value='1', key=f'cost_{program_list_df.iloc[3,1]}')
        st.session_state.costs[19] = cost_GBS_PG
    with col3:
        cost_H_PG = st.text_input(f'{program_list_df.iloc[3,2]}', value='1', key=f'cost_{program_list_df.iloc[3,2]}')
        st.session_state.costs[20] = cost_H_PG
    with col4:
        cost_H_UG = st.text_input(f'{program_list_df.iloc[3,3]}', value='1', key=f'cost_{program_list_df.iloc[3,3]}')
        st.session_state.costs[21] = cost_H_UG
    with col5:
        cost_IASDA_PG = st.text_input(f'{program_list_df.iloc[3,4]}', value='1', key=f'cost_{program_list_df.iloc[3,4]}')
        st.session_state.costs[22] = cost_IASDA_PG
    with col6:
        cost_IASDA_UG = st.text_input(f'{program_list_df.iloc[3,5]}', value='1', key=f'cost_{program_list_df.iloc[3,5]}')
        st.session_state.costs[23] = cost_IASDA_UG

    col1, col2, col3, col4, col5, col6 = st.columns([1, 1, 1, 1, 1, 1])
    with col1:
        cost_ICAD_PG = st.text_input(f'{program_list_df.iloc[4,0]}', value='1', key=f'cost_{program_list_df.iloc[4,0]}')
        st.session_state.costs[24] = cost_ICAD_PG
    with col2:
        cost_ICAD_UG = st.text_input(f'{program_list_df.iloc[4,1]}', value='1', key=f'cost_{program_list_df.iloc[4,1]}')
        st.session_state.costs[25] = cost_ICAD_UG
    with col3:
        cost_IMUS_PG = st.text_input(f'{program_list_df.iloc[4,2]}', value='1', key=f'cost_{program_list_df.iloc[4,2]}')
        st.session_state.costs[26] = cost_IMUS_PG
    with col4:
        cost_IMUS_UG = st.text_input(f'{program_list_df.iloc[4,3]}', value='1', key=f'cost_{program_list_df.iloc[4,3]}')
        st.session_state.costs[27] = cost_IMUS_UG
    with col5:
        cost_IT_PG = st.text_input(f'{program_list_df.iloc[4,4]}', value='1', key=f'cost_{program_list_df.iloc[4,4]}')
        st.session_state.costs[28] = cost_IT_PG
    with col6:
        cost_IT_UG = st.text_input(f'{program_list_df.iloc[4,5]}', value='1', key=f'cost_{program_list_df.iloc[4,5]}')
        st.session_state.costs[29] = cost_IT_UG

    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
    with col1:
        cost_MPhD = st.text_input(f'{program_list_df.iloc[5,0]}', value='1', key=f'cost_{program_list_df.iloc[5,0]}')
        st.session_state.costs[30] = cost_MPhD
    with col2:
        cost_SEC_GS = st.text_input(f'{program_list_df.iloc[5,1]}', value='1', key=f'cost_{program_list_df.iloc[5,1]}')
        st.session_state.costs[31] = cost_SEC_GS
    with col3:
        cost_SEC_F = st.text_input(f'{program_list_df.iloc[5,2]}', value='1', key=f'cost_{program_list_df.iloc[5,2]}')
        st.session_state.costs[32] = cost_SEC_F
    with col4:
        cost_SEC_DF = st.text_input(f'{program_list_df.iloc[5,3]}', value='1', key=f'cost_{program_list_df.iloc[5,3]}')
        st.session_state.costs[33] = cost_SEC_DF

    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        cost_SEC_MS = st.text_input(f'{program_list_df.iloc[5,4]}', value='1', key=f'cost_{program_list_df.iloc[5,4]}')
        st.session_state.costs[34] = cost_SEC_MS
    with col2:
        cost_SEC_OEI = st.text_input(f'{program_list_df.iloc[5,5]}', value='1', key=f'cost_{program_list_df.iloc[5,5]}')
        st.session_state.costs[35] = cost_SEC_OEI
    with col3:
        cost_SEC_UEC = st.text_input(f'{program_list_df.iloc[6,0]}', value='1', key=f'cost_{program_list_df.iloc[6,0]}')
        st.session_state.costs[36] = cost_SEC_UEC

    if cal_btn:
        f_year = selected_f_year
        f_month = selected_f_month
        t_year = selected_t_year
        t_month = selected_t_month

        # weekly cpl 계산
        w_df = concat_d_df(programs, f_year, f_month, t_year, t_month)
        # st.write(w_df)
        # w_df = display_weekly_df2(d_df,i_year)
        column_names = w_df.columns.tolist()
        index_values = w_df.index.tolist()

        for p in index_values:
            if p == 'Actuarial Science (PG)':
                for c in range(0, len(column_names)):
                    i = index_values.index('Actuarial Science (PG)')
                    cost = float(cost_AcS_PG)
                    value = cost/w_df.iloc[i, c]
                    w_df.iloc[i, c] = value
            if p == 'Actuarial Science (UG)':
                for c in range(0, len(column_names)):
                    i = index_values.index('Actuarial Science (UG)')
                    cost = float(cost_AcS_UG)
                    value = cost/w_df.iloc[i, c]
                    w_df.iloc[i, c] = value
            if p == 'Applied Sciences (PG)':
                for c in range(0, len(column_names)):
                    i = index_values.index('Applied Sciences (PG)')
                    cost = float(cost_ApS_PG)
                    value = cost/w_df.iloc[i, c]
                    w_df.iloc[i, c] = value
            if p == 'Applied Sciences (UG)':
                for c in range(0, len(column_names)):
                    i = index_values.index('Applied Sciences (UG)')
                    cost = float(cost_ApS_UG)
                    value = cost/w_df.iloc[i, c]
                    w_df.iloc[i, c] = value
            if p == 'Architecture (PG)':
                for c in range(0, len(column_names)):
                    i = index_values.index('Architecture (PG)')
                    cost = float(cost_A_PG)
                    value = cost/w_df.iloc[i, c]
                    w_df.iloc[i, c] = value
            if p == 'Architecture (UG)':
                for c in range(0, len(column_names)):
                    i = index_values.index('Architecture (UG)')
                    cost = float(cost_A_UG)
                    value = cost/w_df.iloc[i, c]
                    w_df.iloc[i, c] = value
            if p == 'Business (PG)':
                for c in range(0, len(column_names)):
                    i = index_values.index('Business (PG)')
                    cost = float(cost_B_PG)
                    value = cost/w_df.iloc[i, c]
                    w_df.iloc[i, c] = value
            if p == 'Business (UG)':
                for c in range(0, len(column_names)):
                    i = index_values.index('Business (UG)')
                    cost = float(cost_B_UG)
                    value = cost/w_df.iloc[i, c]
                    w_df.iloc[i, c] = value
            if p == 'Engineering (PG)':
                for c in range(0, len(column_names)):
                    i = index_values.index('Engineering (PG)')
                    cost = float(cost_E_PG)
                    value = cost/w_df.iloc[i, c]
                    w_df.iloc[i, c] = value
            if p == 'Engineering (UG)':
                for c in range(0, len(column_names)):
                    i = index_values.index('Engineering (UG)')
                    cost = float(cost_E_UG)
                    value = cost/w_df.iloc[i, c]
                    w_df.iloc[i, c] = value
            if p == 'FMHS (PG)':
                for c in range(0, len(column_names)):
                    i = index_values.index('FMHS (PG)')
                    cost = float(cost_FMHS_PG)
                    value = cost/w_df.iloc[i, c]
                    w_df.iloc[i, c] = value
            if p == 'FMHS (UG)':
                for c in range(0, len(column_names)):
                    i = index_values.index('FMHS (UG)')
                    cost = float(cost_FMHS_UG)
                    value = cost/w_df.iloc[i, c]
                    w_df.iloc[i, c] = value
            if p == 'FMHS (UG) - Nursing':
                for c in range(0, len(column_names)):
                    i = index_values.index('FMHS (UG) - Nursing')
                    cost = float(cost_FMHS_UG_N)
                    value = cost/w_df.iloc[i, c]
                    w_df.iloc[i, c] = value
            if p == 'FOSSLA (PG)':
                for c in range(0, len(column_names)):
                    i = index_values.index('FOSSLA (PG)')
                    cost = float(cost_FOSSLA_PG)
                    value = cost/w_df.iloc[i, c]
                    w_df.iloc[i, c] = value
            if p == 'FOSSLA (UG)':
                for c in range(0, len(column_names)):
                    i = index_values.index('FOSSLA (UG)')
                    cost = float(cost_FOSSLA_UG)
                    value = cost/w_df.iloc[i, c]
                    w_df.iloc[i, c] = value
            if p == 'Foundation in Arts':
                for c in range(0, len(column_names)):
                    i = index_values.index('Foundation in Arts')
                    cost = float(cost_F_art)
                    value = cost/w_df.iloc[i, c]
                    w_df.iloc[i, c] = value
            if p == 'Foundation in Science':
                for c in range(0, len(column_names)):
                    i = index_values.index('Foundation in Science')
                    cost = float(cost_F_sci)
                    value = cost/w_df.iloc[i, c]
                    w_df.iloc[i, c] = value
            if p == 'FPS (PG)':
                for c in range(0, len(column_names)):
                    i = index_values.index('FPS (PG)')
                    cost = float(cost_FPS_PG)
                    value = cost/w_df.iloc[i, c]
                    w_df.iloc[i, c] = value
            if p == 'FPS (UG)':
                for c in range(0, len(column_names)):
                    i = index_values.index('FPS (UG)')
                    cost = float(cost_FPS_UG)
                    value = cost/w_df.iloc[i, c]
                    w_df.iloc[i, c] = value
            if p == 'GBS (PG)':
                for c in range(0, len(column_names)):
                    i = index_values.index('GBS (PG)')
                    cost = float(cost_GBS_PG)
                    value = cost/w_df.iloc[i, c]
                    w_df.iloc[i, c] = value
            if p == 'Hospitality (PG)':
                for c in range(0, len(column_names)):
                    i = index_values.index('Hospitality (PG)')
                    cost = float(cost_H_PG)
                    value = cost/w_df.iloc[i, c]
                    w_df.iloc[i, c] = value
            if p == 'Hospitality (UG)':
                for c in range(0, len(column_names)):
                    i = index_values.index('Hospitality (UG)')
                    cost = float(cost_H_UG)
                    value = cost/w_df.iloc[i, c]
                    w_df.iloc[i, c] = value
            if p == 'IASDA (PG)':
                for c in range(0, len(column_names)):
                    i = index_values.index('IASDA (PG)')
                    cost = float(cost_IASDA_PG)
                    value = cost/w_df.iloc[i, c]
                    w_df.iloc[i, c] = value
            if p == 'IASDA (UG)':
                for c in range(0, len(column_names)):
                    i = index_values.index('IASDA (UG)')
                    cost = float(cost_IASDA_UG)
                    value = cost/w_df.iloc[i, c]
                    w_df.iloc[i, c] = value
            if p == 'ICAD (PG)':
                for c in range(0, len(column_names)):
                    i = index_values.index('ICAD (PG)')
                    cost = float(cost_ICAD_PG)
                    value = cost/w_df.iloc[i, c]
                    w_df.iloc[i, c] = value
            if p == 'ICAD (UG)':
                for c in range(0, len(column_names)):
                    i = index_values.index('ICAD (UG)')
                    cost = float(cost_ICAD_UG)
                    value = cost/w_df.iloc[i, c]
                    w_df.iloc[i, c] = value
            if p == 'IMUS (PG)':
                for c in range(0, len(column_names)):
                    i = index_values.index('IMUS (PG)')
                    cost = float(cost_IMUS_PG)
                    value = cost/w_df.iloc[i, c]
                    w_df.iloc[i, c] = value
            if p == 'IMUS (UG)':
                for c in range(0, len(column_names)):
                    i = index_values.index('IMUS (UG)')
                    cost = float(cost_IMUS_UG)
                    value = cost/w_df.iloc[i, c]
                    w_df.iloc[i, c] = value
            if p == 'IT (PG)':
                for c in range(0, len(column_names)):
                    i = index_values.index('IT (PG)')
                    cost = float(cost_IT_PG)
                    value = cost/w_df.iloc[i, c]
                    w_df.iloc[i, c] = value
            if p == 'IT (UG)':
                for c in range(0, len(column_names)):
                    i = index_values.index('IT (UG)')
                    cost = float(cost_IT_UG)
                    value = cost/w_df.iloc[i, c]
                    w_df.iloc[i, c] = value
            if p == 'Master & PhD Programme':
                for c in range(0, len(column_names)):
                    i = index_values.index('Master & PhD Programme')
                    cost = float(cost_MPhD)
                    value = cost/w_df.iloc[i, c]
                    w_df.iloc[i, c] = value
            if p == 'SEC-General Scholarship':
                for c in range(0, len(column_names)):
                    i = index_values.index('SEC-General Scholarship')
                    cost = float(cost_SEC_GS)
                    value = cost/w_df.iloc[i, c]
                    w_df.iloc[i, c] = value
            if p == 'SEC-Foundation':
                for c in range(0, len(column_names)):
                    i = index_values.index('SEC-Foundation')
                    cost = float(cost_SEC_F)
                    value = cost/w_df.iloc[i, c]
                    w_df.iloc[i, c] = value
            if p == 'SEC-Diploma & Foundation':
                for c in range(0, len(column_names)):
                    i = index_values.index('SEC-Diploma & Foundation')
                    cost = float(cost_SEC_DF)
                    value = cost/w_df.iloc[i, c]
                    w_df.iloc[i, c] = value
            if p == 'SEC-MARA Scholarship':
                for c in range(0, len(column_names)):
                    i = index_values.index('SEC-MARA Scholarship')
                    cost = float(cost_SEC_MS)
                    value = cost/w_df.iloc[i, c]
                    w_df.iloc[i, c] = value
            if p == 'SEC-Open Day/Enrolment Day/Info Day':
                for c in range(0, len(column_names)):
                    i = index_values.index('SEC-Open Day/Enrolment Day/Info Day')
                    cost = float(cost_SEC_OEI)
                    value = cost/w_df.iloc[i, c]
                    w_df.iloc[i, c] = value
            if p == 'SEC-UEC':
                for c in range(0, len(column_names)):
                    i = index_values.index('SEC-UEC')
                    cost = float(cost_SEC_UEC)
                    value = cost/w_df.iloc[i, c]
                    w_df.iloc[i, c] = value

        st.write(f'{f_month}/{f_year}_{t_month}/{t_year}')
        if st.session_state.w_cpl_df in st.session_state:
            st.session_state.t_cpl_df = True
        d_df = concat_d_df(programs, f_year, f_month, t_year, t_month)
        numeric_cols = d_df.select_dtypes(include=['number']).columns # 열 선택
        d_df['Total_Leads'] = d_df[numeric_cols].sum(axis=1)
        # st.write(d_df)
        #cost
        cost_dic = {}
        for p in index_values:
            if p == 'Actuarial Science (PG)':
                i = index_values.index('Actuarial Science (PG)')
                cost = float(cost_AcS_PG)
                cost_dic[p]=cost
            if p == 'Actuarial Science (UG)':
                    i = index_values.index('Actuarial Science (UG)')
                    cost = float(cost_AcS_UG)
                    cost_dic[p]=cost
            if p == 'Applied Sciences (PG)':
                    i = index_values.index('Applied Sciences (PG)')
                    cost = float(cost_ApS_PG)
                    cost_dic[p]=cost
            if p == 'Applied Sciences (UG)':
                    i = index_values.index('Applied Sciences (UG)')
                    cost = float(cost_ApS_UG)
                    cost_dic[p]=cost
            if p == 'Architecture (PG)':
                    i = index_values.index('Architecture (PG)')
                    cost = float(cost_A_PG)
                    cost_dic[p]=cost
            if p == 'Architecture (UG)':
                    i = index_values.index('Architecture (UG)')
                    cost = float(cost_A_UG)
                    cost_dic[p]=cost
            if p == 'Business (PG)':
                    cost_dic[p]=cost
                    i = index_values.index('Business (PG)')
                    cost = float(cost_B_PG)
                    cost_dic[p]=cost
            if p == 'Business (UG)':
                    i = index_values.index('Business (UG)')
                    cost = float(cost_B_UG)
                    cost_dic[p]=cost
            if p == 'Engineering (PG)':
                    i = index_values.index('Engineering (PG)')
                    cost = float(cost_E_PG)
                    cost_dic[p]=cost
            if p == 'Engineering (UG)':
                    i = index_values.index('Engineering (UG)')
                    cost = float(cost_E_UG)
                    cost_dic[p]=cost
            if p == 'FMHS (PG)':
                    i = index_values.index('FMHS (PG)')
                    cost = float(cost_FMHS_PG)
                    cost_dic[p]=cost
            if p == 'FMHS (UG)':
                    i = index_values.index('FMHS (UG)')
                    cost = float(cost_FMHS_UG)
                    cost_dic[p]=cost
            if p == 'FMHS (UG) - Nursing':
                    i = index_values.index('FMHS (UG) - Nursing')
                    cost = float(cost_FMHS_UG_N)
                    cost_dic[p]=cost
            if p == 'FOSSLA (PG)':
                    i = index_values.index('FOSSLA (PG)')
                    cost = float(cost_FOSSLA_PG)
                    cost_dic[p]=cost
            if p == 'FOSSLA (UG)':
                    i = index_values.index('FOSSLA (UG)')
                    cost = float(cost_FOSSLA_UG)
                    cost_dic[p]=cost
            if p == 'Foundation in Arts':
                    i = index_values.index('Foundation in Arts')
                    cost = float(cost_F_art)
                    cost_dic[p]=cost
            if p == 'Foundation in Science':
                    i = index_values.index('Foundation in Science')
                    cost = float(cost_F_sci)
                    cost_dic[p]=cost
            if p == 'FPS (PG)':
                    i = index_values.index('FPS (PG)')
                    cost = float(cost_FPS_PG)
                    cost_dic[p]=cost
            if p == 'FPS (UG)':
                    i = index_values.index('FPS (UG)')
                    cost = float(cost_FPS_UG)
                    cost_dic[p]=cost
            if p == 'GBS (PG)':
                    i = index_values.index('GBS (PG)')
                    cost = float(cost_GBS_PG)
                    cost_dic[p]=cost
            if p == 'Hospitality (PG)':
                    i = index_values.index('Hospitality (PG)')
                    cost = float(cost_H_PG)
                    cost_dic[p]=cost
            if p == 'Hospitality (UG)':
                    i = index_values.index('Hospitality (UG)')
                    cost = float(cost_H_UG)
                    cost_dic[p]=cost
            if p == 'IASDA (PG)':
                    i = index_values.index('IASDA (PG)')
                    cost = float(cost_IASDA_PG)
                    cost_dic[p]=cost
            if p == 'IASDA (UG)':
                    i = index_values.index('IASDA (UG)')
                    cost = float(cost_IASDA_UG)
                    cost_dic[p]=cost
            if p == 'ICAD (PG)':
                    i = index_values.index('ICAD (PG)')
                    cost = float(cost_ICAD_PG)
                    cost_dic[p]=cost
            if p == 'ICAD (UG)':
                    i = index_values.index('ICAD (UG)')
                    cost = float(cost_ICAD_UG)
                    cost_dic[p]=cost
            if p == 'IMUS (PG)':
                    i = index_values.index('IMUS (PG)')
                    cost = float(cost_IMUS_PG)
                    cost_dic[p]=cost
            if p == 'IMUS (UG)':
                    i = index_values.index('IMUS (UG)')
                    cost = float(cost_IMUS_UG)
                    cost_dic[p]=cost
            if p == 'IT (PG)':
                    i = index_values.index('IT (PG)')
                    cost = float(cost_IT_PG)
                    cost_dic[p]=cost
            if p == 'IT (UG)':
                    i = index_values.index('IT (UG)')
                    cost = float(cost_IT_UG)
                    cost_dic[p]=cost
            if p == 'Master & PhD Programme':
                    i = index_values.index('Master & PhD Programme')
                    cost = float(cost_MPhD)
                    cost_dic[p]=cost
            if p == 'SEC-General Scholarship':
                    i = index_values.index('SEC-General Scholarship')
                    cost = float(cost_SEC_GS)
                    cost_dic[p]=cost
            if p == 'SEC-Foundation':
                    i = index_values.index('SEC-Foundation')
                    cost = float(cost_SEC_F)
                    cost_dic[p]=cost
            if p == 'SEC-Diploma & Foundation':
                    i = index_values.index('SEC-Diploma & Foundation')
                    cost = float(cost_SEC_DF)
                    cost_dic[p]=cost
            if p == 'SEC-MARA Scholarship':
                    i = index_values.index('SEC-MARA Scholarship')
                    cost = float(cost_SEC_MS)
                    cost_dic[p]=cost
            if p == 'SEC-Open Day/Enrolment Day/Info Day':
                    i = index_values.index('SEC-Open Day/Enrolment Day/Info Day')
                    cost = float(cost_SEC_OEI)
                    cost_dic[p]=cost
            if p == 'SEC-UEC':
                    i = index_values.index('SEC-UEC')
                    cost = float(cost_SEC_UEC)
                    cost_dic[p]=cost
        d_df['Cost'] = d_df.index.map(cost_dic)

        #(Total) CPL
        d_df['CPL'] = d_df['Cost'] / d_df['Total_Leads']
        t_df = pd.DataFrame()
        t_df = d_df[['Cost','Total_Leads','CPL']]
        st.session_state.w_cpl_df = w_df
        st.session_state.t_cpl_df = t_df

    if st.session_state.w_cpl_df is not False:
        st.write(st.session_state.w_cpl_df)
        st.write(st.session_state.t_cpl_df)

if __name__ == "__main__":
    # os.system('python -m streamlit run ALD_eex.py')
    # os.environ["PATH"] += os.pathsep + os.path.dirname(os.path.abspath(__file__))
    main()


