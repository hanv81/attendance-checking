import streamlit as st
import pandas as pd
import glob

def verify(classes, id, name):
    if classes == None or len(classes) == 0:
        st.write('Please input Class')
        return False
    elif id == None or len(id) == 0:
        st.write('Please input Student ID')
        return False
    elif name == None or len(name) < 2:
        st.write('Please input Student Name')
        return False
    return True

def search(classes, id, name):
    if verify(classes, id, name):
        files = glob.glob('data/*.csv')
        if not files:
            st.write('Data files not found')
            return

        st.write('Result')
        summary = {}
        i = 0
        for f in files:
            df = pd.read_csv(f)
            pat = "^" + classes + ".?-.?" + id + ".?-.?" + ".*" + name
            rs = df.loc[df['Tên (Tên gốc)'].str.match(pat, case=False)]
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
    with open("export.xlsx", "rb") as file:
        st.download_button(label="Download", data=file, file_name="export.xlsx", mime="data/xlsx")
    files = glob.glob('data/*.csv')
    writer = pd.ExcelWriter('export.xlsx')
    for f in files:
        df = pd.read_csv(f)
        time = df.iloc[0]['Thời gian vào'][:10]
        sr = df.groupby(['Tên (Tên gốc)'])['Thời gian (Phút)'].sum()
        st.write(time, sr)
        sr.to_excel(writer, sheet_name=time.replace("/","-"))
    writer.save()

def main():
    classes = st.sidebar.text_input('Class', '')
    id = st.sidebar.text_input('Student ID', '')
    name = st.sidebar.text_input('Student Name', '')

    if st.sidebar.button('Search'):
        search(classes.strip(), id.strip(), name.strip())

    if st.sidebar.button('Export'):
        export()

if __name__ == "__main__":
    main()