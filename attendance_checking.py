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

def summary():
    files = glob.glob('data/*.csv')
    if not files:
        st.write('Data files not found')
        return
    if os.path.exists("summary.xlsx"):
        os.remove("summary.xlsx")

    writer = pd.ExcelWriter('summary.xlsx')
    summary = {}
    for f in files:
        df = pd.read_csv(f)
        preprocess(df)

        time = df.iloc[0]['Join Time'][:10]
        sr = df.groupby(['Name (Original Name)'])['Duration (Minutes)'].sum()
        for s in sr.index:
            minutes = sr.loc[s]
            s = s.split('-')
            if len(s) < 3:
                continue
            for i in range(len(s)):
                s[i] = s[i].strip()
            if not s[1].isdigit():
                continue
            if not s[0][0:2].isdigit():
                continue

            check = 'x' if minutes < 60 else ''
            info = summary.get(s[0])
            if info is None:
                summary[s[0]] = [[s[2], time, str(minutes), check]]
            else:
                info.append([s[2], time, str(minutes), check])

    for cl,lst in summary.items():
        df = pd.DataFrame(lst, columns=['Name', 'Date', 'Duration (Minutes)', 'Check'])
        df.to_excel(writer, sheet_name=cl)

    writer.save()

    with open("summary.xlsx", "rb") as file:
        st.download_button(label="Download", data=file, file_name="summary.xlsx", mime="data/xlsx")

def preprocess(df):
    for i in df.index:
        name = df['Name (Original Name)'][i].replace('_', '-').replace(' -', '-').replace('- ','-').replace('CP-SN', 'CPSN').replace('CTr', 'CTR').replace('CTR-N', 'CTRN').replace('CSu', 'CSU').replace('CSU-Đ', 'CSUĐ').replace('CSi', 'CSI').replace('CTin', 'CTIN').replace('Cl1', 'CL1').replace('CL-', 'CL2-').replace('10d2', '10D2').replace('10CT-', '10CT2-').replace('19SN', '10SN').replace('10CA-', '10CA1-')
        if name.find('(') > 0:
            name = name[:name.find('(')-1]
        df['Name (Original Name)'][i] = name

def drop_invalid_rows(df):
    new_df = pd.DataFrame([], columns=['class', 'name', 'date', 'join time'])
    for i in df.index:
        name = df['Name (Original Name)'][i]
        s = name.split('-')
        if len(s) != 3:
            continue
        for i in range(len(s)):
            s[i] = s[i].strip()
        if not s[1].isdigit():
            continue
        if not s[0][0:2].isdigit():
            continue
        date = df['Join Time'][i][:10]
        time = df['Join Time'][i][10]
        row = {'class':s[0], 'name':s[2], 'date':date, 'join time': time}
        new_df = new_df.append(row, ignore_index=True)

    print(new_df)

def summary2():
    files = glob.glob('data/*.csv')
    if not files:
        st.write('Data files not found')
        return
    # if os.path.exists("summary.xlsx"):
    #     os.remove("summary.xlsx")

    # writer = pd.ExcelWriter('summary.xlsx')
    # summary = {}
    for f in files:
        df = pd.read_csv(f)
        preprocess(df)
        drop_invalid_rows(df)
        
    # writer.save()
    # with open("summary.xlsx", "rb") as file:
    #     st.download_button(label="Download", data=file, file_name="summary.xlsx", mime="data/xlsx")

def main():
    classes = st.sidebar.text_input('Class', '')
    id = st.sidebar.text_input('Student ID', '')
    name = st.sidebar.text_input('Student Name', '')

    if st.sidebar.button('Search'):
        search(unidecode.unidecode(classes.strip()), id.strip(), unidecode.unidecode(name.strip()))

    if st.sidebar.button('Export'):
        export()

    uploaded_files = st.sidebar.file_uploader("Choose CSV files", accept_multiple_files=True, type='csv')
    if len(uploaded_files) > 0:
        if classes == 'cotai1109':
            for file in uploaded_files:
                with open(os.path.join("data", file.name), "wb") as f:
                    f.write(file.getbuffer())
            st.write('Data files uploaded')

if __name__ == "__main__":
    main()