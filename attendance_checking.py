import streamlit as st
import pandas as pd
import glob
import os
import unidecode

def verify(classes, name):
    if classes == None or len(classes) == 0:
        st.write('Please input Class')
        return False
    elif name == None or len(name) == 0:
        st.write('Please input Student Name')
        return False
    return True

def search(classes, id, name):
    if verify(classes, name):
        files = glob.glob('data/*.csv')
        if not files:
            st.write('Data files not found')
            return

        st.write('Result')
        summary = {}
        i = 0
        for f in files:
            try:
                df = pd.read_csv(f)
                df_copy = df.copy()
                for i in df.index:
                    df.loc[i,'Name (Original Name)'] = unidecode.unidecode(df.loc[i,'Name (Original Name)'])
                if len(id) > 0:
                    pat = "^" + classes + ".?-.?" + id + ".?-.?" + ".*" + name
                else:
                    pat = "^" + classes + ".*" + name
                rs = df.loc[df['Name (Original Name)'].str.match(pat, case=False)]

                if not rs.empty:
                    rs = df_copy.loc[rs.index].drop(columns=['User Email', 'Guest', 'Recording Consent'])
                    st.write(rs)
                    total_time = rs['Duration (Minutes)'].sum()
                    time = rs.iloc[0]['Join Time'][:10]
                    summary[i] = [time, total_time]
                    i += 1
            except:
                print('Error')

        if summary:
            st.write('Summary')
            df_summary = pd.DataFrame.from_dict(summary, orient='index', columns=['Date', 'Duration (Minutes)'])
            st.write(df_summary)

def export():
    files = glob.glob('data/*.csv')
    if not files:
        st.write('Data files not found')
        return
    if os.path.exists("export.xlsx"):
        os.remove("export.xlsx")

    writer = pd.ExcelWriter('export.xlsx')
    report = []
    for f in files:
        df = pd.read_csv(f)
        time = df.iloc[0]['Join Time'][:10]
        sr = df.groupby(['Name (Original Name)'])['Duration (Minutes)'].sum()
        sr.to_excel(writer, sheet_name=time.replace("/","-"))
        report += [(time, sr)]
    writer.save()

    with open("export.xlsx", "rb") as file:
        st.download_button(label="Download", data=file, file_name="export.xlsx", mime="data/xlsx")
    for time, sr in report:
        st.write(time, sr)

def main():
    classes = st.sidebar.text_input('Class', '')
    id = st.sidebar.text_input('Student ID', '')
    name = st.sidebar.text_input('Student Name', '')

    if st.sidebar.button('Search'):
        search(unidecode.unidecode(classes.strip()), id.strip(), unidecode.unidecode(name.strip()))

    if st.sidebar.button('Export'):
        export()

if __name__ == "__main__":
    main()