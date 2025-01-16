import mysql.connector
import os

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="admin123",
    database="animake_db"
)

def create_audio():
    cursor=mydb.cursor()
    query = "CREATE TABLE audio_files (id INT AUTO_INCREMENT PRIMARY KEY, filename VARCHAR(255), audio_data LONGBLOB)"

    cursor.execute(query)
    mydb.commit()

    cursor.close()

def upload_audios() :
    folder_path = './preloaded_audio/audios'
    cursor=mydb.cursor()
    
    for filename in os.listdir(folder_path):
        if filename.endswith('.mp3') or filename.endswith('.wav'):
            ldir = folder_path + '/' + filename
            with open(ldir, 'rb') as file:
                audio_data = file.read()

                # Insert audio data into database
                sql = "INSERT INTO audio_files (filename, audio_data) VALUES (%s, %s)"
                values = (filename, audio_data)
                cursor.execute(sql, values)
            mydb.commit()

    cursor.close()

create_audio()
upload_audios()