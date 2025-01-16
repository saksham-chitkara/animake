from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import base64
from flask_bcrypt import Bcrypt
import os
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, decode_token
from datetime import timedelta, datetime
import numpy as np
from flask import send_file
import base64
from moviepy.editor import AudioFileClip, concatenate_audioclips
import base64

import psycopg2
import random

app = Flask(
    __name__,
    template_folder='./templates',
    static_folder='./static'
)

app.secret_key = os.urandom(24)
app.permanent_session_lifetime = timedelta(hours=1)

bcrypt = Bcrypt(app)

def connect_to_database():
    ssl_root_cert_path = "./root.crt"
    conn_string = (
        f"postgresql://swam:kt6kEyaRvJoFCzJXRiKp1w"
        f"@swam-singla-4058.7s5.aws-ap-south-1.cockroachlabs.cloud:26257/animake_db"
        f"?sslmode=verify-full&sslrootcert={ssl_root_cert_path}"
    )

    # Connect to the database
    return psycopg2.connect(conn_string)
conn = connect_to_database()

# JWT configurations
app.config['JWT_SECRET_KEY'] = os.urandom(24)
jwt = JWTManager(app)

users = {}

@app.route("/", methods=["GET"])
def homepage():
    acc_token = request.args.get('access_token')
    if acc_token :
        try:
            current_user = decode_token(acc_token)['sub']
            return render_template("/homepage/home.html", user_name = current_user, acc_token = acc_token)
        except Exception as e:
            print(e)
            return redirect(url_for('login'))
    else :
        if 'username' in session:
            user = session['username']
            return render_template("/homepage/home.html", acc_token = session['jwt_token'], user_name = user) 
        else : 
            return render_template("/homepage/home.html", acc_token = "", user_name = "")

def delete_user_folder(username):
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM past_projects WHERE username = %s", (username))
        conn.commit()
        
        cursor.close()
    except Exception as e:
        return jsonify({'error': 'An error occurred while storing the image'}), 500

def change_folder_name(old_username, new_username):
    try:
        cursor = conn.cursor()
        cursor.execute("UPDATE past_projects SET username = %s WHERE username = %s",(new_username, old_username))
        conn.commit()
        cursor.close()
    except Exception as e:
        return jsonify({'error': 'An error occurred while storing the image'}), 500

from io import BytesIO
import imageio

@app.route("/save_frame", methods=['GET', 'POST'])
def store_frame():
    data = request.json
    if data is None or 'video_URL' not in data:
        return "Error: URL not provided in request", 400
    
    url = data['video_URL']
    user = data['username']
    project_name = data['proj_name']

    clip = VideoFileClip(url)
    dur = clip.duration
    first_frame = clip.get_frame(0)

    current_datetime = datetime.now()
    times = current_datetime.strftime("%H:%M:%S %Y-%m-%d")

    byte_stream = BytesIO()
    imageio.imwrite(byte_stream, first_frame, format='PNG')

    byte_string = byte_stream.getvalue()

    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO past_projects (username, project_name, img_frame, created, duration) VALUES (%s, %s, %s, %s, %s)",
                    (user, project_name, byte_string, times, dur))
        conn.commit()
        cursor.close()
    except Exception as e:
        return jsonify({'error': 'An error occurred while storing the image'}), 500

    return jsonify({'status': 200})

@app.route("/delete_stored", methods=['POST']) 
def delStored():
    cursor = conn.cursor()
    data = request.json
    if data is None or 'username' not in data:
        return "Error: Username not provided in request", 400
    
    username = data['username']
    query = "DELETE FROM proj_imgs WHERE proj_user = %s"
    query2 = "DELETE FROM audio_files WHERE aud_user = %s"
    cursor.execute(query, (username,))
    cursor.execute(query2, (username,))
    conn.commit()

    cursor.close()
    return "status : 200"

def format_duration2(seconds):
    minutes, seconds = divmod(seconds, 60)
    return '{:02d}:{:02d}'.format(minutes, seconds)

