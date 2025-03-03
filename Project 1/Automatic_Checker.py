import pyodbc
import csv
import glob
import zipfile
import re
import importlib
import zipimport
import pandas as pd
import os

def db_connect(server_name, database, user, pwd):
    cnxn = pyodbc.connect('DRIVER={SQL Server};'
                          'SERVER=' + server_name + ';'
                          'DATABASE=' + database + ';'
                          'UID=' + user + ';'
                          'PWD=' + pwd + '')

    # Create a cursor from the connection
    cursor = cnxn.cursor()
    return cnxn, cursor


def create_tables(cursor, TABLES):
    for table_name in TABLES[::-1]:
        drop_sql = "DROP TABLE IF EXISTS " + table_name
        cursor.execute(drop_sql)
        cursor.commit()
    create_tables_file = open(CREATE_TABLES_FILE_NAME, 'r')
    create_tables_commands = create_tables_file.read()
    create_tables_file.close()
    sqlCommands = create_tables_commands.split(';')
    for command in sqlCommands[:-1]:
        try:
            cursor.execute(command)
            cursor.commit()
        except:
            print("Command skipped: ", command)


def test_data_insertion(cursor, table_list, test_num):
    for table_name in table_list:
        file_path = 'data/' + table_name + '_test' + str(test_num) + '.csv'
        insert_data_to_tables(cursor, file_path, table_name)
    return


def insert_data_to_tables(cursor, file_path, table_name):
    with open(file_path, 'r', encoding="utf8") as f:
        reader = csv.reader(f)
        columns = next(reader)
        data_to_upload = []
        for data in reader:
            data_to_upload.append('(' + ','.join([f"'{item}'" for item in data]) + ')')
            if len(data_to_upload) >= 1000:
                query = f"insert into {table_name}({','.join(columns)}) values "
                query += ','.join(data_to_upload)
                cursor.execute(query)
                cursor.commit()
                data_to_upload = []
        query = f"insert into {table_name}({','.join(columns)}) values "
        query += ','.join(data_to_upload)
        cursor.execute(query)
        cursor.commit()


def delete_views(cursor):
    cursor.execute("SELECT * FROM sys.views;")
    views_list = []
    for row in cursor.fetchall():
        if "database_firewall" not in row[0]:
            views_list.append(row[0])
    for view in views_list:
        command = "DROP VIEW " + view
        cursor.execute(command)
    cursor.commit()
    return


def run_views(cursor, view_commands, q_number, IDS):
    for view_ind, view_query in enumerate(view_commands):
        if view_ind > 6:
            print("Illegal solution. You cannot use more than 4 views!")
            return
        try:
            cursor.execute(view_query)
        except Exception as e:
            print(f"{IDS}: Error occurred when executing view number {view_ind} of q_{q_number}")
            print(e)
            return "ERROR"
    return


def get_query_result_from_file(file_path, q_number, query_result_type, test_number):
    with open(f'{file_path}GT_Q{q_number}_test{test_number}.csv', 'r') as f:
        reader = csv.reader(f)
        columns = next(reader)
        correct_result = [tuple([str(elem) for elem in row]) for row in reader]
        if query_result_type == 'set':
            correct_result = set(correct_result)
        return correct_result


def get_query_result_from_code(cursor, IDS, q_number, query_result_type, zip_submission_folder_path=None, zipFolder=None):
    if zip_submission_folder_path is not None:
        zip_importer = zipimport.zipimporter(zip_submission_folder_path)
        if WITH_VIEWS:
            views_dict = zip_importer.load_module(IDS + '_Views').VIEWS_DICT
            view_commands = views_dict[f"Q{q_number}"]
            run_views(cursor, view_commands, q_number, IDS)
        query_answers = zip_importer.load_module(IDS + '_Queries').QUERY_ANSWERS
    else:
        if WITH_VIEWS:
            views_file = importlib.import_module(IDS + "_Views")
            views_dict = views_file.VIEWS_DICT
            view_commands = views_dict[f"Q{q_number}"]
            run_views(cursor, view_commands, q_number, IDS)
        queries_file = importlib.import_module(IDS + "_Queries")
        query_answers = queries_file.QUERY_ANSWERS
    query = query_answers[f"Q{q_number}"]
    try:
        cursor.execute(query)
        query_result = [tuple([str(elem) for elem in data]) for data in cursor.fetchall()]
        if query_result_type == 'set':
            query_result = set(query_result)
        return query_result
    except Exception as e:
        # print(f"Error occurred in q_{q_number}, students {IDS}, folder path: {zip_submission_folder_path}")
        # print(f"Please check your submission format again")
        # print(e)
        return "Unable to produce query result. Please check your submission format again"


