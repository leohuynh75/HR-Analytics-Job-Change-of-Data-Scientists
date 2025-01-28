import os
import pandas as pd
import requests
from sqlalchemy import create_engine
import pymysql

# EXTRACT
# Load data from the google sheets
gg_sheet_id_1 = '1VCkHwBjJGRJ21asd9pxW4_0z2PWuKhbLR3gUHm-p4GI'
url_1 = 'https://docs.google.com/spreadsheets/d/' + gg_sheet_id_1 + '/export?format=xlsx'
df = pd.read_excel(url_1, sheet_name='enrollies')

# Download and open the excel file
excel_url = 'https://assets.swisscoding.edu.vn/company_course/enrollies_education.xlsx'
if not os.path.exists('enrollies_education.xlsx'):
  excel_response = requests.get(excel_url.strip())
  with open('enrollies_education.xlsx', 'wb') as file:
    file.write(excel_response.content)
enrollies_education = pd.read_excel('enrollies_education.xlsx')

# Download and open the csv file
csv_url = 'https://assets.swisscoding.edu.vn/company_course/work_experience.csv'
if not os.path.exists('work_experience,csv'):
  csv_response = requests.get(csv_url)
  with open('work_experience.csv', 'wb') as file:
    file.write(csv_response.content)
work_experience = pd.read_csv('work_experience.csv')

# Load data from database
engine = create_engine('mysql+pymysql://etl_practice:550814@112.213.86.31:3360/company_course')
training_hours = pd.read_sql_table('training_hours', con=engine)

engine_1 = create_engine('mysql+pymysql://etl_practice:550814@112.213.86.31:3360/company_course')
employment = pd.read_sql_table('employment', con=engine_1)

# Load data from website
table = pd.read_html('https://sca-programming-school.github.io/city_development_index/index.html')
city = table[0]

# TRANSFORM
# Write function to clean and transform data
def handling_missing_value(df):
  for col in df.columns:
    if df[col].isna().sum() > 0:
      if pd.api.types.is_numeric_dtype(df[col]):
        df[col].fillna(df[col].median(), inplace=True)
      elif pd.api.types.is_object_dtype(df[col]) or pd.api.types.is_categorical_dtype(df[col]):
        df[col].fillna('Unknown', inplace=True)
        df[col] = df[col].str.lower()
  return df

data_tables = {
  'enrollies': df,
  'enrollies_edu': enrollies_education,
  'work_exp': work_experience,
  'training_hours': training_hours,
  'employment': employment,
  'city': city
}

for table_name, data_frame in data_tables.items():
  data_tables[table_name] = handling_missing_value(data_frame)

#LOAD DATA
# Path to the SQLite database
db_path = r'C:\Users\LoanVo\Documents\DBeaver\data_warehouse.db'
# Create an SQL Alchemy engine
engine_2 = create_engine(f'sqlite:///{db_path}')

df.to_sql('Dim_enrollies', con=engine_2, if_exists='replace', index=False)
enrollies_education.to_sql('Dim_education', con=engine_2, if_exists='replace', index=False)
work_experience.to_sql('Dim_experience', con=engine_2, if_exists='replace', index=False)
training_hours.to_sql('Dim_training', con=engine_2, if_exists='replace', index=False)
city.to_sql('Dim_city', con=engine_2, if_exists='replace', index=False)
employment.to_sql('Fact_employment', con=engine_2, if_exists='replace', index=False)
