FROM python:3

WORKDIR /att

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 8501
COPY . .

CMD [ "streamlit", "run", "./attendance_checking.py" ]