@app.route("/dashboard")
@jwt_required(optional=True)
def dashboard():
    access_token = request.args.get('access_token')
    if access_token:
        try:
            current_user = decode_token(access_token)['sub']
        except Exception as e:
            print(e)  # Handle token decoding errors
            return redirect(url_for('login'))
    else:
        if 'username' in session:
            current_user = session['username']
        else: 
            return redirect(url_for('login'))
    
    cursor = conn.cursor()
    query = "SELECT * FROM past_projects WHERE username = %s"
    cursor.execute(query, (current_user, ))

    results = cursor.fetchall()
    video_details = []
    for i in results :
        blob_data = bytes(i[2])  # Convert memoryview to bytes
        base64_blob = base64.b64encode(blob_data).decode('utf-8')
        
        duration_seconds = float(i[3])
        duration_formatted = format_duration2(int(duration_seconds))
        video_details.append({
            'username' : i[1],
            'frame_blob': base64_blob,
            'project_name': i[5],
            'created': i[4],
            'duration': duration_formatted 
        })
    cursor.close()
    return render_template("/dashboard/d-index.html", user_name=current_user, acc_token=access_token, video_details=video_details)


@app.route('/upload_profile_image', methods=['POST'])
def upload_profile_image():
    username = request.form.get('username')  # Get the username
    file = request.files['image_file']
    if file:
        cursor = conn.cursor()
        data = file.read()
        cursor.execute("UPDATE users SET profile_image = %s WHERE name = %s", (data, username))
        conn.commit()
        flash('Profile image updated successfully.')
        cursor.close()
    else:
        flash('No file selected.')
    return redirect(url_for('dashboard'))

@app.route('/retrieve_profiles/<username>')
def user_profile_image(username):
    cursor = conn.cursor()
    query = "SELECT name, email, profile_image FROM users WHERE name = %s"
    cursor.execute(query, (username, ))

    result = cursor.fetchone()
    cursor.close()
    if result and result[2]:
        user_name = result[0]
        email = result[1]
        blob_data = bytes(result[2])
        base64_blob = base64.b64encode(blob_data).decode('utf-8')

        return jsonify({"image_blob" : base64_blob, 'name' : user_name, 'email' : email})
    else:
        user_name = result[0]
        email = result[1]
        with open('static/dashboard/profile.png', 'rb') as f:
            default_image_data = f.read()
        base64_default_image = base64.b64encode(default_image_data).decode('utf-8')

        # Return the default profile image data as a base64-encoded string in JSON format
        return jsonify({"image_blob": base64_default_image,  'name' : user_name, 'email' : email})
    
@app.route('/remove_profile_image', methods=['POST'])
def remove_profile_image():
    username = request.form['username']
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET profile_image = NULL WHERE name = %s", (username,))
    conn.commit()
    cursor.close()
    return redirect(url_for('user_profile_image', username=username))

def authenticate(username, password):
    cursor = conn.cursor()
    query = "SELECT * FROM users"
    cursor.execute(query)

    results = cursor.fetchall()
    cursor.close()
    for i in results :
        if i[1] == username and bcrypt.check_password_hash(i[3], password) :
            user = dict()
            user['id'] = i[0]
            user['name'] = i[1]
            user['email'] = i[2]
            user['password'] = i[3]
            user['role'] = i[4]

            return user
    return None

def identity(payload):
    user_id = payload['id']
    return users.get(user_id, None)

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('l-name')
        password = request.form.get('l-password')
    
        user = authenticate(username, password)
        if user:
            # Create JWT token
            access_token = create_access_token(identity=username)
            # Store JWT token in session
            session['jwt_token'] = access_token
            session['username'] = username
            session['role'] = user['role']
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE name = %s", (username,))
            conn.commit()
            cursor.close()
            return jsonify({'message': username, 'access_token': access_token, 'user_role': user['role']}), 200
        else:
            return jsonify({'message': 'Invalid credentials'}), 401
    elif request.method == 'GET':
        if 'username' in session:
            user = session['username']
            access_token = session['jwt_token']
            return render_template("/homepage/home.html", user_name = user, access_token = access_token)
        else : 
            return render_template('/login/login.html')

@app.route("/logout")
def logout():
    session.pop('jwt_token', None)
    session.pop('username', None)
    session.pop('role', None)
    return redirect(url_for('homepage'))

@app.route("/isLoggedIn", methods=['POST'])
def checkLoginStatus():
    if 'username' in session:
        user = session['username']
        return jsonify({'message': 'yes', 'username': user})
    else : 
        return jsonify({'message': 'no'})

