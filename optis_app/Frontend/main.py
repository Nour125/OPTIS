"""
The main app. This handles both the backend and the frontend side.
render_template just renders the html from the "template" folder.
redirect_url redirects towards a certain url, but does NOT render a template if the pointed url also does not.

"""
from flask import Flask, render_template, url_for, request, redirect, flash, send_file, send_from_directory
from datetime import datetime
from werkzeug.utils import secure_filename
import os, time, sys
"""
The following are the import for the backend. Just write the name of the script without .py.
Then you can immediately use the function from the script directly in the app.
"""
sys.path.append(os.path.join(os.path.dirname(sys.path[0]),'backend'))
import dqn, petrinet
import eventlog as elog 

#define the app
app = Flask(__name__)

#the super secret key that allows browser based flashes :
app.secret_key = '54321'

#specifies where the upload directory is and the file type available for uploads
UPLOAD_FOLDER = r'upload'
ALLOWED_EXTENSIONS = {'.csv','.xes'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

#specifies the static folder used for images and stuff
STATIC_FOLDER = r'static'
app.config['STATIC_FOLDER'] = STATIC_FOLDER

#specifices where the temporary folder for downloaded file would be:
DOWNLOAD_FOLDER = r'export'
app.config['DOWNLOAD_FOLDER'] = DOWNLOAD_FOLDER

#global variable in which the allowed file types are saved
FILE_TYPES = ['csv','xes']

#route to the index page
@app.route('/')
def index():
    return render_template('index.html')

#redirect to the next page when the button on the index page is pressed
@app.route('/', methods=['POST'])
def go_to_start():
    return redirect(url_for('start'))

#home page route. The type inputs are just for the list selection.
@app.route('/start')
def start():
    file_types = ['csv','xes']
    current_time = datetime.now().strftime('%Y-%m-%dT%H:%M')
    return render_template('start.html', file_types = file_types, current_time = current_time)

"""
The following is the upload functionality. It uploads directly into the "upload" directory.
Then it redirects towards the case ID input page.
"""
@app.route('/start', methods=['GET','POST'])
def upload_file():
    uploaded_file = request.files['file']
    if uploaded_file.filename != '':
        #file is saved in the 'upload' directory.
        uploaded_file.save(os.path.join(app.config['UPLOAD_FOLDER'],uploaded_file.filename))
        if not elog.format_check(uploaded_file.filename):
            #if the event log is not of the right format flashes a warning
            flash('Event log does not match the expected business process!')
            return redirect(url_for('start'))
    elif uploaded_file.filename == '':
        #if no file has been selected, flashes a warning
        flash('No files selected! Please select a file!')
        return redirect(url_for('start'))

    return redirect(url_for('preview', filename = uploaded_file.filename))
    
"""
The download function. Generates an event log based on the user specification -
Start and End Date and Time, as well as format (csv or xes), and downloads it.
"""
@app.route('/download/<current_time>', methods=['GET'])
def download(current_time):
    file_types = FILE_TYPES
    filetype = time = ''
    filetype = request.args.get("selectType")

    
    # retrieving the start and end times from the request
    start_date_time = request.args.get("startTime")
    end_date_time = request.args.get("endTime")

    #warnings if empty
    if not start_date_time:
        flash('Invalid simulation period! Start Date and Time cannot be empty!')
    elif not end_date_time:
        flash('Invalid simulation period! End Date and Time cannot be empty!')
    else: 
        start_time = datetime.strptime(start_date_time, '%Y-%m-%dT%H:%M')
        end_time = datetime.strptime(end_date_time, '%Y-%m-%dT%H:%M')

        # Calculate the duration in minutes
        time = (end_time - start_time).total_seconds() / 60
        
        if time < 0:
            flash('Invalid simulation period! End Date and Time cannot be later than Start Date and Time!')
            return render_template('start.html', file_types = file_types, current_time = current_time)
        elif time == 0:
            flash('Invalid simulation period! End Date and Time cannot be the same as Start Date and Time!')
            return render_template('start.html', file_types = file_types, current_time = current_time)
        elif time > 0:
            elog.generate_event_log(start_time, time)
            flash('', '')

            if filetype == 'csv':
                path = os.path.join(app.config['DOWNLOAD_FOLDER'], 'elog.csv')
                #flash the confirmation that file is succesfully downloaded
                # flash('Generated a event log in csv. Please check your attachments!')
                return send_file(path, as_attachment=True)
            elif filetype == 'xes':
                path = os.path.join(app.config['DOWNLOAD_FOLDER'], 'elog.xes')
                #flash the confirmation that file is succesfully downloaded
                # flash('Generated a event log in xes. Please check your attachments!')
                return send_file(path, as_attachment=True)
            else:
                path = os.path.join(app.config['DOWNLOAD_FOLDER'], 'fish.png')
                #flash the confirmation that file is succesfully downloaded
                # flash('Else')
                return send_file(path, as_attachment=True)
            
    return render_template('start.html', file_types = file_types, current_time = current_time)
    
        
"""
The preview page. Gets the first 15 rows of the uploaded file and passes them to the template in html format.
"""
@app.route('/preview.html/<filename>', methods=['GET'])
def preview(filename):
    df = elog.convert_to_dataframe(filename)
    preview_df = df.head(15)
    row_count = preview_df.shape[0]
    preview_data=preview_df.to_html()
    return render_template('preview.html', preview_data=preview_data, filename=filename, row_count=row_count)

"""
Redirects from the preview page to the case selection page.
"""
@app.route('/preview.html/<filename>', methods=['POST'])
def go_to_selection(filename):
    return redirect(url_for('case_id', filename=filename))

"""
Route for displaying possible case IDs. It is a dropdown menu that displays the list from the python script in the dropdown menu.
There is a preview functionality, when clicked will show a preview of a generated image. It is linked to the 'preview' button in the case id page.
"""
@app.route('/case.html/<filename>', methods=['GET'])
def case_id(filename):
    selection = elog.get_active_cases(filename) 
    previewid = request.args.get("selectpreview")
    state = None

    if previewid != None:
        for file in os.listdir('static/'):
            if file.startswith('preview_net'):  # not to remove other images
                os.remove('static/' + file)

        previewid = int(previewid)

        state = elog.get_case_information(previewid, filename)
        state = state.to_html()
        petrinet.decorate_petri_net(previewid, filename)
   
    return render_template('case.html', selection=selection, filename=filename, previewid=previewid, state = state)
    
"""
Route for sending the case id towards recommendation. This is linked to the 'Optimize now' button in the case ID page.
I have decided to use a separate dropdown list to avoid cross sending the http requests by accident.
"""
@app.route('/case.html/<filename>', methods=['POST'])
def send_caseid(filename):
    result = request.form.get("selectresult")
    return redirect(url_for('recommendation', result=result, filename=filename))

"""
The result page. 
"""
@app.route('/result.html/<filename>/<result>', methods=['GET'])
def recommendation(result, filename):
    result = int(result)
    state = elog.get_state(result, filename)
    rec = dqn.deploy(state)
    rec = int(rec)

    for file in os.listdir('static/'):
            if file.startswith('net'):  # not to remove other images
                os.remove('static/' + file)
    
    name = petrinet.decorate_petri_net_with_rec(result, rec, filename)

    return render_template('result.html', name = name)

"""
Loading page. Has yet to be used.
"""
#loading page route
@app.route('/loading.html')
def loading():
    return render_template('loading.html')

#about us page route
@app.route('/aboutus.html')
def aboutus():
    return render_template('aboutus.html')

#info us page route
@app.route('/info.html')
def info():
    return render_template('info.html')

#the main app
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)


