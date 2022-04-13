import streamlit as st
import pandas as pd
import glob
import os
import unidecode
import time
from datetime import datetime

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
        summary = []
        for f in files:
            try:
                df = pd.read_csv(f)
                df_copy = df.copy()
                for j in df.index:
                    df.loc[j,'Name (Original Name)'] = unidecode.unidecode(df.loc[j,'Name (Original Name)'])
                if len(id) > 0:
                    pat = "^" + classes + ".?-.?" + id + ".?-.?" + ".*" + name
                else:
                    pat = "^" + classes + ".*" + name
                rs = df.loc[df['Name (Original Name)'].str.match(pat, case=False)]

                if not rs.empty:
                    rs = df_copy.loc[rs.index].drop(columns=['User Email', 'Guest', 'Recording Consent'])
                    st.write(rs)
                    duration = rs['Duration (Minutes)'].sum()
                    join_time = rs['Join Time'].min()[11:]
                    date = rs.iloc[0]['Join Time'][:10]
                    summary += [[date, join_time, duration]]
            except:
                print('Error')

        if summary:
            st.write('Summary')
            st.write(pd.DataFrame(summary, columns=['Date', 'Join Time', 'Duration (Minutes)']))

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

def preprocess(df):
    for i in df.index:
        name = df['Name (Original Name)'][i]
        # name = name.replace('_', '-').replace('CP-SN', 'CPSN').replace('CTr', 'CTR').replace('CTR-N', 'CTRN').replace('CSu', 'CSU').replace('CSU-Đ', 'CSUĐ').replace('CSi', 'CSI').replace('CTin', 'CTIN').replace('Cl1', 'CL1').replace('CL-', 'CL2-').replace('10d2', '10D2').replace('10CT-', '10CT2-').replace('19SN', '10SN').replace('10CA-', '10CA1-').replace('10VA3', '10CA3')
        if name.find('(') > 0:
            name = name[:name.find('(')-1]
        df.loc[i,'Name (Original Name)'] = name

def create_data(df, data):
    date = df['Join Time'][0][:10]
    for i in df.index:
        name = df['Name (Original Name)'][i]
        s = name.split('-')
        if len(s) != 3:
            continue
        for j in range(len(s)):
            s[j] = s[j].strip()
        if not s[1].isdigit():
            continue
        if not s[0][0:2].isdigit():
            continue

        t = df['Join Time'][i][11:]
        duration = df['Duration (Minutes)'][i]
        data.append([s[0], s[2], date, t, duration])

def summary():
    curmilis = int(round(time.time() * 1000))
    files = glob.glob('data/*.csv')
    if not files:
        st.write('Data files not found')
        return
    if os.path.exists("summary.xlsx"):
        os.remove("summary.xlsx")

    print('creating data ...')
    writer = pd.ExcelWriter('summary.xlsx')
    data = []
    for f in files:
        df = pd.read_csv(f)
        preprocess(df)
        create_data(df, data)

    print('processing data ...')
    date1 = ['2022/02/08', '2022/02/15', '2022/02/22', '2022/03/01', '2022/03/08', '2022/03/15', '2022/03/22', '2022/03/29', '2022/04/05', '2022/04/12', '2022/04/19', '2022/04/26']
    date2 = ['2022/02/11', '2022/02/18', '2022/02/25', '2022/03/04', '2022/03/11', '2022/03/18', '2022/03/25', '2022/04/01', '2022/04/08', '2022/04/15', '2022/04/22', '2022/04/29']
    df = pd.DataFrame(data, columns=['class', 'name', 'date', 'time', 'duration'])
    sr = df.groupby(['class', 'name'])['date'].nunique()
    summary = {}
    for (cls, name), count in sr.items():
        if summary.get(cls) is None:
            summary[cls] = [[name, 12-count, 0, 0, '', []]]
        else:
            summary[cls].append([name, 12-count, 0, 0, '', []])

    sr = df.groupby(['class', 'name', 'date']).agg({'duration':'sum', 'time': 'min'})
    fmt = '%H:%M:%S'
    t0 = datetime.strptime('13:05:59', fmt)
    for i in sr.index:
        cls, name, date = i
        duration = sr.loc[i]['duration']
        t = sr.loc[i]['time']
        cls = summary[cls]
        for std in cls:
            if std[0] == name:
                t = datetime.strptime(t, fmt)
                dt = (t-t0).seconds // 60
                if t > t0 and dt > 0:
                    std[2] += 1
                    std[4] += '| ' + date + ' : ' + str(dt) + '\' late '
                if duration < 60:
                    std[3] += 1
                    std[4] += '| ' + date + ' : ' + str(duration) + '\' duration '
                if not std[5]:
                    if date in date1:
                        std[5].extend(date1)
                    else:
                        std[5].extend(date2)
                if date in std[5]:
                    std[5].remove(date)
                break

    for cls,lst in summary.items():
        for std in lst:
            for date in std[5]:
                std[4] += '| ' + date + ' : ' + ' absent'
            std.pop()
        pd.DataFrame(lst, columns=['Name', 'Absent', 'Late', 'Short Duration', 'Detail']).to_excel(writer, sheet_name=cls)

    writer.save()
    with open("summary.xlsx", "rb") as file:
        st.download_button(label="Download", data=file, file_name="summary.xlsx", mime="data/xlsx")

    curmilis = int(round(time.time() * 1000)) - curmilis
    print('Done. Total time:', curmilis)

def main():
    classes = st.sidebar.text_input('Class', '')
    id = st.sidebar.text_input('Student ID', '')
    name = st.sidebar.text_input('Student Name', '')

    if st.sidebar.button('Search'):
        search(unidecode.unidecode(classes.strip()), id.strip(), unidecode.unidecode(name.strip()))

    if st.sidebar.button('Export'):
        export()

    # if st.sidebar.button('Summary'):
    #     summary()

    uploaded_files = st.sidebar.file_uploader("Choose CSV files", accept_multiple_files=True, type='csv')
    if len(uploaded_files) > 0:
        if classes == 'cotai1109':
            for file in uploaded_files:
                with open(os.path.join("data", file.name), "wb") as f:
                    f.write(file.getbuffer())
            st.write('Data files uploaded')

if __name__ == "__main__":
    main()