@app.route("/upload", methods=['POST', 'GET'])
def upload():
    if request.method == 'GET' :
        access_token = request.args.get('access_token')
        if access_token:
            try:
                current_user = decode_token(access_token)['sub']
                return render_template('/upload_page/uploadPage.html', access_token=access_token, user_name = current_user)
            except Exception as e:
                print(e)  # Handle token decoding errors
                return redirect(url_for('login'))
        else:
            if 'username' in session:
                user = session['username']
                return render_template('/upload_page/uploadPage.html', user_name = user, access_token = access_token)
            else : 
                return redirect(url_for('login'))
            
    elif request.method == 'POST':
        user = request.form['username']
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400

        files = request.files.getlist('file')
        for file in files:
            # Ensure file has a name
            if file.filename == '':
                return jsonify({'error': 'No selected file'}), 400

            # Read image file
            image_blob = file.read()
            filename = file.filename
            filetype = file.content_type
            filesize = len(image_blob)

            # Validate content type and size
            allowed_types = ['image/jpeg', 'image/png']
            max_file_size = 10 * 1024 * 1024  # 10 MB

            if filetype not in allowed_types:
                return jsonify({'error': 'Unsupported file type'}), 400

            if filesize > max_file_size:
                return jsonify({'error': 'File size exceeds the limit'}), 400

            # Store image data in MySQL database
            try:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO proj_imgs (proj_user, img_name, img_size, img_type, img_data) VALUES (%s, %s, %s, %s, %s)",
                            (user, filename, filesize, filetype, image_blob))
                conn.commit()
                cursor.close()
            except Exception as e:
                return jsonify({'error': 'An error occurred while storing the image'}), 500

        return jsonify({'message': 'Upload successful'}), 200

@app.route("/retrieve_images/<user>")
def retriever(user):
    query = "SELECT img_name, img_data FROM proj_imgs WHERE proj_user = %s"
    cursor = conn.cursor()
    cursor.execute(query, (user,))
    images = cursor.fetchall()
    cursor.close()
    images_base64 = [{"imagename": image[0], "data": base64.b64encode(image[1]).decode('utf-8')} for image in images]
    return jsonify(images_base64)

@app.route("/retrieve_audio/<user_name>")
def retriever_audio(user_name):
    query = "SELECT filename, audio_data FROM audio_files WHERE aud_user = 'all' or aud_user = %s"
    cursor = conn.cursor()
    cursor.execute(query, (user_name, ))
    audios = cursor.fetchall()
    cursor.close()
    audio_data = [{"filename": audio[0], "data": base64.b64encode(audio[1]).decode('utf-8')} for audio in audios]
    return jsonify(audio_data)

