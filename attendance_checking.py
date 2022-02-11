import streamlit as st
import pandas as pd

classes = inp_class = st.sidebar.text_input('Class', '10CL1')
id = inp_id = st.sidebar.text_input('Student ID', '33')
name = inp_name = st.sidebar.text_input('Student Name', 'Trâm')

if st.sidebar.button('Search'):
    if classes == None or len(classes) == 0:
        st.write('Please input Class')
    elif id == None or len(id) == 0:
        st.write('Please input Student ID')
    elif name == None or len(name) == 0:
        st.write('Please input Student Name')
    else:
        df = pd.read_csv('data/08022022.csv')
        rs = df.loc[df['Tên (Tên gốc)'].str.startswith(classes + '-' + id)]
        rs.drop(columns='Email người dùng', inplace=True)
        st.write(rs)
        st.write('Summary')
        total_time = rs['Thời gian (Phút)'].sum()
        time = rs.iloc[0]['Thời gian vào'][:10]
        st.write(time, total_time, 'minutes')