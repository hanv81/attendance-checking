import streamlit as st
import pandas as pd
import glob

def search(classes, id, name):
    if classes == None or len(classes) == 0:
        st.write('Please input Class')
    elif id == None or len(id) == 0:
        st.write('Please input Student ID')
    elif name == None or len(name) == 0:
        st.write('Please input Student Name')
    else:
        st.write('Result')
        files = glob.glob('data/*.csv')
        summary = {}
        i = 0
        for f in files:
            df = pd.read_csv(f)
            rs = df.loc[df['Tên (Tên gốc)'].str.startswith(classes + '-' + id)]
            if not rs.empty:
                rs.drop(columns='Email người dùng', inplace=True)
                st.write(rs)
                total_time = rs['Thời gian (Phút)'].sum()
                time = rs.iloc[0]['Thời gian vào'][:10]
                summary[i] = [time, total_time]
                i += 1

        if summary:
            st.write('Summary')
            df_summary = pd.DataFrame.from_dict(summary, orient='index', columns=['Date', 'Time'])
            st.write(df_summary)

def export():
    files = glob.glob('data/*.csv')
    ls_df = []
    for f in files:
        df = pd.read_csv(f)
        df = df.groupby(['Tên (Tên gốc)'])['Thời gian (Phút)'].sum()
        st.write(df)
        ls_df.append(df)
    df = pd.concat(ls_df)
    df.to_csv('export.csv')

def main():
    classes = st.sidebar.text_input('Class', '10CL1')
    id = st.sidebar.text_input('Student ID', '33')
    name = st.sidebar.text_input('Student Name', 'Trâm')

    if st.sidebar.button('Search'):
        search(classes, id, name)

    if st.sidebar.button('Export'):
        export()

if __name__ == "__main__":
    main()