@app.route("/signup", methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form.get('s-name')
        email = request.form.get('s-email')
        password = request.form.get('s-password')

        query = "SELECT name, email FROM users WHERE (name = %s) or (email = %s)"
        cursor = conn.cursor()
        cursor.execute(query, (name, email))

        al_users = cursor.fetchall()
        if al_users :
            return jsonify({'status': 'already exists'})
        else :
            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
            cursor.execute("INSERT INTO users (name, email, password, role) VALUES (%s, %s, %s, %s)", (name, email, hashed_password, "user"))
            
            conn.commit()
            cursor.close()
        return jsonify({'status': 'success'})
    elif request.method == 'GET':
        return render_template("/login/signup.html")

@app.route("/forgot-pass")
def forgot_pass():
    return render_template("/login/forgotpass/forgot.html")

@app.route('/change_video_quality/<username>', methods=['POST', 'GET'])
def change_video_quality(username):
    data = request.get_json()

    video_url = data.get('video_url')
    quality = data.get('quality')
    dimensions = data.get('dimensions')

    modified_url = modify_video_quality(username, video_url, quality, dimensions)

    return jsonify({'modified_url': modified_url})

def modify_video_quality(user_name, video_path, quality, dimensions):
    try:
        clip = VideoFileClip(video_path)

        final = clip.fx(vfx.resize, width=dimensions['width'], height=dimensions['height'])
        bitrate = 22347

        now = datetime.now()
        current_time = now.strftime("%Y-%m-%d_%H-%M-%S")

        url_video = os.path.join(local_disk_path, f'proj_{current_time}.mp4')
        final.write_videofile(url_video, codec='libx264', audio_codec='aac', fps=24, bitrate=f"{bitrate}k")
        
        video_url = url_for('videos', filename=f'proj_{current_time}.mp4')
        return video_url
    except Exception as e:
        print(f"Error modifying video quality: {e}")
        return None
    
@app.route('/change_fps/<username>', methods=['POST', 'GET'])
def change_fps(username):
    data = request.get_json()

    # Extract the video URL, desired quality, and dimensions from the request data
    video_url = data.get('video_url')
    new_fps = data.get('new_fps')

    # Perform video quality modification using MoviePy
    modified_url = modify_fps(username, video_url, new_fps)
    return jsonify({'modified_url': modified_url})

def modify_fps(user_name, video_path, new_fps):
    try:
        clip = VideoFileClip(video_path)

        bitrate = 22347
        now = datetime.now()
        current_time = now.strftime("%Y-%m-%d_%H-%M-%S")

        url_video = os.path.join(local_disk_path, f'proj_{current_time}.mp4')
        clip.write_videofile(url_video, codec='libx264', audio_codec='aac', fps=new_fps, bitrate=f"{bitrate}k")

        video_url = url_for('videos', filename=f'proj_{current_time}.mp4')
        return video_url
    except Exception as e:
        print(f"Error modifying fps: {e}")
        return None

@app.route("/create-video")
def videopage():
    access_token = request.args.get('access_token')
    if access_token:
        try:
            current_user = decode_token(access_token)['sub']
            return render_template("/videopage/block.html", user_name = current_user, access_token = access_token)
        except Exception as e:
            print(e)  # Handle token decoding errors
            return redirect(url_for('login'))
    else:
        if 'username' in session:
            user = session['username']
            return render_template("/videopage/block.html", user_name = user, access_token = access_token)
        else : 
            return redirect(url_for('login'))

from moviepy.editor import *
import tempfile

from moviepy.editor import concatenate_videoclips
from moviepy.video.fx import all as vfx
from moviepy import *

from moviepy.decorators import requires_duration
import os

__all__ = ["slide_in", "slide_out"]

def slide_in(clip, duration, side):
    """Makes the clip arrive from one side of the screen.

    Only works when the clip is included in a CompositeVideoClip,
    and if the clip has the same size as the whole composition.

    Parameters
    ----------

    clip : moviepy.Clip.Clip
      A video clip.

    duration : float
      Time taken for the clip to be fully visible

    side : str
      Side of the screen where the clip comes from. One of
      'top', 'bottom', 'left' or 'right'.

    
    clips = [... make a list of clips]
    slided_clips = [
        CompositeVideoClip([clip.fx(transfx.slide_in, 1, "left")])
        for clip in clips
    ]
    final_clip = concatenate_videoclips(slided_clips, padding=-1)
    
    clip = ColorClip(
        color=(255, 0, 0), duration=1, size=(300, 300)
    ).with_fps(60)
    final_clip = CompositeVideoClip([transfx.slide_in(clip, 1, "right")])
    """
    w, h = clip.size
    pos_dict = {
        "left": lambda t: (min(0, w * (t / duration - 1)), "center"),
        "right": lambda t: (max(0, w * (1 - t / duration)), "center"),
        "top": lambda t: ("center", min(0, h * (t / duration - 1))),
        "bottom": lambda t: ("center", max(0, h * (1 - t / duration))),
    }

    return clip.with_position(pos_dict[side])


@requires_duration
def slide_out(clip, duration, side):
    """Makes the clip go away by one side of the screen.

    Only works when the clip is included in a CompositeVideoClip,
    and if the clip has the same size as the whole composition.

    Parameters
    ----------

    clip : moviepy.Clip.Clip
      A video clip.

    duration : float
      Time taken for the clip to fully disappear.

    side : str
      Side of the screen where the clip goes. One of
      'top', 'bottom', 'left' or 'right'.

    Examples
    --------

     clips = [... make a list of clips]
     slided_clips = [
         CompositeVideoClip([clip.fx(transfx.slide_out, 1, "left")])
         for clip in clips
    ]
    final_clip = concatenate_videoclips(slided_clips, padding=-1)
    
    clip = ColorClip(
         color=(255, 0, 0), duration=1, size=(300, 300)
     ).with_fps(60)
    final_clip = CompositeVideoClip([transfx.slide_out(clip, 1, "right")])
    """
    w, h = clip.size
    ts = clip.duration - duration  # start time of the effect.
    pos_dict = {
        "left": lambda t: (min(0, w * (-(t - ts) / duration)), "center"),
        "right": lambda t: (max(0, w * ((t - ts) / duration)), "center"),
        "top": lambda t: ("center", min(0, h * (-(t - ts) / duration))),
        "bottom": lambda t: ("center", max(0, h * ((t - ts) / duration))),
    }

    return clip.with_position(pos_dict[side])

# local_disk_path = os.getenv('RENDER_LOCAL_STORAGE', '/tmp')
local_disk_path = "./static/user_videos"
@app.route("/create_movie/<username>", methods=['POST'])
def create_movie(username):
    data = request.json

    base64_datas = data['image_datas']
    durations = data['image_durations']
    durations = [d / 150 for d in durations]

    img_trans_in = data['image_trans_in']
    img_trans_out = data['image_trans_out']

    for ind, d in enumerate(base64_datas):
        if d == -1:
            durations[ind] = -1
            img_trans_in[ind] = -1
            img_trans_out[ind] = -1
    base64_datas = [i for i in base64_datas if i != -1]
    durations = [i for i in durations if i != -1]
    img_trans_in = [i for i in img_trans_in if i != -1]
    img_trans_out = [i for i in img_trans_out if i != -1]

    if not base64_datas:
        return jsonify({'message': 'no images provided'})

    base64_audios = data['audio_datas']
    if base64_audios:
        aud_durations = data['audio_durations']
        aud_durations = [d / 150 for d in aud_durations] 

        for ind, d in enumerate(base64_audios):
            if d == -1:
                aud_durations[ind] = -1
        base64_audios = [i for i in base64_audios if i != -1]
        aud_durations = [i for i in aud_durations if i != -1]
    clips = []
    temp_dir = tempfile.mkdtemp()

    total_duration = sum(durations)  # Calculate the total duration of the video

    for idx, base64_data in enumerate(base64_datas):
        image_path = os.path.join(temp_dir, f'image_{idx}.png')
        with open(image_path, 'wb') as f:
            f.write(base64.b64decode(base64_data))
        clip = ImageClip(image_path).set_duration(durations[idx])

        if img_trans_in[idx] != 0:
            transition_in_clip = None
            if img_trans_in[idx] == 1:
                transition_in_clip = clip.fx(vfx.fadein, duration=0.25)
            elif img_trans_in[idx] == 2:
                transition_in_clip = CompositeVideoClip([clip.fx(transfx.slide_in, 0.5, "left")])
            elif img_trans_in[idx] == 3:
                for i in range(1, 101):
                    transition_clip = clip.set_duration(0.005)
                    transition_clip = transition_clip.resize((max(i * 0.01, 0.01)))
                    clips.append(transition_clip)
            elif img_trans_in[idx] == 4:
                width, _ = clip.size
                width_half = width / 2
                part = width_half / 100
                for i in range(0, 101):
                    transition_clip = clip.set_duration(0.005)
                    transition_clip = transition_clip.crop(x1=width_half - (max(i * part, 0.01)), x2=width_half + (max(i * part, 0.01)))
                    clips.append(transition_clip)

            if transition_in_clip:
                transition_in_clip = transition_in_clip.set_duration(0.5)
                clips.append(transition_in_clip)
        else:
            transition_in_clip = clip.set_duration(0.5)
            clips.append(transition_in_clip)
            
            clip_tmp = clip.set_duration(durations[idx] - 1)
        if  round(durations[idx] - 1, 2) != 0:
            clips.append(clip_tmp)

        if img_trans_out[idx] != 0:
            transition_out_clip = None
            if img_trans_out[idx] == 1:
                transition_out_clip = clip.fx(vfx.fadeout, duration=0.25)
            elif img_trans_out[idx] == 2:
                transition_out_clip = CompositeVideoClip([clip.fx(transfx.slide_out, 0.5, "right")])
            elif img_trans_out[idx] == 3:
                for i in range(1, 101):
                    transition_clip = clip.set_duration(0.005)
                    transition_clip = transition_clip.resize((max((100 - i) * 0.01, 0.01)))
                    clips.append(transition_clip)
            elif img_trans_out[idx] == 4:
                width, height = clip.size
                width_half = width / 2
                part = width_half / 100
                for i in range(0, 100):
                    transition_clip = clip.set_duration(0.005)
                    transition_clip = transition_clip.crop(x1=round((max(i * part, 0.01)), 2), x2=round(width - (max(i * part, 0.01)), 2))
                    clips.append(transition_clip)
                else:
                    transition_clip = clip.set_duration(0.005)
                    transition_clip = transition_clip.crop(x1=width_half, x2=width_half)
                    clips.append(transition_clip)

            if transition_out_clip:
                transition_out_clip = transition_out_clip.set_duration(0.5)
                clips.append(transition_out_clip)
        else :
            transition_out_clip = clip.set_duration(0.5)
            clips.append(transition_out_clip)

    video_clip = concatenate_videoclips(clips, method="compose")
    video_clip.set_duration(total_duration)

    if base64_audios:
        audio_lsts = []
        for idx, base64_audio in enumerate(base64_audios):
            audio_path = os.path.join(temp_dir, f'audio_{idx}.mp3')
            with open(audio_path, 'wb') as f:
                f.write(base64.b64decode(base64_audio))
            
            actual_duration = AudioFileClip(audio_path).duration
            count = int(aud_durations[idx] // actual_duration)

            remaining = aud_durations[idx] % actual_duration

            audio_clip = AudioFileClip(audio_path)
            audio_clip2 = AudioFileClip(audio_path).set_duration(remaining)

            for _ in range(count):
                audio_lsts.append(audio_clip)
            audio_lsts.append(audio_clip2)

        final_audio = concatenate_audioclips(audio_lsts)
        video_clip = video_clip.set_audio(final_audio)

    now = datetime.now()
    current_time = now.strftime("%Y-%m-%d_%H-%M-%S")

    filename = f'proj_{current_time}.mp4'
    output_filename = os.path.join(local_disk_path, filename)

    video_clip.write_videofile(output_filename, fps=24, codec='libx264', preset='ultrafast', bitrate='5000k')

    video_url = url_for('videos', filename=filename)
    return jsonify({'message': 'Movie created successfully', 'filename': video_url})

@app.route("/admin", methods = ['GET'])
def admin():
    access_token = request.args.get('access_token')
    if access_token:
        try:
            return render_template("/admin/admin.html")
        except Exception as e:
            print(e) 
            return redirect(url_for('login'))
    else:
        if 'username' in session:
            return render_template("/admin/admin.html")
        else : 
            return redirect(url_for('login'))

@app.route("/get_viewers", methods=["GET"])
def get_viewers():
    cursor = conn.cursor()
    query = "SELECT id, name, email, last_login FROM users WHERE role = 'user'"
    cursor.execute(query)
    viewers = cursor.fetchall()
    
    viewers_list = []
    for viewer in viewers:
        viewer_dict = {
            'id': viewer[0],
            'name': viewer[1],
            'email': viewer[2],
            'lastLogin': viewer[3]
        }
        viewers_list.append(viewer_dict)
    cursor.close()
    return jsonify(viewers_list)


@app.route("/delete_user/<user_name>", methods=["DELETE"])
def delete_user(user_name):
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM users WHERE name = %s", (user_name,))
    results = cursor.fetchone()
    if results:
        cursor.execute("DELETE FROM users WHERE name = %s", (user_name,))
        delete_user_folder(user_name)
        conn.commit()
        cursor.close()
        return jsonify({'message': 'User deleted successfully'})
    else:
        cursor.close()
        return jsonify({'error': 'User not found'}), 404

from flask import send_from_directory

@app.route('/videos/<path:filename>')
def videos(filename):
    return send_from_directory(local_disk_path, filename)

@app.route("/update_user_name/<user_name>", methods=['PUT'])
def update_user_name(user_name):
    new_name = request.json.get('name')
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM users WHERE name = %s", (user_name,))
    results = cursor.fetchone()

    if results:
        query = "UPDATE users SET name = %s WHERE name = %s"
        cursor.execute(query, (new_name, user_name))
        conn.commit()
        cursor.close()
        change_folder_name(user_name, new_name)
        return jsonify({'message': 'User name updated successfully'})
    else:
        cursor.close()
        return jsonify({'error': 'User not found'}), 404


@app.route('/upload_audio/<u_name>', methods=['POST'])
def upload_audio(u_name):
    if 'audio_file' in request.files:
        audio_file = request.files['audio_file']
        
        # Convert audio file to blob
        audio_blob = audio_file.read()
        
        # Insert audio blob into database
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO audio_files (filename, audio_data, aud_user) VALUES (%s, %s, %s)",
                            (audio_file.filename, audio_blob, u_name))
            conn.commit()
            cursor.close()
            return 'Audio file uploaded successfully.', 200
        except Exception as e:
            print("Error:", e)
            cursor.close()
            return 'Error uploading audio file.', 500
    else:
        return 'No audio file provided.', 400


from itsdangerous import URLSafeTimedSerializer

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        user = authenticate_user_by_email(email)
        if user:
            serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
            token = serializer.dumps(user['email'], salt='reset-password')
            send_reset_email(email)
            
            flash('An email with your OTP has been sent.', 'success')
        else:
            flash('There is no account with that email address.', 'danger')
        return redirect(url_for('forgot_password'))
    return render_template('/login/forgotpass/forgot.html')


from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from itsdangerous import URLSafeTimedSerializer

def authenticate_user_by_email(email):
    query = "SELECT * FROM users WHERE email = %s"
    cursor = conn.cursor()
    cursor.execute(query, (email,))
    user = cursor.fetchone()
    if user:
        return {
            'id': user[0],
            'name': user[1],
            'email': user[2],
            'password': user[3],
            'role': user[4]
        }
    cursor.close()
    return None

from flask import request, jsonify

@app.route('/check_email', methods=['POST'])
def check_email():
    email = request.json.get('email')
    if not email:
        return jsonify({'error': 'Email is required'}), 400

    query = "SELECT * FROM users WHERE email = %s"
    cursor = conn.cursor()
    cursor.execute(query, (email,))
    user = cursor.fetchone()
    cursor.close()
    if user:
        return jsonify({'exists': True})
    else:
        return jsonify({'exists': False})
    
from flask import flash
from itsdangerous import URLSafeTimedSerializer


@app.route('/send_reset_email', methods=['POST'])
def send_reset_email():
    email = request.json.get('email')
    if not email:
        return jsonify({'error': 'Email is required'}), 400

    user = authenticate_user_by_email(email)
    if user:
        # Generate a reset token
        serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
        token = serializer.dumps(user['email'], salt='reset-password')

        otp = random.randint(100000, 999999)  # Generate 6-digit OTP
        send_reset_email_helper(user['email'],otp)

        return jsonify({'success': True})
    else:
        return jsonify({'error': 'User with this email does not exist'}), 404

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

otp_final = 0
email_used = ""

def send_reset_email_helper(email, otp):
    message = Mail(
        from_email='mr.swamsingla@gmail.com',  
        to_emails=email,
        subject='Password Reset OTP',
        html_content=f'Your OTP for password reset is: {otp}.'
    )
    global otp_final
    global email_used
    email_used = email
    try:
        sg = SendGridAPIClient("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")
        response = sg.send(message)
        print(f"Email sent, status code: {response.status_code}")
        otp_final = otp
        return render_template("/login/forgotpass/forgot.html", correct_otp=otp, email=email)

    except Exception as e:
        print(f"Error sending reset email using SendGrid: {e}")


@app.route('/verify_otp', methods=['POST'])
def verify_otp():
    user_otp = request.form['otp']

    if int(user_otp) == int(otp_final):
        # Proceed with password reset
        return redirect('/reset_password/' + email_used)
    else:
        # Incorrect OTP, show an error message
        flash('Incorrect OTP entered!')
        return render_template('/login/forgotpass/forgot.html')


@app.route('/reset_password/<email>', methods=['GET', 'POST'])
def reset_password(email):
    if request.method == 'POST':
        new_password = request.form.get('new_password')
        # Update the user's password in the database
        try:
            update_password(email, new_password)
            flash('Your password has been reset successfully.', 'success')
            return redirect(url_for('login'))  # Assuming you have a route named 'login'
        except Exception as e:
            flash('Error resetting password. Please try again.', 'danger')
            print(e)  # For debugging
    return render_template('/login/forgotpass/reset_password.html', email=email)

def update_password(user_id, new_password):
    cursor = conn.cursor()
    hashed_password = bcrypt.generate_password_hash(new_password).decode('utf-8')
    query = "UPDATE users SET password = %s WHERE email = %s"
    cursor.execute(query, (hashed_password, user_id))
    conn.commit()
    cursor.close()

if __name__ == '__main__':
    app.run(debug=True)
