import csv
import difflib


def update_indicies(rows, used_indicies, vfields, oldest_names, min_score,
                    header, version_num, matched_indicies):
    v_index = header.index('^' + version_num)
    for i in range(len(vfields)):
        if i in matched_indicies:
            continue
        best_match = {'score': 0, 'name': '', 'index': -1}
        test_field = vfields[i]
        if test_field == '':
            continue
        for j in range(len(oldest_names)):
            if j in used_indicies:
                continue
            oldest_name = oldest_names[j]
            seq = difflib.SequenceMatcher(
                a=test_field,
                b=oldest_name,
            )
            ratio = seq.ratio()
            last_index = rows[j][v_index - 2]
            last_index_int = int(last_index) if last_index.isdigit() else -100
            index_diff = abs((i + 1) - last_index_int)
            score = ratio - (index_diff / 50)
            if score > best_match['score']:
                best_match = {
                    'score': score,
                    'name': oldest_name,
                    'index': j,
                }
        if best_match['score'] > min_score:
            used_indicies.append(best_match['index'])
            matched_indicies.append(i)
            print(test_field + ' - ' + best_match['name'] + ' - ' +
                  str(best_match['index']) + ' -> ' +
                  str(i + 1) + ':' +
                  rows[best_match['index']][v_index - 2] + ' - ' +
                  str(best_match['score']))
            rows[best_match['index']][v_index] = str(i + 1)
            rows[best_match['index']][v_index + 1] = test_field.strip()
        else:
            if min_score == 0.4:
                print('<<<<< no match for {n}>>>>>'.format(n=test_field))


def edit_file(name, version_fields, first_time=False):
    print('---------{n}---------'.format(n=name))
    version_num = version_fields[0][1:]
    vfields = version_fields[2:]
    filename = name + '.csv'
    with open(filename) as form_file:
        header = []
        rows = []
        is_header = True
        oldest_names = []
        for line in form_file:
            if is_header:
                reader = csv.reader([line])
                header = next(reader)
                if first_time:
                    header.append('^' + version_num)
                    header.append('')
                is_header = False
            else:
                reader = csv.reader([line])
                fields = next(reader)
                fields_copy = list(fields)
                if first_time:
                    fields_copy += ['', '']
                rows.append(fields_copy)
                oldest_name = ''
                for field in fields:
                    if field != '':
                        oldest_name = field
                oldest_names.append(oldest_name)
    used_indicies = []
    matched_indicies = []
    for val in [0.9, 0.8, 0.7, 0.6, 0.5, 0.4]:
        update_indicies(rows, used_indicies, vfields, oldest_names, val,
                        header, version_num, matched_indicies)
    with open(filename, 'w', newline='') as newfile:
        csvwriter = csv.writer(newfile)
        csvwriter.writerow(header)
        for row in rows:
            csvwriter.writerow(row)


def addHeaders(version, first_time=False):
    filename = version + 'headers.csv'
    with open(filename) as header_file:
        for line in header_file:
            if ',' in line:
                reader = csv.reader([line])
                fields = next(reader)
                if fields[1].startswith('F'):
                    if fields[1][1] != '8':
                        edit_file(fields[1], fields, first_time)
                elif fields[1][1] == 'H':
                    edit_file(fields[1][1:], fields, first_time)
                elif fields[1][1] != 'I':
                    edit_file('Sch' + fields[1][1:], fields, first_time)


if __name__ == '__main__':
    addHeaders('v2', True)
    addHeaders('v1', True)