def check_queries(cursor, student_IDS, correct_result_by_q, zip_submission_folder_path,
                  zipFolder, test_num, test_reports_dict, POINTS_FOR_TEST=dict()):
    txt_file_content = []
    test_corr_by_q = {q_number: 0 for q_number in correct_result_by_q.keys()}
    for q_number in QUERY_NUMBERS:
        students_query_result = get_query_result_from_code(cursor, student_IDS, q_number,
                                                           QUERY_RESULT_TYPES[q_number],
                                                           zip_submission_folder_path,
                                                           zipFolder)
        if MODE == 'student':
            print(50 * "*")
            if correct_result_by_q[q_number] == students_query_result:
                print(f"query {q_number}, test {test_num}: Good")
            else:
                print(f"query {q_number}, test {test_num}: Error")
                print(f"Correct Answer: {correct_result_by_q[q_number]}\n")
                print(f"Your Answer: {students_query_result}\n")
                print()
        else:
            if correct_result_by_q[q_number] == students_query_result:
                test_corr_by_q[q_number] = 1 * POINTS_FOR_TEST[q_number]
                test_reports_dict[student_IDS].append(f"query {q_number}, test {test_num}: Good\n")
                test_reports_dict[student_IDS].append(f"\n")
            else:
                test_corr_by_q[q_number] = 0
                test_reports_dict[student_IDS].append(f"query {q_number}, test {test_num}: Error\n")
                test_reports_dict[student_IDS].append(f"Correct Answer: {correct_result_by_q[q_number]}\n")
                test_reports_dict[student_IDS].append(f"Your Answer: {students_query_result}\n")
                test_reports_dict[student_IDS].append(f"\n")
    return test_corr_by_q, txt_file_content, test_reports_dict


def add_test_corr_to_students_grades(students, students_grades_dict, test_corr_by_q):
    updated_students_grades_dict = students_grades_dict.copy()

    if students not in updated_students_grades_dict:
        updated_students_grades_dict[students] = dict()

    for q_number, corr_by_q in test_corr_by_q.items():
        if q_number not in updated_students_grades_dict[students]:
            updated_students_grades_dict[students][q_number] = []
        updated_students_grades_dict[students][q_number].append(corr_by_q)
    return updated_students_grades_dict


