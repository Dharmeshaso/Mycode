__author__ = 'dharmesh'
import os
from flask import Flask
from flask import render_template
from flask import request
from urllib2 import urlopen

app = Flask(__name__)

tempfilepath='tmp/tmpmpinfo.csv'

@app.route('/')
def home():
    """
    function is called at start of app
    :return:template name and info of MP's
    """
    response = urlopen("https://data.gov.in/node/85984/datastore/export/csv")
    csv = response.read()
    csvstr = str(csv).strip("b'")
    lines = csvstr.split("\\n")
    try:
        os.remove(tempfilepath)  # removing temp file if present
    except OSError, e:
        print e
    with open(tempfilepath, 'wb') as csvf:
        for line in lines:
            csvf.write(line)
    mp_info = read_csv(tempfilepath)
    return render_template('index.html', mp_info=mp_info, records=len(mp_info))


@app.route('/search_filter', methods=["POST"])
def filter_info():
    """
    function is called when filtered info needed
    :return:template name and info of filtered MP's
    """
    filter_type = request.form['filter_on']
    filter_val = request.form['filter']
    mp_info = read_csv(tempfilepath, {filter_type: filter_val})
    return render_template('index.html', mp_info=mp_info, records=len(mp_info))


def read_csv(filepath, filter={}):
    """
    function to read a csv and convert info to a list of dict
    :param filepath is path of temp csv file:
    :param filter is set of filter attributes:
    :return: list of dict
    """
    with open(filepath, 'rb') as file_obj:
        lines = file_obj
        header_removed = False
        mp_info = []
        s_no = 0
        for line in lines:
            attr_list = line.replace("\"", "").split(",")
            if not header_removed or len(attr_list) != 9:
                header_removed = True
                continue

            keys = ["s_no", "div", "name", "lok_sabha", "session", "state", "const", "total_seat", "attnd_days"]
            if filter and filter.keys()[0] in keys:
                index = keys.index(filter.keys()[0])
                if str(filter.values()[0]) not in str(attr_list[index]):
                    continue
            s_no += 1
            mp_info.append({"s_no": s_no,
                            "div": attr_list[1],
                            "name": attr_list[2],
                            "lok_sabha": attr_list[3],
                            "session": attr_list[4],
                            "state": attr_list[5],
                            "const": attr_list[6],
                            "total_seat": attr_list[7],
                            "attnd_days": attr_list[8]})

    return mp_info


if __name__ == "__main__":
    app.run(debug=True)