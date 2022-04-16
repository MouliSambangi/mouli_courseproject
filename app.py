from flask import Flask, make_response, request
from itertools import chain, combinations
import os
import argparse
import io
import csv

app = Flask(__name__)

output_result = {
    "error": None,
    "result": "",
    "file": None,
    "total": None
}



@app.route('/')
def form():
    return """
       <html>
        <head>
            
        </head>
       
        <body>
            <div id="login">
            <div>
                <div>
                <div>
                    <div>
                    <form method="post" enctype="multipart/form-data" action="/apriori" id="login-form" >
                        <p> Data Mining Apriori Algorithm in Heroku Engine</p>
                        Input file: <input type="file" name="data_file" />
                        Minimum Support Value: <input value="20" name="mim_sup" placeholder="Minimum Support"  type="number" />
                        <input type="submit" />
                        <p> Mouli Sambangi, CSU ID: 2834899</p>
                    </form>
                    </div>
                </div>
                </div>
            </div>
            </div>
        </body>
        </html>
    """

    
def add_to_sets(items):
    add_to_set = set()
    for item in items:
        add_to_set.add(item)
    return add_to_set


def convert_to_array_int(items):
    arr = []
    for item in items:
        arr.append(int((item)))
    return arr


def candidate_item(frequent_item, iterator):
    data = []
    for i in frequent_item:
        for j in frequent_item:
            if len(i.union(j)) == iterator:
                data.append(i.union(j))
    return set(data)


def subset(candidate, iterator):
    return set([frozenset(list(z)) for z in
                list(chain.from_iterable(combinations(candidate, j) for j in range(iterator - 1, iterator)))])


def has_infrequent_subset(candidate, data_set, minimum_support):
    re_formatted_candidate = set()
    list_of_items = list(candidate)
    for item in range(len(list_of_items)):
        i = 0
        for data in data_set:
            if list_of_items[item].issubset(data):
                i += 1
        if i >= minimum_support:
            re_formatted_candidate.add(list_of_items[item])
    return re_formatted_candidate


def apriori_gen(read_lines, minimum_support):
    re_formatted_data = []
    item_sets = set()
    iterator = 2
    for row in read_lines:
        split_by_comma = str(row.strip()).split(", ")
        line_number = split_by_comma.pop(0)
        item_sets = item_sets.union(split_by_comma)
        data = set(convert_to_array_int(split_by_comma))
        data.add(line_number + 'key')
        # converting tuple to frozenset
        re_formatted_data.append(frozenset(data))

    re_formatted_item_set = set(frozenset([int(single_set)]) for single_set in item_sets)
    frequent_item = has_infrequent_subset(re_formatted_item_set, re_formatted_data, minimum_support)
    frequent_item_sets = add_to_sets(frequent_item)

    while True:
        candidate_items = candidate_item(frequent_item, iterator)
        temp_candidate_items = set()
        for candidate in candidate_items:
            subsets = subset(candidate, iterator)
            count = 0
            for item in subsets:
                if item in frequent_item:
                    count += 1
            if count == len(subsets):
                temp_candidate_items.add(candidate)

        candidate_items = temp_candidate_items
        frequent_item = has_infrequent_subset(candidate_items, re_formatted_data, minimum_support)

        if len(frequent_item) != 0:
            for candidate in frequent_item:
                subsets = subset(candidate, iterator)
                frequent_item_sets.add(candidate)
                frequent_item_sets = frequent_item_sets - subsets

            iterator += 1
        else:
            break
    output_result["total"] = len(frequent_item_sets)
    return [set(z) for z in frequent_item_sets]


def main(select_file_list, minimum_support):
    try:
        filename = str(select_file_list)
        file_read = open(filename, "r")
        read_lines = file_read.readlines()
        file_read.close()
        output_result["result"] = apriori_gen(read_lines, int(minimum_support))
    except:
        output_result["error"] = "Invalid File: Some thing is wrong with file upload "

    return output_result

@app.route('/apriori', methods=["POST"])
def transform_view():
    try:
        f = request.files['data_file']
        name = f.filename
        minimum_support = request.form.get('mim_sup')
        if not f:
            return "No file"
        stream = io.StringIO(f.stream.read().decode("UTF8"), newline=None)
        csv_input = csv.reader(stream)
        l = []
        for i,v in enumerate(csv_input):
            t = ""
            for x in v:
                t = t+x+","
            l.append(t[:-1])
        output_result["result"] = apriori_gen(l, int(minimum_support))
        print(output_result['result'])
        print("End - total items:", output_result['total'])
        return str("Data File Name: "+name +"             Minimum support: "+minimum_support+"            "+str(output_result['result'])+ "               "+ "End Total items: "+str(len(output_result['result'])) )
    except Exception as e:
        return " *Must provide Minimum support value,  "+ str(e)