def write_results_to_csv_with_final_grade(students_grades_dict):
    csv_rows = []
    header_row = ['id'] + ['q' + str(q_number) + '_t' + str(test_num)
                           for q_number in QUERY_NUMBERS
                           for test_num in range(1, NUMBER_OF_TESTS + 1)]
    csv_rows.append(header_row)
    for students, results_by_q in students_grades_dict.items():
        student_ids = [student_id for student_id in students.split('_') if len(student_id) == 9]
        all_results = []
        for q_number in QUERY_NUMBERS:
            all_results.extend(results_by_q[q_number])
        total_grade = sum(all_results)
        for student_id in student_ids:
            row = [student_id, ] + all_results
            row.append(total_grade)
            csv_rows.append(row)
    with open('students_tests_grades.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(csv_rows)


def create_GT_CSV(correct_result, QUERIES_RESULT_COLUMNS, q_number, test_num):
    if len(correct_result):
        df = pd.DataFrame(list(correct_result))
        df.columns = QUERIES_RESULT_COLUMNS[q_number]
    else:
        df = pd.DataFrame(columns=QUERIES_RESULT_COLUMNS[q_number])
    df.to_csv('GT_q' + str(q_number) + '_test' + str(test_num) + '.csv', index=False)
    return


def initialize_test_reports_dict(students_folders):
    test_reports_dict = dict()
    if not os.path.exists("test_reports"):
        os.makedirs("test_reports")
    for idx, students_folder in enumerate(students_folders):
        zip_submission_folder = glob.glob(students_folder + "/*.zip")
        if zip_submission_folder != []:
            try:
                students = zip_submission_folder[0].split('\\')[-1].replace(".zip", "")
                test_reports_dict[students] = []
            except:
                continue
    return test_reports_dict


def write_test_reports(test_reports_dict, students_grades_dict):
    for ids, content in test_reports_dict.items():
        try:
            grade = sum([sum(Q_scores) for Q_scores in students_grades_dict[ids].values()])
        except:
            grade = 0
        txt_file_name = f"{ids}({grade}).txt"
        with open(os.path.join('test_reports', txt_file_name), "w") as output_file:
            for txt in content:
                output_file.write(txt)
    return



if __name__ == "__main__":
    MODE = "student"  # Can be defined as student or grader
    RES_FROM_FILE = False
    WITH_VIEWS = True
    IDS = "ID1_ID2"  # For student mode

    SERVER_NAME = "techniondbcourse01.database.windows.net"
    DATABASE_NAME = "user"
    USER_NAME = "user"
    PASSWORD = "Qwerty12!"
    CREATE_TABLES_FILE_NAME = "data/create_table_commands.sql"
    TABLES_COLS = {'Company': ['Symbol', 'Sector', 'Location', 'Founded'],
                   'Stock': ['Symbol', 'tDate', 'Price'],
                   'Buying': ['ID', 'tDate', 'Symbol', 'BQuantity']}
    TABLES = list(TABLES_COLS.keys())
    NUMBER_OF_TESTS = 1
    QUERY_NUMBERS = [3, 4]
    QUERY_RESULT_TYPES = {3: 'list', 4: 'set'}  # We use list for queries with ORDER BY, otherwise use set
    QUERIES_RESULT_COLUMNS = {3: ['ID', 'Actions', 'TotalSum', 'Sector'],
                              4: ['ID', 'Actions']}
    POINTS_FOR_TEST = {2: 4, 3: 4, 4: 4}
    if MODE == 'student':
        students_folders = glob.glob(IDS + ".zip")
    else:
        STUDENTS_FOLDER_NAME = "00094241.02-HW1-211986"
        students_folders = glob.glob(STUDENTS_FOLDER_NAME + "/*")
        students_grades_dict = dict()
    test_reports_dict = initialize_test_reports_dict(students_folders)
    for test_num in range(1, NUMBER_OF_TESTS + 1):
        cnxn, cursor = db_connect(SERVER_NAME, DATABASE_NAME, USER_NAME, PASSWORD)
        # print(f"Test number {test_num}")
        create_tables(cursor, TABLES)
        test_data_insertion(cursor, TABLES, test_num)
        correct_result_by_q = dict()
        delete_views(cursor)
        for q_number in QUERY_NUMBERS:
            res_type = QUERY_RESULT_TYPES[q_number]
            if MODE == 'student' or RES_FROM_FILE:
                correct_result = get_query_result_from_file("data/", q_number, res_type, test_num)
            else:
                correct_result = get_query_result_from_code(cursor, 'GT', q_number, res_type)
                create_GT_CSV(correct_result, QUERIES_RESULT_COLUMNS, q_number, test_num)
            correct_result_by_q[q_number] = correct_result
            delete_views(cursor)
        for idx, students_folder in enumerate(students_folders):
            if MODE == 'student':
                zip_submission_folder = glob.glob(students_folder)
            else:
                zip_submission_folder = glob.glob(students_folder + "/*.zip")
            if zip_submission_folder != []:
                try:
                    zipFolder = zipfile.ZipFile(zip_submission_folder[0], 'r')
                    students = zip_submission_folder[0].split('\\')[-1].replace(".zip", "")
                    test_corr_by_q, txt_file_content, test_reports_dict = check_queries(cursor, students,
                                                                                        correct_result_by_q,
                                                                                        zip_submission_folder[0],
                                                                                        zipFolder, test_num,
                                                                                        test_reports_dict,
                                                                                        POINTS_FOR_TEST)
                    if MODE == 'grader':
                        students_grades_dict = add_test_corr_to_students_grades(students, students_grades_dict,
                                                                                test_corr_by_q).copy()

                except Exception as e:
                    print(f"General error occurred in folder: {students_folder}")
                    print(e)
                # if idx % 20 == 0:
                #     print(f"{idx} student pairs were checked")
                try:
                    delete_views(cursor)
                except Exception as e:
                    print(f"Could not delete views in folder: {students_folder}")
                    print(e)


        for table_name in TABLES:
            delete_records_query = "DELETE FROM " + table_name + " WHERE 1=1"
            cursor.execute(delete_records_query)
            cursor.commit()

        # print(f"Test number {test_num} finished")
    if MODE == 'grader':
        write_test_reports(test_reports_dict, students_grades_dict)
        write_results_to_csv_with_final_grade(students_grades_dict)